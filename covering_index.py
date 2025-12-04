import pymysql
pymysql.install_as_MySQLdb()

from app import app, db
from sqlalchemy import text

def create_covering_index():
    with app.app_context():
        print("📚 创建覆盖索引优化...")
        
        try:
            # 删除可能存在的旧索引
            db.session.execute(text("DROP INDEX IF EXISTS idx_post_covering ON post"))
            
            # 创建覆盖索引（包含查询需要的所有字段）
            print("创建覆盖索引...")
            db.session.execute(text("""
                CREATE INDEX idx_post_covering ON post 
                (created_at DESC, user_id, title, category_id)
            """))
            
            db.session.commit()
            print("✅ 覆盖索引创建完成")
            
            # 验证索引
            indexes = db.session.execute(text("SHOW INDEX FROM post WHERE Key_name = 'idx_post_covering'"))
            print("覆盖索引字段:")
            for idx in indexes:
                print(f"   - {idx[4]}")
                
        except Exception as e:
            print(f"❌ 索引创建失败: {e}")
            db.session.rollback()

if __name__ == '__main__':
    create_covering_index()
