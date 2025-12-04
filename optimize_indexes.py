import pymysql
pymysql.install_as_MySQLdb()

from app import app, db
from sqlalchemy import text

def optimize_indexes():
    with app.app_context():
        print("⚡ 开始优化索引...")
        
        try:
            # 添加 created_at 索引（优化 ORDER BY）
            print("1. 添加 created_at 索引...")
            db.session.execute(text("CREATE INDEX idx_post_created_at ON post(created_at DESC)"))
            
            # 添加 user_id 索引（优化 JOIN）
            print("2. 添加 user_id 索引...")
            db.session.execute(text("CREATE INDEX idx_post_user_id ON post(user_id)"))
            
            # 添加复合索引（进一步优化）
            print("3. 添加复合索引...")
            db.session.execute(text("CREATE INDEX idx_post_user_created ON post(created_at DESC，user_id )"))
            
            db.session.commit()
            print("✅ 索引优化完成！")
            
            # 验证索引创建
            indexes = db.session.execute(text("SHOW INDEX FROM post"))
            print("\n📊 当前文章表索引:")
            for idx in indexes:
                print(f"   - {idx[2]}: {idx[4]} ({idx[10]})")
                
        except Exception as e:
            print(f"❌ 索引创建失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    optimize_indexes()
