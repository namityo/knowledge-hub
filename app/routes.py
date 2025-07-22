import os
import uuid
from flask import render_template, request, redirect, url_for, flash, abort, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
from .models import db, Knowledge, Comment, Like, CommentLike, Attachment, Tag, ViewHistory
from .utils import get_current_user_id, handle_file_uploads, handle_tags, audit_logger, get_bulk_engagement_stats
from .config import SYSTEM_TITLE, MAX_FILE_SIZE_MB, POPULAR_ARTICLES_COUNT, allowed_file

def register_routes(app):
    """ルートをFlaskアプリに登録"""
    
    @app.route('/')
    def index():
        search_query = request.args.get('search', '').strip()
        my_posts = request.args.get('my_posts', '').strip()
        liked_posts = request.args.get('liked_posts', '').strip()
        tag_filter = request.args.get('tag', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = 10  # 1ページあたりの件数
        current_user_id = get_current_user_id()
        
        # クエリの基本条件を設定（下書きを除外）
        query = Knowledge.query.filter(Knowledge.is_draft == False)
        
        # 自分の投稿フィルター
        if my_posts == '1':
            query = query.filter(Knowledge.author == current_user_id)
        
        # いいねした投稿フィルター（記事またはコメントのいいね）
        if liked_posts == '1':
            query = query.filter(
                db.or_(
                    # 記事自体にいいね
                    Knowledge.likes.any(Like.user_id == current_user_id),
                    # その記事のコメントにいいね
                    Knowledge.comments.any(Comment.comment_likes.any(CommentLike.user_id == current_user_id))
                )
            )
        
        # タグフィルター
        if tag_filter:
            query = query.filter(Knowledge.tags.any(Tag.name == tag_filter))
        
        # 検索フィルター
        if search_query:
            # タイトル、内容、またはコメントで検索
            query = query.filter(
                db.or_(
                    Knowledge.title.contains(search_query),
                    Knowledge.content.contains(search_query),
                    Knowledge.comments.any(Comment.content.contains(search_query))
                )
            )
        
        pagination = query.order_by(Knowledge.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        knowledge_list = pagination.items
        
        # 一括でエンゲージメント統計を取得（N+1問題回避）
        engagement_stats = get_bulk_engagement_stats(knowledge_list)
        
        # タグ一覧を取得（公開記事で使用されているタグのみ、使用回数順）
        all_tags = Tag.query.join(
            Tag.knowledge_items
        ).filter(
            Knowledge.is_draft == False,
            Tag.usage_count > 0
        ).distinct().order_by(Tag.usage_count.desc()).all()
        
        return render_template('index.html', 
                             knowledge_list=knowledge_list, 
                             engagement_stats=engagement_stats,
                             current_user_id=current_user_id, 
                             search_query=search_query,
                             my_posts=my_posts,
                             liked_posts=liked_posts,
                             tag_filter=tag_filter,
                             all_tags=all_tags,
                             pagination=pagination,
                             system_title=SYSTEM_TITLE)

    @app.route('/create', methods=['GET', 'POST'])
    def create():
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            tags_string = request.form.get('tags', '').strip()
            # 下書きかどうかを判定（"save_draft"ボタンがクリックされた場合）
            is_draft = 'save_draft' in request.form
            # HTTPヘッダーからユーザーIDを取得してauthorに設定
            author = get_current_user_id()
            
            new_knowledge = Knowledge(title=title, content=content, author=author, is_draft=is_draft)
            db.session.add(new_knowledge)
            db.session.flush()  # IDを取得するためにflush
            
            # タグ処理
            handle_tags(new_knowledge, tags_string, author)
            
            # ファイルアップロード処理
            handle_file_uploads(new_knowledge.id, author, app.config)
            
            db.session.commit()
            
            if is_draft:
                flash('下書きとして保存されました！', 'success')
                return redirect(url_for('drafts'))
            else:
                flash('ナレッジが投稿されました！', 'success')
                return redirect(url_for('index'))
        
        # GETリクエスト時は現在のユーザーIDをテンプレートに渡す
        current_user_id = get_current_user_id()
        
        return render_template('form_editor.html', mode='create', current_user_id=current_user_id, 
                             system_title=SYSTEM_TITLE, max_file_size_mb=MAX_FILE_SIZE_MB)

    @app.route('/view/<int:id>')
    def view(id):
        knowledge = Knowledge.query.get_or_404(id)
        comments = Comment.query.filter_by(knowledge_id=id).order_by(Comment.created_at.desc()).all()
        attachments = Attachment.query.filter_by(knowledge_id=id).order_by(Attachment.created_at.asc()).all()
        current_user_id = get_current_user_id()
        
        # 閲覧履歴を記録（作成者以外の場合のみ）
        if knowledge.author != current_user_id:
            # 今日の日付を取得
            today = datetime.now(timezone.utc).date()
            
            # 同じユーザーが同じ記事を今日既に閲覧しているかチェック
            existing_view_today = ViewHistory.query.filter(
                ViewHistory.user_id == current_user_id,
                ViewHistory.knowledge_id == id,
                db.func.date(ViewHistory.viewed_at) == today
            ).first()
            
            # 今日初回の閲覧の場合のみ記録
            if not existing_view_today:
                # 閲覧履歴を記録
                view_history = ViewHistory(
                    user_id=current_user_id,
                    knowledge_id=id
                )
                db.session.add(view_history)
                db.session.commit()
                audit_logger.info(f"View history recorded - Knowledge ID:{id}, User:{current_user_id}")
            else:
                audit_logger.debug(f"Duplicate view today prevented - Knowledge ID:{id}, User:{current_user_id}")
        
        # 現在のユーザーがこのナレッジにいいねしているかチェック
        user_liked = Like.query.filter_by(user_id=current_user_id, knowledge_id=id).first() is not None
        
        # 各コメントに対するユーザーのいいね状態をチェック
        comment_likes = {}
        for comment in comments:
            comment_likes[comment.id] = CommentLike.query.filter_by(user_id=current_user_id, comment_id=comment.id).first() is not None
        
        return render_template('view.html', knowledge=knowledge, comments=comments, attachments=attachments,
                             current_user_id=current_user_id, user_liked=user_liked, 
                             comment_likes=comment_likes, system_title=SYSTEM_TITLE)

    @app.route('/edit/<int:id>', methods=['GET', 'POST'])
    def edit(id):
        knowledge = Knowledge.query.get_or_404(id)
        current_user_id = get_current_user_id()
        
        # 投稿者と現在のユーザーIDが一致しない場合は403エラー
        if knowledge.author != current_user_id:
            audit_logger.warning(f"Unauthorized edit attempt - User:{current_user_id}, Knowledge ID:{id}, Owner:{knowledge.author}")
            abort(403)
        
        if request.method == 'POST':
            knowledge.title = request.form['title']
            knowledge.content = request.form['content']
            tags_string = request.form.get('tags', '').strip()
            # HTTPヘッダーからユーザーIDを取得してauthorに設定
            knowledge.author = current_user_id
            knowledge.updated_at = datetime.now(timezone.utc)
            
            # 下書き状態の処理
            if 'save_draft' in request.form:
                # 下書きとして保存
                knowledge.is_draft = True
                message = '下書きとして保存されました！'
                redirect_target = url_for('drafts')
            else:
                # 公開として保存（下書きから公開する場合も含む）
                was_draft = knowledge.is_draft
                knowledge.is_draft = False
                message = '公開されました！' if was_draft else 'ナレッジが更新されました！'
                redirect_target = url_for('view', id=knowledge.id)
            
            # タグ処理
            handle_tags(knowledge, tags_string, current_user_id)
            
            # ファイルアップロード処理
            handle_file_uploads(knowledge.id, current_user_id, app.config)
            
            db.session.commit()
            
            flash(message, 'success')
            return redirect(redirect_target)
        
        # 既存の添付ファイルを取得
        attachments = Attachment.query.filter_by(knowledge_id=id).order_by(Attachment.created_at.asc()).all()
        
        return render_template('form_editor.html', mode='edit', knowledge=knowledge, attachments=attachments, 
                             current_user_id=current_user_id, system_title=SYSTEM_TITLE, max_file_size_mb=MAX_FILE_SIZE_MB)

    @app.route('/delete/<int:id>')
    def delete(id):
        knowledge = Knowledge.query.get_or_404(id)
        current_user_id = get_current_user_id()
        
        # 投稿者と現在のユーザーIDが一致しない場合は403エラー
        if knowledge.author != current_user_id:
            audit_logger.warning(f"Unauthorized delete attempt - User:{current_user_id}, Knowledge ID:{id}, Owner:{knowledge.author}")
            abort(403)
        
        # タグ関連付けをクリア（使用回数も自動更新される）
        handle_tags(knowledge, '', current_user_id)
        
        # 関連する添付ファイルを事前に取得してファイルシステムから削除
        attachments = knowledge.attachments
        for attachment in attachments:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment.stored_filename)
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    audit_logger.info(f"Deleted attachment file: {attachment.stored_filename}")
            except OSError as e:
                audit_logger.error(f"Failed to delete attachment file {file_path}: {e}")
        
        # 記事を削除（cascade='all, delete-orphan'によりAttachmentレコードも自動削除）
        db.session.delete(knowledge)
        db.session.commit()
        
        flash('ナレッジが削除されました！', 'success')
        return redirect(url_for('index'))

    @app.route('/comment/<int:knowledge_id>', methods=['POST'])
    def add_comment(knowledge_id):
        knowledge = Knowledge.query.get_or_404(knowledge_id)
        content = request.form['content']
        author = get_current_user_id()
        
        new_comment = Comment(content=content, author=author, knowledge_id=knowledge_id)
        db.session.add(new_comment)
        db.session.commit()
        
        flash('コメントが投稿されました！', 'success')
        return redirect(url_for('view', id=knowledge_id))

    @app.route('/comment/delete/<int:comment_id>')
    def delete_comment(comment_id):
        comment = Comment.query.get_or_404(comment_id)
        current_user_id = get_current_user_id()
        
        # コメント投稿者と現在のユーザーIDが一致しない場合は403エラー
        if comment.author != current_user_id:
            audit_logger.warning(f"Unauthorized comment delete attempt - User:{current_user_id}, Comment ID:{comment_id}, Owner:{comment.author}")
            abort(403)
        
        knowledge_id = comment.knowledge_id
        db.session.delete(comment)
        db.session.commit()
        flash('コメントが削除されました！', 'success')
        return redirect(url_for('view', id=knowledge_id))

    @app.route('/like/<int:knowledge_id>', methods=['POST'])
    def toggle_like(knowledge_id):
        knowledge = Knowledge.query.get_or_404(knowledge_id)
        current_user_id = get_current_user_id()
        
        # 自分の記事にはいいねできない
        if knowledge.author == current_user_id:
            audit_logger.warning(f"Self-like attempt - User:{current_user_id}, Knowledge ID:{knowledge_id}")
            flash('自分の記事にはいいねできません。', 'warning')
            return redirect(url_for('view', id=knowledge_id))
        
        # 既存のいいねをチェック
        existing_like = Like.query.filter_by(user_id=current_user_id, knowledge_id=knowledge_id).first()
        
        if existing_like:
            # いいねを取り消し
            db.session.delete(existing_like)
            db.session.commit()
            flash('いいねを取り消しました！', 'info')
        else:
            # いいねを追加
            new_like = Like(user_id=current_user_id, knowledge_id=knowledge_id)
            db.session.add(new_like)
            db.session.commit()
            flash('いいねしました！', 'success')
        
        return redirect(url_for('view', id=knowledge_id))

    @app.route('/comment/like/<int:comment_id>', methods=['POST'])
    def toggle_comment_like(comment_id):
        comment = Comment.query.get_or_404(comment_id)
        current_user_id = get_current_user_id()
        
        # 自分のコメントにはいいねできない
        if comment.author == current_user_id:
            audit_logger.warning(f"Self-comment-like attempt - User:{current_user_id}, Comment ID:{comment_id}")
            flash('自分のコメントにはいいねできません。', 'warning')
            return redirect(url_for('view', id=comment.knowledge_id))
        
        # 既存のいいねをチェック
        existing_like = CommentLike.query.filter_by(user_id=current_user_id, comment_id=comment_id).first()
        
        if existing_like:
            # いいねを取り消し
            db.session.delete(existing_like)
            db.session.commit()
            flash('コメントのいいねを取り消しました！', 'info')
        else:
            # いいねを追加
            new_like = CommentLike(user_id=current_user_id, comment_id=comment_id)
            db.session.add(new_like)
            db.session.commit()
            flash('コメントにいいねしました！', 'success')
        
        return redirect(url_for('view', id=comment.knowledge_id))

    @app.route('/download/<int:attachment_id>')
    def download_file(attachment_id):
        attachment = Attachment.query.get_or_404(attachment_id)
        try:
            return send_from_directory(
                app.config['UPLOAD_FOLDER'],
                attachment.stored_filename,
                as_attachment=True,
                download_name=attachment.filename
            )
        except FileNotFoundError:
            flash('ファイルが見つかりません。', 'error')
            return redirect(url_for('view', id=attachment.knowledge_id))

    @app.route('/delete_attachment/<int:attachment_id>')
    def delete_attachment(attachment_id):
        attachment = Attachment.query.get_or_404(attachment_id)
        current_user_id = get_current_user_id()
        knowledge = attachment.knowledge
        
        # 記事の作成者またはファイルのアップロード者のみ削除可能
        if knowledge.author != current_user_id and attachment.uploaded_by != current_user_id:
            audit_logger.warning(f"Unauthorized attachment delete attempt - User:{current_user_id}, Attachment ID:{attachment_id}")
            abort(403)
        
        # ファイルシステムからファイルを削除
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment.stored_filename)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except OSError as e:
            audit_logger.error(f"Failed to delete file {file_path}: {e}")
        
        # データベースから削除
        db.session.delete(attachment)
        db.session.commit()
        flash('添付ファイルが削除されました！', 'success')
        return redirect(url_for('view', id=knowledge.id))

    @app.route('/drafts')
    def drafts():
        page = request.args.get('page', 1, type=int)
        per_page = 10  # 1ページあたりの件数
        current_user_id = get_current_user_id()
        
        # 現在のユーザーの下書きのみを取得
        query = Knowledge.query.filter(
            Knowledge.is_draft == True,
            Knowledge.author == current_user_id
        )
        
        pagination = query.order_by(Knowledge.updated_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        draft_list = pagination.items
        
        return render_template('drafts.html', 
                             draft_list=draft_list,
                             current_user_id=current_user_id,
                             pagination=pagination,
                             system_title=SYSTEM_TITLE)

    @app.route('/popular')
    def popular():
        """人気記事ページ - 直近一ヶ月のアクティビティでトップ3を表示"""
        current_user_id = get_current_user_id()
        
        # 全記事を取得（下書きを除外）
        all_knowledge = Knowledge.query.filter(Knowledge.is_draft == False).all()
        
        # 記事がない場合は空のリストを返す
        if not all_knowledge:
            return render_template('popular.html',
                                 top_by_views=[],
                                 top_by_likes=[],
                                 top_by_comments=[],
                                 current_user_id=current_user_id,
                                 system_title=SYSTEM_TITLE)
        
        # 直近30日の統計を一括取得（効率的）
        recent_stats = get_bulk_engagement_stats(all_knowledge, days=30)
        
        # 各記事に統計情報を付与
        articles_with_stats = []
        for knowledge in all_knowledge:
            stats = recent_stats[knowledge.id]
            articles_with_stats.append({
                'knowledge': knowledge,
                'recent_views': stats['views'],
                'recent_likes': stats['likes'],
                'recent_comments': stats['comments']
            })
        
        # 各カテゴリでソートしてトップN件を取得
        top_by_views_with_counts = sorted(articles_with_stats, key=lambda x: x['recent_views'], reverse=True)[:POPULAR_ARTICLES_COUNT]
        top_by_likes_with_counts = sorted(articles_with_stats, key=lambda x: x['recent_likes'], reverse=True)[:POPULAR_ARTICLES_COUNT]
        top_by_comments_with_counts = sorted(articles_with_stats, key=lambda x: x['recent_comments'], reverse=True)[:POPULAR_ARTICLES_COUNT]
        
        return render_template('popular.html',
                             top_by_views=top_by_views_with_counts,
                             top_by_likes=top_by_likes_with_counts,
                             top_by_comments=top_by_comments_with_counts,
                             current_user_id=current_user_id,
                             system_title=SYSTEM_TITLE)

    @app.route('/image/<int:attachment_id>')
    def serve_image(attachment_id):
        """画像ファイルの表示用エンドポイント"""
        attachment = Attachment.query.get_or_404(attachment_id)
        
        # 画像ファイルかどうかチェック
        if not attachment.mime_type.startswith('image/'):
            abort(404)
        
        try:
            return send_from_directory(
                app.config['UPLOAD_FOLDER'],
                attachment.stored_filename,
                mimetype=attachment.mime_type
            )
        except FileNotFoundError:
            abort(404)

    @app.route('/upload_image', methods=['POST'])
    def upload_image():
        """画像アップロード専用エンドポイント（ドラッグ&ドロップ用）"""
        try:
            if 'image' not in request.files:
                return jsonify({'success': False, 'message': 'ファイルがありません'}), 400
            
            file = request.files['image']
            if file.filename == '':
                return jsonify({'success': False, 'message': 'ファイルが選択されていません'}), 400
            
            # 画像ファイルかどうかチェック
            if not file.content_type.startswith('image/'):
                return jsonify({'success': False, 'message': '画像ファイルのみアップロード可能です'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'success': False, 'message': 'サポートされていない画像形式です'}), 400
            
            # 安全なファイル名を生成
            original_filename = secure_filename(file.filename)
            file_extension = original_filename.rsplit('.', 1)[1].lower()
            stored_filename = f"{uuid.uuid4().hex}.{file_extension}"
            
            # ファイルを保存
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)
            file.save(file_path)
            
            # ファイルサイズとMIMEタイプを取得
            file_size = os.path.getsize(file_path)
            mime_type = file.content_type
            
            # 一時的な添付ファイル情報をDBに保存（knowledge_idは後で設定）
            attachment = Attachment(
                filename=original_filename,
                stored_filename=stored_filename,
                file_size=file_size,
                mime_type=mime_type,
                knowledge_id=None,  # 一時的にNone
                uploaded_by=get_current_user_id()
            )
            db.session.add(attachment)
            db.session.commit()
            
            # Markdownで使用する画像リンクを生成
            image_url = url_for('serve_image', attachment_id=attachment.id)
            markdown_text = f"![{original_filename}]({image_url})"
            
            return jsonify({
                'success': True,
                'attachment_id': attachment.id,
                'image_url': image_url,
                'markdown': markdown_text,
                'filename': original_filename
            })
            
        except Exception as e:
            audit_logger.error(f"Image upload failed: {str(e)}")
            return jsonify({'success': False, 'message': 'アップロードに失敗しました'}), 500

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, '..', 'static'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )