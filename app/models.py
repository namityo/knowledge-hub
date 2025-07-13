from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

# 多対多の関連テーブル
knowledge_tags = db.Table('knowledge_tags',
    db.Column('knowledge_id', db.Integer, db.ForeignKey('knowledge.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
)

class Knowledge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    is_draft = db.Column(db.Boolean, default=False, nullable=False)  # 下書きフラグ
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # コメントとのリレーションシップ
    comments = db.relationship('Comment', backref='knowledge', lazy=True, cascade='all, delete-orphan')
    # いいねとのリレーションシップ
    likes = db.relationship('Like', backref='knowledge', lazy=True, cascade='all, delete-orphan')
    # 添付ファイルとのリレーションシップ
    attachments = db.relationship('Attachment', backref='knowledge', lazy=True, cascade='all, delete-orphan')
    # タグとのリレーションシップ（多対多）
    tags = db.relationship('Tag', secondary=knowledge_tags, lazy='subquery', backref=db.backref('knowledge_items', lazy=True))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledge.id'), nullable=False)
    
    # コメントいいねとのリレーションシップ
    comment_likes = db.relationship('CommentLike', backref='comment', lazy=True, cascade='all, delete-orphan')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledge.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 同一ユーザーが同一ナレッジに複数いいねできないようにする
    __table_args__ = (db.UniqueConstraint('user_id', 'knowledge_id', name='unique_user_knowledge_like'),)

class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 同一ユーザーが同一コメントに複数いいねできないようにする
    __table_args__ = (db.UniqueConstraint('user_id', 'comment_id', name='unique_user_comment_like'),)

class Attachment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)  # 元のファイル名
    stored_filename = db.Column(db.String(255), nullable=False)  # 保存時のファイル名（重複回避）
    file_size = db.Column(db.Integer, nullable=False)  # ファイルサイズ（バイト）
    mime_type = db.Column(db.String(100), nullable=False)  # MIMEタイプ
    knowledge_id = db.Column(db.Integer, db.ForeignKey('knowledge.id'), nullable=False)
    uploaded_by = db.Column(db.String(100), nullable=False)  # アップロードしたユーザー
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # タグ名（一意）
    color = db.Column(db.String(7), default='#007bff')  # 表示色（HEX）
    usage_count = db.Column(db.Integer, default=0)  # 使用回数
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.String(100), nullable=False)  # 作成者
    
    def __repr__(self):
        return f'<Tag {self.name}>'