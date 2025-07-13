import os
from flask import render_template, request, redirect, url_for, flash, abort, send_from_directory
from datetime import datetime, timezone
from .models import db, Knowledge, Comment, Like, CommentLike, Attachment, Tag
from .utils import get_current_user_id, handle_file_uploads, handle_tags, audit_logger
from .config import SYSTEM_TITLE, MAX_FILE_SIZE_MB

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
        
        # 人気タグ一覧を取得（使用回数上位10位）
        popular_tags = Tag.query.filter(Tag.usage_count > 0).order_by(Tag.usage_count.desc()).limit(10).all()
        
        return render_template('index.html', 
                             knowledge_list=knowledge_list, 
                             current_user_id=current_user_id, 
                             search_query=search_query,
                             my_posts=my_posts,
                             liked_posts=liked_posts,
                             tag_filter=tag_filter,
                             popular_tags=popular_tags,
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

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, '..', 'static'),
            'favicon.ico',
            mimetype='image/vnd.microsoft.icon'
        )