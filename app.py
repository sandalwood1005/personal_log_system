from flask import Flask,request,redirect,render_template,url_for,flash,abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from flask_wtf.csrf import CSRFProtect
import os

app=Flask(__name__)

app.config['SECRET_KEY']='logsystemJCT1005.'
csrf = CSRFProtect(app)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///blog.db'
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # 禁用默认的CSRF检查
app.config['WTF_CSRF_TIME_LIMIT'] = None     # 移除CSRF令牌的时间限制
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db=SQLAlchemy(app)

#初始化登录管理器
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'  #设置登录视图

#用户模型
class User(UserMixin,db.Model): #这行代码定义了一个用户模型类，它同时继承了两个类：UserMixin 和 db.Model。
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(80),unique=True,nullable=False)
    password_hash=db.Column(db.String(120))
    email=db.Column(db.String(120),unique=True,nullable=False)
    posts=db.relationship('Post',backref='author',lazy=True)
    comments=db.relationship('Comment',backref='author',lazy=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

    def set_password(self,password):
        self.password_hash=generate_password_hash(password)
    
    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

# 文章模型
class Post(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(200),nullable=False)
    content=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    category_id=db.Column(db.Integer,db.ForeignKey('category.id'),nullable=False)
    comments=db.relationship('Comment',backref='post',lazy=True)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
    updated_at=db.Column(db.DateTime,default=datetime.utcnow,onupdate=datetime.utcnow)
    tags=db.relationship('Tag',secondary='post_tag',backref='posts')

#标签模型
class Tag(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),unique=True,nullable=False)

#文章标签关联表
post_tag=db.Table('post_tag',
                  db.Column('post_id',db.Integer,db.ForeignKey('post.id'),primary_key=True),
                  db.Column('tag_id',db.Integer,db.ForeignKey('tag.id'),primary_key=True)
                )   

#分类模型
class Category(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),unique=True,nullable=False)
    posts=db.relationship('Post',backref='category',lazy=True)

#评论模型
class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    content=db.Column(db.Text,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    post_id=db.Column(db.Integer,db.ForeignKey('post.id'),nullable=False)
    created_at=db.Column(db.DateTime,default=datetime.utcnow)

#用户加载回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 创建数据库表
with app.app_context():
    db.create_all()



# 路由定义
@app.route('/')
def index():
    page=request.args.get('page',1,type=int)
    posts=Post.query.order_by(Post.created_at.desc()).paginate(page=page,per_page=5)
    categories=Category.query.all()
    return render_template('index.html',posts=posts,categories=categories)

@app.route('/register',methods=['GET','POST'])
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
                return redirect(url_for('register'))
    
            if User.query.filter_by(username=username).first():
                if request.is_json:
                    return {'error': '用户名已存在'}, 400
                flash('用户名已存在','error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                if request.is_json:
                    return {'error': '邮箱已注册'}, 400
                flash('邮箱已注册','error')
                return redirect(url_for('register'))
            
            user=User(username=username,email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            if request.is_json:
                return {'message': '注册成功'}, 200
            flash('注册成功，请登录','success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return {'error': '注册过程中发生错误'}, 500
            flash('注册过程中发生错误，请重试','error')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login',methods=['GET',"POST"])
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
            return redirect(url_for('index') or next_page)
        
        if request.is_json:
            return {'error': '用户名或密码错误'}, 401
        flash('用户名错误或密码错误','error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('你已退出登录','success')
    return redirect(url_for('index'))

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html',user=current_user)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    post=Post.query.get_or_404(post_id)
    return render_template('post.html',post=post)

@app.route('/create',methods=['GET','POST'])
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
            return redirect(url_for('create_post'))
            
        # 验证分类是否存在
        if not Category.query.get(category_id):
            if request.is_json:
                return {'error': '无效的分类ID'}, 400
            flash('无效的分类', 'error')
            return redirect(url_for('create_post'))
            
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
        return redirect(url_for('index'))
    categories=Category.query.all()
    return render_template('create_post.html',categories=categories)

@app.route('/edit/<int:post_id>',methods=['GET','POST'])
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
        return redirect(url_for('show_post',post_id=post.id))
    categories=Category.query.all()
    tags_str=','.join([tag.name for tag in post.tags])
    return render_template('edit_post.html',post=post,categories=categories,tags_str=tags_str)

@app.route('/delete/<int:post_id>',methods=['POST'])
@login_required
def delete_post(post_id):
    post=Post.query.get_or_404(post_id)
    if post.author!=current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('文章已删除','success')
    return redirect(url_for('index'))


if __name__=='__main__':
    app.run(debug=True)






        


