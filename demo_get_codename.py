# -*- coding: utf-8 -*-
"""
get_codename.py 功能演示
"""

from get_codename import get_codename, search_stocks, get_stock_count

def demo():
    print("🎯 get_codename.py 优化功能演示")
    print("=" * 50)
    
    print(f"📊 当前股票数据库包含 {get_stock_count()} 只股票")
    print()
    
    # 演示基本查询功能
    print("1️⃣ 基本查询功能（静态数据）")
    print("-" * 30)
    
    test_cases = [
        ("长电科技", "code", "根据名称查代码"),
        ("600584", "name", "根据代码查名称"),
        ("00700", "name", "港股查询"),
        ("AAPL", "name", "美股查询")
    ]
    
    for stock, return_type, desc in test_cases:
        result = get_codename(stock, return_type)
        print(f"  {desc}: {stock} -> {result}")
    
    print()
    
    # 演示模糊搜索
    print("2️⃣ 模糊搜索功能")
    print("-" * 30)
    
    keywords = ["科技", "银行", "能源"]
    for keyword in keywords:
        print(f"  搜索 '{keyword}' 相关股票:")
        results = search_stocks(keyword, 3)
        for result in results:
            print(f"    • {result['code']} - {result['name']}")
        print()
    
    # 演示实时查询（如果需要）
    print("3️⃣ 实时查询功能演示")
    print("-" * 30)
    print("  注意: 如果静态数据中没有找到股票，系统会自动进行实时查询")
    print("  并将结果添加到静态数据文件中，实现自动更新。")
    print()
    
    # 演示错误处理
    print("4️⃣ 错误处理")
    print("-" * 30)
    
    error_cases = [None, "", "不存在的股票"]
    for case in error_cases:
        result = get_codename(case)
        print(f"  查询 '{case}': {result}")
    
    print()
    print("✅ 演示完成！")
    print()
    print("💡 主要优化点:")
    print("  • 支持A股、港股、美股查询")
    print("  • 静态数据查不到时自动实时查询")
    print("  • 查询结果自动更新到静态文件")
    print("  • 完善的错误处理和日志记录")
    print("  • 模糊搜索和数据统计功能")

if __name__ == '__main__':
    demo()