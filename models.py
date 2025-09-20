from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

# 创建数据库实例
db = SQLAlchemy()

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