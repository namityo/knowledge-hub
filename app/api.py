#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
REST API for Knowledge Base Application

外部アプリケーション向けのREST APIエンドポイント
"""

from flask import Blueprint, request
from functools import wraps
import json
from .models import Knowledge, Tag
from .config import JST, API_KEY, API_KEY_HEADER_NAME
from datetime import timezone

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

def json_response(data, status_code=200):
    """Unicode文字を正しく表示するJSONレスポンスを作成"""
    from flask import Response
    json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    return Response(
        json_str,
        status=status_code,
        mimetype='application/json; charset=utf-8'
    )

def require_api_key(f):
    """API認証デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # API_KEYが設定されていない場合は認証をスキップ
        if not API_KEY:
            return f(*args, **kwargs)
        
        # ヘッダーからAPIキーを取得
        api_key = request.headers.get(API_KEY_HEADER_NAME)
        
        # APIキーが提供されていない場合
        if not api_key:
            return json_response({
                'status': 'error',
                'message': f'APIキーが必要です。ヘッダー「{API_KEY_HEADER_NAME}」にAPIキーを指定してください。'
            }, 401)
        
        # APIキーが正しくない場合
        if api_key != API_KEY:
            return json_response({
                'status': 'error',
                'message': 'APIキーが無効です。'
            }, 403)
        
        return f(*args, **kwargs)
    return decorated_function

def serialize_knowledge(knowledge):
    """Knowledge オブジェクトをJSON形式にシリアライズ"""
    # 日本時間に変換
    created_at_jst = None
    updated_at_jst = None
    
    if knowledge.created_at:
        if knowledge.created_at.tzinfo is None:
            created_at_utc = knowledge.created_at.replace(tzinfo=timezone.utc)
        else:
            created_at_utc = knowledge.created_at
        created_at_jst = created_at_utc.astimezone(JST).strftime('%Y-%m-%d %H:%M:%S')
    
    if knowledge.updated_at:
        if knowledge.updated_at.tzinfo is None:
            updated_at_utc = knowledge.updated_at.replace(tzinfo=timezone.utc)
        else:
            updated_at_utc = knowledge.updated_at
        updated_at_jst = updated_at_utc.astimezone(JST).strftime('%Y-%m-%d %H:%M:%S')
    
    return {
        'id': knowledge.id,
        'title': knowledge.title,
        'content': knowledge.content,
        'author': knowledge.author,
        'created_at': created_at_jst,
        'updated_at': updated_at_jst,
        'like_count': len(knowledge.likes),
        'comment_count': len(knowledge.comments),
        'attachment_count': len(knowledge.attachments),
        'tags': [{'id': tag.id, 'name': tag.name, 'color': tag.color} for tag in knowledge.tags],
        'is_draft': knowledge.is_draft
    }

@api_bp.route('/articles/latest', methods=['GET'])
@require_api_key
def get_latest_articles():
    """最新記事一覧を取得 (公開記事のみ)"""
    try:
        # クエリパラメータの取得
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)
        author = request.args.get('author', None)
        tag = request.args.get('tag', None)
        since = request.args.get('since', None)  # 指定日付以降の記事フィルタ
        
        # limitの上限設定（100件まで）
        if limit > 100:
            limit = 100
        
        # 基本クエリ（下書きを除外）
        query = Knowledge.query.filter(Knowledge.is_draft == False)
        
        # 作成者フィルタ
        if author:
            query = query.filter(Knowledge.author == author)
        
        # タグフィルタ
        if tag:
            query = query.filter(Knowledge.tags.any(Tag.name == tag))
        
        # 日付フィルタ（指定日付以降の記事）
        if since:
            try:
                from datetime import datetime
                # 複数の日付フォーマットに対応
                date_formats = [
                    '%Y-%m-%d',           # 2025-07-13
                    '%Y-%m-%d %H:%M:%S',  # 2025-07-13 10:30:00
                    '%Y-%m-%d %H:%M',     # 2025-07-13 10:30
                    '%Y/%m/%d',           # 2025/07/13
                    '%Y%m%d',             # 20250713
                ]
                
                since_date = None
                for date_format in date_formats:
                    try:
                        since_date = datetime.strptime(since, date_format)
                        break
                    except ValueError:
                        continue
                
                if since_date is None:
                    return json_response({
                        'status': 'error',
                        'message': f'日付フォーマットが無効です。有効な形式: YYYY-MM-DD, YYYY-MM-DD HH:MM:SS, YYYY/MM/DD, YYYYMMDD'
                    }, 400)
                
                # updated_at が指定日付以降の記事をフィルタ
                query = query.filter(Knowledge.updated_at >= since_date)
                
            except Exception as e:
                return json_response({
                    'status': 'error',
                    'message': f'日付パラメータの処理中にエラーが発生しました: {str(e)}'
                }, 400)
        
        # 最新順でソート
        query = query.order_by(Knowledge.updated_at.desc())
        
        # ページネーション
        articles = query.offset(offset).limit(limit).all()
        total_count = query.count()
        
        # レスポンス構築
        response_data = {
            'status': 'success',
            'data': {
                'articles': [serialize_knowledge(article) for article in articles],
                'pagination': {
                    'total': total_count,
                    'limit': limit,
                    'offset': offset,
                    'has_more': (offset + limit) < total_count
                }
            }
        }
        
        return json_response(response_data, 200)
        
    except Exception as e:
        return json_response({
            'status': 'error',
            'message': f'記事の取得中にエラーが発生しました: {str(e)}'
        }, 500)

@api_bp.route('/articles/<int:article_id>', methods=['GET'])
@require_api_key
def get_article(article_id):
    """特定記事の詳細を取得"""
    try:
        article = Knowledge.query.filter(
            Knowledge.id == article_id,
            Knowledge.is_draft == False
        ).first()
        
        if not article:
            return json_response({
                'status': 'error',
                'message': '記事が見つかりません'
            }, 404)
        
        return json_response({
            'status': 'success',
            'data': serialize_knowledge(article)
        }, 200)
        
    except Exception as e:
        return json_response({
            'status': 'error',
            'message': f'記事の取得中にエラーが発生しました: {str(e)}'
        }, 500)

@api_bp.route('/tags', methods=['GET'])
@require_api_key
def get_tags():
    """タグ一覧を取得"""
    try:
        tags = Tag.query.order_by(Tag.usage_count.desc()).all()
        
        response_data = {
            'status': 'success',
            'data': {
                'tags': [{
                    'id': tag.id,
                    'name': tag.name,
                    'color': tag.color,
                    'usage_count': tag.usage_count
                } for tag in tags]
            }
        }
        
        return json_response(response_data, 200)
        
    except Exception as e:
        return json_response({
            'status': 'error',
            'message': f'タグの取得中にエラーが発生しました: {str(e)}'
        }, 500)

@api_bp.route('/articles/popular', methods=['GET'])
@require_api_key
def get_popular_articles():
    """人気記事ランキングを取得（直近30日の閲覧数・いいね数・コメント数別）"""
    try:
        from .config import POPULAR_ARTICLES_COUNT
        from .utils import get_bulk_engagement_stats
        
        limit = request.args.get('limit', POPULAR_ARTICLES_COUNT, type=int)
        days = request.args.get('days', 30, type=int)
        
        if limit > 100:
            limit = 100
        
        if days > 365:
            days = 365  # 最大1年間
        
        # 全記事を取得（下書きを除外）
        all_knowledge = Knowledge.query.filter(Knowledge.is_draft == False).all()
        
        if not all_knowledge:
            return json_response({
                'status': 'success',
                'data': {
                    'top_by_views': [],
                    'top_by_likes': [],
                    'top_by_comments': [],
                    'period_days': days,
                    'limit': limit
                }
            }, 200)
        
        # 指定期間の統計を一括取得
        recent_stats = get_bulk_engagement_stats(all_knowledge, days=days)
        
        # 各記事に統計情報を付与してシリアライズ
        articles_with_stats = []
        for knowledge in all_knowledge:
            stats = recent_stats[knowledge.id]
            
            # 基本記事データをシリアライズ
            article_data = serialize_knowledge(knowledge)
            
            # 期間別統計を追加
            article_data.update({
                'recent_views': stats['views'],
                'recent_likes': stats['likes'],
                'recent_comments': stats['comments']
            })
            
            articles_with_stats.append(article_data)
        
        # 各カテゴリでソートしてトップN件を取得
        top_by_views = sorted(articles_with_stats, key=lambda x: x['recent_views'], reverse=True)[:limit]
        top_by_likes = sorted(articles_with_stats, key=lambda x: x['recent_likes'], reverse=True)[:limit]
        top_by_comments = sorted(articles_with_stats, key=lambda x: x['recent_comments'], reverse=True)[:limit]
        
        response_data = {
            'status': 'success',
            'data': {
                'top_by_views': top_by_views,
                'top_by_likes': top_by_likes,
                'top_by_comments': top_by_comments,
                'period_days': days,
                'limit': limit
            }
        }
        
        return json_response(response_data, 200)
        
    except Exception as e:
        return json_response({
            'status': 'error',
            'message': f'人気記事の取得中にエラーが発生しました: {str(e)}'
        }, 500)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """APIヘルスチェック"""
    return json_response({
        'status': 'healthy',
        'message': 'Knowledge Base API is running'
    }, 200)

def register_api_routes(app):
    """APIルートを登録"""
    app.register_blueprint(api_bp)