import os
import re
import logging

# ファイルアップロード設定
MAX_FILE_SIZE_MB = int(os.environ.get('MAX_FILE_SIZE_MB', '16'))

# 許可するファイル拡張子を環境変数から取得
ALLOWED_EXTENSIONS_ENV = os.environ.get('ALLOWED_FILE_EXTENSIONS')
if ALLOWED_EXTENSIONS_ENV:
    # 環境変数からカンマ区切りで取得し、小文字に変換してセットに格納
    ALLOWED_EXTENSIONS = {ext.strip().lower() for ext in ALLOWED_EXTENSIONS_ENV.split(',') if ext.strip()}
else:
    # デフォルトの許可拡張子
    ALLOWED_EXTENSIONS = {
        'txt', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
        'png', 'jpg', 'jpeg', 'gif', 'svg', 'webp',
        'zip', 'rar', '7z',
        'csv', 'json', 'xml', 'md'
    }

# ユーザーID検証用正規表現を環境変数から取得
USER_ID_PATTERN = os.environ.get('USER_ID_PATTERN', r'^[a-zA-Z0-9_-]{3,20}$')

# システムタイトルを環境変数から取得
SYSTEM_TITLE = os.environ.get('SYSTEM_TITLE', 'ナレッジベース')

# デフォルトユーザー名を環境変数から取得
DEFAULT_USER_ID = os.environ.get('DEFAULT_USER_ID', 'anonymous')

# ユーザーIDヘッダー名を環境変数から取得
USER_ID_HEADER_NAME = os.environ.get('USER_ID_HEADER_NAME', 'X-User-ID')

# データベース関連の環境変数を定数として取得
DATABASE_DIR = os.environ.get('DATABASE_DIR')
DATABASE_FILENAME = os.environ.get('DATABASE_FILENAME', 'knowledge.db')
DATABASE_URL = os.environ.get('DATABASE_URL')

# その他の環境変数を定数として取得
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-fallback-key-change-in-production')

# API認証設定
API_KEY = os.environ.get('API_KEY')
API_KEY_HEADER_NAME = os.environ.get('API_KEY_HEADER_NAME', 'X-API-Key')

# 人気記事表示件数設定
POPULAR_ARTICLES_COUNT = int(os.environ.get('POPULAR_ARTICLES_COUNT', '5'))

# タイムゾーン設定
import pytz
JST = pytz.timezone('Asia/Tokyo')

# カスタムアップロードディレクトリ（相対または絶対パス）
UPLOAD_DIR = os.environ.get('UPLOAD_DIR')

# ログ関連の環境変数を定数として取得
AUDIT_LOG_DIR = os.environ.get('AUDIT_LOG_DIR')
AUDIT_LOG_FILENAME = os.environ.get('AUDIT_LOG_FILENAME', 'audit.log')

def get_database_path():
    """データベースファイルのパスを構築"""
    if DATABASE_DIR:
        # 絶対パスまたは相対パスを指定
        if not os.path.isabs(DATABASE_DIR):
            # 相対パスの場合は、アプリケーションルートからの相対パス
            app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_dir = os.path.join(app_root, DATABASE_DIR)
        else:
            db_dir = DATABASE_DIR
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, DATABASE_FILENAME)
    else:
        # デフォルト: instanceディレクトリ
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        instance_dir = os.path.join(app_root, 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        return os.path.join(instance_dir, DATABASE_FILENAME)

def get_upload_path():
    """アップロードディレクトリのパスを構築"""
    if UPLOAD_DIR:
        # 絶対パスまたは相対パスを指定
        if not os.path.isabs(UPLOAD_DIR):
            # 相対パスの場合は、アプリケーションルートからの相対パス
            app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            upload_dir = os.path.join(app_root, UPLOAD_DIR)
        else:
            upload_dir = UPLOAD_DIR
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir
    else:
        # デフォルト: アプリケーションルート/uploads
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_dir = os.path.join(app_root, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        return upload_dir

def get_audit_log_path():
    """監査ログファイルのパスを構築"""
    if AUDIT_LOG_DIR:
        # 絶対パスまたは相対パスを指定
        if not os.path.isabs(AUDIT_LOG_DIR):
            # 相対パスの場合は、アプリケーションルートからの相対パス
            app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            log_dir = os.path.join(app_root, AUDIT_LOG_DIR)
        else:
            log_dir = AUDIT_LOG_DIR
        
        # ディレクトリが存在しない場合は作成
        os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, AUDIT_LOG_FILENAME)
    else:
        # デフォルト: アプリケーションルート
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(app_root, AUDIT_LOG_FILENAME)

# 監査ログの設定
def setup_audit_logging():
    """監査ログの設定を初期化"""
    audit_log_path = get_audit_log_path()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(audit_log_path),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('audit')

def validate_user_id(user_id):
    """ユーザーIDが正規表現パターンに一致するかチェック"""
    if user_id == DEFAULT_USER_ID:
        return True
    try:
        return bool(re.match(USER_ID_PATTERN, user_id))
    except re.error:
        # 正規表現が無効な場合はFalseを返す
        return False

def allowed_file(filename):
    """ファイル拡張子が許可されているかチェック"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class Config:
    """Flask アプリケーション設定クラス"""
    SECRET_KEY = SECRET_KEY
    
    # データベース設定を動的に構築
    @staticmethod
    def get_sqlalchemy_database_uri():
        """データベースURIを構築"""
        # DATABASE_URLが明示的に設定されている場合はそれを優先
        if DATABASE_URL:
            return DATABASE_URL
        else:
            # パスからURIを構築
            db_path = get_database_path()
            return f'sqlite:///{db_path}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    # ファイルアップロード設定
    @staticmethod
    def get_upload_folder():
        """アップロードフォルダパスを取得"""
        return get_upload_path()
    
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024
    
    @staticmethod
    def init_app(app):
        """アプリケーション初期化時の設定"""
        # アップロードフォルダパスを動的に設定
        app.config['UPLOAD_FOLDER'] = Config.get_upload_folder()
        # アップロードフォルダが存在しない場合は作成（get_upload_path()で既に作成済み）
        pass