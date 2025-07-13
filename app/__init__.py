from flask import Flask


def create_app():
    """アプリケーションファクトリー"""
    # 遅延インポート
    try:
        import markdown
        from markupsafe import Markup
    except ImportError as e:
        print(f"Warning: Missing dependencies - {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        raise
    
    from sqlalchemy import event
    from .config import Config, MAX_FILE_SIZE_MB
    from .models import db, Knowledge, Comment, Like, CommentLike
    from .utils import get_current_user_id, audit_logger
    from .routes import register_routes
    from .api import register_api_routes
    
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(Config)
    
    # JSON出力でUnicodeをエスケープしない設定
    app.config['JSON_AS_ASCII'] = False
    
    # データベースURIを動的に設定
    app.config['SQLALCHEMY_DATABASE_URI'] = Config.get_sqlalchemy_database_uri()
    
    # 設定の初期化
    Config.init_app(app)
    
    # データベースの初期化
    db.init_app(app)
    
    # ルートの登録
    register_routes(app)
    
    # APIルートの登録
    register_api_routes(app)
    
    # テンプレートフィルターの登録
    register_template_filters(app)
    
    # エラーハンドラーの登録
    register_error_handlers(app)
    
    # イベントリスナーの登録
    register_event_listeners()
    
    # コンテキストプロセッサーの登録
    register_context_processors(app)
    
    return app

def register_template_filters(app):
    """テンプレートフィルターを登録"""
    import markdown
    from markupsafe import Markup
    
    @app.template_filter('markdown')
    def markdown_filter(text):
        return Markup(markdown.markdown(text, extensions=['fenced_code', 'tables', 'codehilite', 'nl2br']))

    @app.template_filter('preview')
    def preview_filter(text, max_lines=5):
        if not text:
            return ''
        
        # 改行で分割して最初の5行を取得
        lines = text.split('\n')
        
        if len(lines) <= max_lines:
            # 5行以下の場合はそのまま改行を<br>に変換
            return Markup('<br>'.join(lines))
        else:
            # 5行を超える場合は省略記号を追加
            preview_lines = lines[:max_lines]
            return Markup('<br>'.join(preview_lines) + '<br>...')

    @app.template_filter('nl2br')
    def nl2br_filter(text):
        if not text:
            return ''
        return Markup(text.replace('\n', '<br>'))

    @app.template_filter('tags_to_string')
    def tags_to_string_filter(tags):
        """タグオブジェクトのリストをカンマ区切り文字列に変換"""
        if not tags:
            return ''
        return ', '.join([tag.name for tag in tags])

    @app.template_filter('jst')
    def jst_filter(dt):
        """UTC時刻を日本時間（JST）に変換"""
        if not dt:
            return ''
        from .config import JST
        from datetime import timezone
        
        # UTCタイムゾーンが設定されていない場合は設定
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        # 日本時間に変換
        jst_time = dt.astimezone(JST)
        return jst_time.strftime('%Y-%m-%d %H:%M')

def register_error_handlers(app):
    """エラーハンドラーを登録"""
    from .config import MAX_FILE_SIZE_MB
    
    @app.errorhandler(413)
    def file_too_large(error):
        from flask import flash, redirect, request, url_for
        flash(f'ファイルサイズが大きすぎます。最大{MAX_FILE_SIZE_MB}MBまでアップロード可能です。', 'error')
        return redirect(request.referrer or url_for('index'))

def register_event_listeners():
    """SQLAlchemyイベントリスナーを登録"""
    from sqlalchemy import event
    from .models import Knowledge, Comment, Like, CommentLike
    from .utils import get_current_user_id, audit_logger
    
    @event.listens_for(Knowledge, 'after_insert')
    def log_insert(mapper, connection, target):
        user_id = get_current_user_id()
        audit_logger.info(f"INSERT - User:{user_id}, Knowledge ID:{target.id}, Title:'{target.title}', Author:'{target.author}'")

    @event.listens_for(Knowledge, 'after_update')
    def log_update(mapper, connection, target):
        user_id = get_current_user_id()
        audit_logger.info(f"UPDATE - User:{user_id}, Knowledge ID:{target.id}, Title:'{target.title}', Author:'{target.author}'")

    @event.listens_for(Knowledge, 'after_delete')
    def log_delete(mapper, connection, target):
        user_id = get_current_user_id()
        audit_logger.info(f"DELETE - User:{user_id}, Knowledge ID:{target.id}, Title:'{target.title}', Author:'{target.author}'")

    @event.listens_for(Comment, 'after_insert')
    def log_comment_insert(mapper, connection, target):
        user_id = get_current_user_id()
        audit_logger.info(f"COMMENT INSERT - User:{user_id}, Comment ID:{target.id}, Knowledge ID:{target.knowledge_id}, Author:'{target.author}'")

    @event.listens_for(Comment, 'after_delete')
    def log_comment_delete(mapper, connection, target):
        user_id = get_current_user_id()
        audit_logger.info(f"COMMENT DELETE - User:{user_id}, Comment ID:{target.id}, Knowledge ID:{target.knowledge_id}, Author:'{target.author}'")

    @event.listens_for(Like, 'after_insert')
    def log_like_insert(mapper, connection, target):
        user_id = get_current_user_id()
        audit_logger.info(f"LIKE INSERT - User:{user_id}, Like ID:{target.id}, Knowledge ID:{target.knowledge_id}, User ID:'{target.user_id}'")

    @event.listens_for(Like, 'after_delete')
    def log_like_delete(mapper, connection, target):
        user_id = get_current_user_id()
        audit_logger.info(f"LIKE DELETE - User:{user_id}, Like ID:{target.id}, Knowledge ID:{target.knowledge_id}, User ID:'{target.user_id}'")

    @event.listens_for(CommentLike, 'after_insert')
    def log_comment_like_insert(mapper, connection, target):
        user_id = get_current_user_id()
        audit_logger.info(f"COMMENT LIKE INSERT - User:{user_id}, CommentLike ID:{target.id}, Comment ID:{target.comment_id}, User ID:'{target.user_id}'")

    @event.listens_for(CommentLike, 'after_delete')
    def log_comment_like_delete(mapper, connection, target):
        user_id = get_current_user_id()
        audit_logger.info(f"COMMENT LIKE DELETE - User:{user_id}, CommentLike ID:{target.id}, Comment ID:{target.comment_id}, User ID:'{target.user_id}'")

def register_context_processors(app):
    """コンテキストプロセッサーを登録"""
    from .models import Knowledge
    from .utils import get_current_user_id
    
    @app.context_processor
    def inject_draft_count():
        """全てのテンプレートで下書き件数を利用可能にする"""
        try:
            current_user_id = get_current_user_id()
            draft_count = Knowledge.query.filter(
                Knowledge.is_draft == True,
                Knowledge.author == current_user_id
            ).count()
            return dict(draft_count=draft_count)
        except:
            # リクエストコンテキスト外などでエラーが発生した場合は0を返す
            return dict(draft_count=0)