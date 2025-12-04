import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User, Post, Category, Tag, Comment, post_tag
from routes import bp
import os

# 创建应用实例
app = Flask(__name__)

# 配置 - 使用 pymysql
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key_j8K9L#mN$pQ7R@sT2uV5w')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blog_user:blogJCT1005.@localhost/myblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_CHECK_DEFAULT'] = False
app.config['WTF_CSRF_TIME_LIMIT'] = None

# 初始化扩展
db.init_app(app)
csrf = CSRFProtect(app)

# 设置登录管理器
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 注册蓝图
app.register_blueprint(bp)

# 创建数据库表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
