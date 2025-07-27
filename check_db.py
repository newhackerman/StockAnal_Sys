#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速检查数据库记录
"""

import sqlite3
import os

db_path = "data/stock_analyzer.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查analysis_results表
        if ('analysis_results',) in tables:
            cursor.execute("SELECT COUNT(*) FROM analysis_results;")
            count = cursor.fetchone()[0]
            print(f"\nanalysis_results表中有 {count} 条记录")
            
            if count > 0:
                cursor.execute("SELECT id, stock_code, market_type, total_score, recommendation, analysis_date FROM analysis_results ORDER BY analysis_date DESC LIMIT 5;")
                records = cursor.fetchall()
                print("\n最近的5条记录:")
                for record in records:
                    print(f"  ID: {record[0]}, 股票: {record[1]}, 市场: {record[2]}, 评分: {record[3]}, 建议: {record[4]}, 时间: {record[5]}")
        else:
            print("\nanalysis_results表不存在")
            
    except Exception as e:
        print(f"查询数据库时出错: {e}")
    finally:
        conn.close()
else:
    print(f"数据库文件不存在: {db_path}")