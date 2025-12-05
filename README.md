# 个人日志系统 (Personal Log System)
一个基于 Flask 构建的轻量级技术博客系统，支持用户管理、文章发布、分类标签、评论互动等核心功能，集成缓存和异步任务提升性能。

## ✨ 功能特点
- **用户管理**：注册、登录、退出及个人资料展示，支持密码加密存储

- **文章管理**：创建、编辑、查看、删除文章，支持富文本内容
  
- **分类与标签**：文章可关联分类和多个标签，方便内容归类和检索
  
- **评论系统**：登录用户可对文章发表评论，实现互动交流
  
- **性能优化**：
  - 基于 Redis 的缓存机制，减少数据库访问压力
  - Celery 异步任务处理，提升用户操作响应速度
  - 数据库索引优化，加速查询效率

## 🛠️ 技术栈
- **后端**：
  - Python 3.8+
  - Flask 2.0.3（Web 框架）
  - Flask-SQLAlchemy 2.5.1（ORM 数据库操作）
  - Flask-Login 0.5.0（用户认证）
  - Celery 5.2.3（异步任务队列）
  - Redis（缓存与 Celery 消息代理）
  - SQLite/MySQL（数据库，支持切换）
- **前端**：
  - HTML5/CSS3
  - JavaScript
  - Bootstrap 5（UI 框架）
  - Font Awesome（图标库）

## 🚀 快速开始
### 环境准备
1.克隆仓库
```bash
git clone https://github.com/sandalwood1005/personal-log-system.git
cd personal-log-system
```
2.创建虚拟环境并激活
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```
3.安装依赖
```bash
pip install -r requirements.txt
```
4.配置环境变量（可选）
创建 `.env` 文件（参考 `.env.example`），配置数据库连接、密钥等信息：
```plaintext
SECRET_KEY=your_secret_key
SQLALCHEMY_DATABASE_URI=sqlite:///blog.db  # 或 MySQL 地址
REDIS_URL=redis://localhost:6379/0
```
### 启动应用
1.初始化数据库
```bash
# 进入 Python 交互环境
python
>>> from app import db
>>> db.create_all()
>>> exit()
```
2.启动 Redis（用于缓存和 Celery）
```bash
redis-server
```
3.启动 Celery worker（异步任务处理）
```bash
celery -A celery_config worker --loglevel=info
```
4.启动 Flask 应用
```bash
flask run
# 或
python app.py
```
5.访问系统
打开浏览器访问 `http://127.0.0.1:5000`

## 📂 项目结构
```plaintext
personal-log-system/
├── app.py               # 应用入口
├── models.py            # 数据模型定义（用户、文章、评论等）
├── routes.py            # 核心路由与视图逻辑
├── routes_with_cache.py # 带缓存的路由
├── routes_with_tasks.py # 带异步任务的路由
├── cache_helper.py      # Redis 缓存工具类
├── celery_config.py     # Celery 配置
├── celery_tasks.py      # 异步任务定义
├── requirements.txt     # 依赖列表
├── templates/           # HTML 模板
│   ├── base.html        # 基础模板
│   ├── index.html       # 首页
│   ├── post.html        # 文章详情页
│   ├── create_post.html # 创建文章页
│   └── ...
└── static/              # 静态资源（CSS、JS、图片等）
```

## 🔍 核心功能模块
**1.用户认证**：基于 Flask-Login 实现，支持 session 管理和密码哈希验证

**2.文章系统**：支持分页查询、分类筛选、标签检索，集成缓存提升加载速度

**3.异步任务**：用户注册后通知、文章统计更新等操作通过 Celery 异步执行

**4.缓存策略**：首页、文章详情页等高频访问页面添加缓存，减少数据库压力

## 📝 许可证
本项目采用 MIT 许可证 - 详见 LICENSE 文件。
