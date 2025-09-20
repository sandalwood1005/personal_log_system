from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash

# 创建应用实例
app = Flask(__name__)

# 配置
app.config['SECRET_KEY'] = 'logsystemJCT1005.'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # 禁用默认的CSRF检查
app.config['WTF_CSRF_TIME_LIMIT'] = None     # 移除CSRF令牌的时间限制

# 初始化扩展
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# 导入模型和路由
from models import User, Post, Category, Tag, Comment, post_tag
from routes import index, register, login, logout, view_post, create_post, edit_post, delete_post

#初始化登录管理器
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'  #设置登录视图

#用户加载回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 创建数据库表
with app.app_context():
    db.create_all()

# 注册路由
app.add_url_rule('/', 'index', index, methods=['GET'])
app.add_url_rule('/register', 'register', register, methods=['GET', 'POST'])
app.add_url_rule('/login', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/logout', 'logout', logout, methods=['GET'])
app.add_url_rule('/post/<int:post_id>', 'view_post', view_post, methods=['GET'])
app.add_url_rule('/create', 'create_post', create_post, methods=['GET', 'POST'])
app.add_url_rule('/edit/<int:post_id>', 'edit_post', edit_post, methods=['GET', 'POST'])
app.add_url_rule('/delete/<int:post_id>', 'delete_post', delete_post, methods=['POST'])

if  __name__=='__main__':
    app.run(debug=True)






        


