#!/usr/bin/env python3
"""
MySQL数据库重置脚本 - 适用于mysqlclient驱动
"""

from app import app, db, User, Post, Category, Tag, Comment

def reset_database():
    with app.app_context():
        try:
            print("开始重置MySQL数据库...")
            
            # 删除所有表
            print("删除现有表...")
            db.drop_all()
            
            # 重新创建表
            print("创建新表...")
            db.create_all()
            
            # 创建默认分类
            print("创建默认分类...")
            default_categories = ['技术', '编程', '数据库', 'Linux', 'Python']
            for cat_name in default_categories:
                category = Category(name=cat_name)
                db.session.add(category)
            
            db.session.commit()
            
            # 创建测试用户
            print("创建测试用户...")
            test_user = User(
                username='admin',
                email='admin@example.com'
            )
            test_user.set_password('admin123')
            db.session.add(test_user)
            db.session.commit()
            
            # 创建测试文章
            print("创建测试文章...")
            test_post = Post(
                title='欢迎使用技术博客',
                content='这是第一篇测试文章，祝贺你成功配置MySQL数据库！',
                user_id=test_user.id,
                category_id=1  # 第一个分类
            )
            db.session.add(test_post)
            db.session.commit()
            
            print("✅ 数据库重置成功！")
            print(f"   数据库: myblog")
            print(f"   测试用户: admin / admin123")
            print(f"   文章数量: {Post.query.count()}")
            print(f"   分类数量: {Category.query.count()}")
            print(f"   用户数量: {User.query.count()}")
            
        except Exception as e:
            print(f"❌ 数据库重置失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    reset_database()
