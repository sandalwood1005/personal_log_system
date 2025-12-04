import pymysql
pymysql.install_as_MySQLdb()

from app import app, db
from sqlalchemy import text

def deep_analyze():
    with app.app_context():
        print("🔍 深入分析查询性能...")
        
        # 详细分析执行计划
        print("\n1. 详细EXPLAIN分析:")
        explain_result = db.session.execute(text("""
            EXPLAIN FORMAT=JSON 
            SELECT post.*, user.* 
            FROM post 
            JOIN user ON post.user_id = user.id 
            ORDER BY post.created_at DESC 
            LIMIT 20
        """))
        
        for row in explain_result:
            import json
            plan = json.loads(row[0])
            print(f"   查询成本: {plan['query_block']['cost_info']['query_cost']}")
            
            # 分析每个表的访问方式
            for table in plan['query_block']['ordering_operation']['table']:
                print(f"   表: {table['table_name']}")
                print(f"     访问类型: {table['access_type']}")
                print(f"     扫描行数: {table['rows_examined_per_scan']}")
                if 'key' in table:
                    print(f"     使用索引: {table['key']}")
        
        # 检查表统计信息
        print("\n2. 表统计信息:")
        stats = db.session.execute(text("""
            SELECT 
                TABLE_NAME,
                TABLE_ROWS,
                AVG_ROW_LENGTH,
                DATA_LENGTH,
                INDEX_LENGTH,
                round(DATA_LENGTH/1024/1024, 2) as data_mb,
                round(INDEX_LENGTH/1024/1024, 2) as index_mb
            FROM information_schema.TABLES 
            WHERE TABLE_SCHEMA = 'myblog'
        """))
        
        for table in stats:
            print(f"   {table[0]}: {table[1]}行, 数据:{table[5]}MB, 索引:{table[6]}MB")
            
        # 检查现有索引
        print("\n3. 当前索引状态:")
        for table in ['post', 'user']:
            indexes = db.session.execute(text(f"SHOW INDEX FROM {table}"))
            print(f"   {table}表索引:")
            for idx in indexes:
                print(f"     - {idx[2]}: {idx[4]}")

if __name__ == '__main__':
    deep_analyze()
