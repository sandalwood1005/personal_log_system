import pymysql
pymysql.install_as_MySQLdb()

from flask import Blueprint, request, flash, redirect, render_template, url_for, abort
from models import db, User, Post, Category, Tag, Comment, post_tag
import json
from flask_login import login_user, login_required, logout_user, current_user

# 安全导入Celery任务
try:
    from celery_tasks import process_user_registration, update_post_statistics
    CELERY_AVAILABLE = True
    print("✅ Celery任务可用")
except ImportError:
    CELERY_AVAILABLE = False
    print("⚠️  Celery不可用，使用同步模式")

# 创建蓝图
bp = Blueprint('main', __name__) #创建一个名为 main 的蓝图实例

# 路由定义
@bp.route('/')
def index():
    try:
        page = request.args.get('page', 1, type=int)
        posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=5,error_out=False)
        categories = Category.query.all()
        return render_template('index.html', posts=posts, categories=categories)
    except Exception as e:
        print(f"Error in index route: {str(e)}")  # 打印错误信息以便调试
        # 确保即使没有数据也能显示页面
        return render_template('index.html', posts=None, categories=[])


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method=='POST':
        try:
            # 检查是否是 JSON 请求
            if request.is_json:
                data = request.get_json()
                username = data.get('username')
                email = data.get('email')
                password = data.get('password')
            else:
                username = request.form.get('username')
                email = request.form.get('email')
                password = request.form.get('password')
            
            # 验证所有字段不为空
            if not username or not email or not password:
                if request.is_json:
                    return {'error': '所有字段都必须填写'}, 400
                flash('所有字段都必须填写','error')
                return redirect(url_for('main.register'))
            
            if User.query.filter_by(username=username).first():
                if request.is_json:
                    return {'error': '用户名已存在'}, 400
                flash('用户名已存在','error')
                return redirect(url_for('main.register'))
            
            if User.query.filter_by(email=email).first():
                if request.is_json:
                    return {'error': '邮箱已注册'}, 400
                flash('邮箱已注册','error')
                return redirect(url_for('main.register'))
                
            # 创建新用户
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

              # 🎯 关键改进：使用Celery异步处理注册后续
            if CELERY_AVAILABLE:
                process_user_registration.delay(user.id)
                print(f"✅ 异步处理用户注册: {user.username}")
            else:
                print(f"⚠️  同步处理用户注册: {user.username}")

            flash('注册成功，请登录', 'success')
            return redirect(url_for('main.login'))
            
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return {'error': '注册过程中发生错误'}, 500
            flash('注册过程中发生错误，请重试','error')
            return redirect(url_for('main.register'))
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        # 检查是否是 JSON 请求
        if request.is_json:
            data = request.get_json()
            username = data.get('username')
            password = data.get('password')
            remember = data.get('remember', False)
        else:
            username = request.form.get('username')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user=user, remember=remember)
            if request.is_json:
                return {'message': '登录成功', 'user': {'username': user.username, 'email': user.email}}, 200
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.index'))
        
        if request.is_json:
            return {'error': '用户名或密码错误'}, 401
        flash('用户名错误或密码错误','error')
    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已退出登录','success')
    return redirect(url_for('main.index'))


@bp.route('/profile')
@login_required
def profile():
    # 强制刷新用户数据，确保获取最新的文章和评论计数
    user = User.query.get(current_user.id)
    # 手动加载文章和评论集合，确保计数是最新的
    posts_count = Post.query.filter_by(user_id=user.id).count()
    comments_count = Comment.query.filter_by(user_id=user.id).count()
    return render_template('profile.html', user=user, posts_count=posts_count, comments_count=comments_count)



@bp.route('/post/<int:post_id>')
def show_post(post_id):
    # 🎯 异步更新文章统计
    if CELERY_AVAILABLE:
        update_post_statistics.delay(post_id)

    return render_template('post.html',post=post)

@bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    if not content:
        flash('评论内容不能为空', 'error')
        return redirect(url_for('main.show_post', post_id=post_id))
    
    comment = Comment(content=content, post_id=post_id, user_id=current_user.id)
    db.session.add(comment)
    db.session.commit()
    flash('评论发表成功', 'success')
    return redirect(url_for('main.show_post', post_id=post_id))


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method=='POST':
        if request.is_json:
            data = request.get_json()
            title = data.get('title')
            content = data.get('content')
            category_id = data.get('category')
            tags = data.get('tags', '')
            if isinstance(tags, list):
                tag_names = tags
            else:
                tag_names = [t.strip() for t in tags.split(',') if t.strip()]
        else:
            title = request.form.get('title')
            content = request.form.get('content')
            category_id = request.form.get('category')
            tags = request.form.get('tags', '')
            tag_names = [t.strip() for t in tags.split(',') if t.strip()]
        
        if not title or not content or not category_id:
            if request.is_json:
                return {'error': '标题、内容和分类都是必填项'}, 400
            flash('标题、内容和分类都是必填项', 'error')
            return redirect(url_for('main.create_post'))
            
        # 验证分类是否存在
        if not Category.query.get(category_id):
            if request.is_json:
                return {'error': '无效的分类ID'}, 400
            flash('无效的分类', 'error')
            return redirect(url_for('main.create_post'))
            
        post=Post(title=title,content=content,user_id=current_user.id,category_id=category_id)

        for tag_name in tag_names:
            tag_name=tag_name.strip()
            if tag_name:
                tag=Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag=Tag(name=tag_name)
                    db.session.add(tag)
                post.tags.append(tag)
        db.session.add(post)
        db.session.commit()
        flash('文章已发布','success')
        return redirect(url_for('main.index'))
    categories=Category.query.all()
    return render_template('create_post.html',categories=categories)


@bp.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author!=current_user:
        abort(403)
    if request.method=='POST':
        post.title=request.form.get('title')
        post.content=request.form.get('content')
        post.category_id=request.form.get('category')
        tag_names=request.form.get('tags','').split(',')
        post.tags=[]
        for tag_name in tag_names:
            tag_name=tag_name.strip()
            if tag_name:
                tag=Tag.query.filter_by(name=tag_name).first()
                if not tag:
                    tag=Tag(name=tag_name)
                    db.session.add(tag)
                post.tags.append(tag)
        db.session.commit()
        flash('文章已更新','success')
        return redirect(url_for('main.show_post', post_id=post.id))
    categories=Category.query.all()
    tags_str=','.join([tag.name for tag in post.tags])
    return render_template('edit_post.html', post=post, categories=categories, tags_str=tags_str)


@bp.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author!=current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('文章已删除','success')
    return redirect(url_for('main.index'))

@bp.route('/categories', methods=['GET', 'POST'])
@login_required
def manage_categories():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            name = data.get('name')
            action = data.get('action')
            category_id = data.get('id')
        else:
            name = request.form.get('name')
            action = request.form.get('action')
            category_id = request.form.get('id')

        if action == 'add':
            if not name:
                flash('分类名称不能为空', 'error')
                return redirect(url_for('main.manage_categories'))
            
            if Category.query.filter_by(name=name).first():
                flash('分类已存在', 'error')
                return redirect(url_for('main.manage_categories'))
            
            category = Category(name=name)
            db.session.add(category)
            flash('分类添加成功', 'success')

        elif action == 'edit' and category_id:
            category = Category.query.get_or_404(category_id)
            if not name:
                flash('分类名称不能为空', 'error')
                return redirect(url_for('main.manage_categories'))
            
            if Category.query.filter(Category.id != category_id, Category.name == name).first():
                flash('分类名称已存在', 'error')
                return redirect(url_for('main.manage_categories'))
            
            category.name = name
            flash('分类更新成功', 'success')

        elif action == 'delete' and category_id:
            category = Category.query.get_or_404(category_id)
            # 检查是否有文章使用此分类
            if Post.query.filter_by(category_id=category_id).first():
                flash('该分类下有文章，无法删除', 'error')
                return redirect(url_for('main.manage_categories'))
            
            db.session.delete(category)
            flash('分类删除成功', 'success')

        db.session.commit()
        return redirect(url_for('main.manage_categories'))

    categories = Category.query.order_by(Category.name).all()
    return render_template('categories.html', categories=categories)
