# fix_news_update.py
# -*- coding: utf-8 -*-
"""
新闻更新问题快速修复脚本
用于解决常见的新闻不更新问题
"""

import logging
import time
from datetime import datetime
from news_fetcher import news_fetcher, news_scheduler

# 设置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fix_news')

def fix_news_update_issues():
    """修复新闻更新问题"""
    logger.info("=== 开始修复新闻更新问题 ===")
    
    try:
        # 1. 重置连续失败计数器
        logger.info("1. 重置连续失败计数器...")
        news_fetcher.consecutive_failures = 0
        logger.info("✓ 连续失败计数器已重置")
        
        # 2. 清理哈希缓存，防止内存泄漏
        logger.info("2. 清理哈希缓存...")
        original_size = len(news_fetcher.news_hashes)
        news_fetcher._cleanup_old_hashes()
        new_size = len(news_fetcher.news_hashes)
        logger.info(f"✓ 哈希缓存已清理: {original_size} -> {new_size}")
        
        # 3. 停止现有调度器
        logger.info("3. 停止现有调度器...")
        if news_scheduler.is_alive():
            news_scheduler.stop()
            time.sleep(3)  # 等待停止
            logger.info("✓ 调度器已停止")
        else:
            logger.info("✓ 调度器未运行，无需停止")
        
        # 4. 测试新闻获取功能
        logger.info("4. 测试新闻获取功能...")
        success = news_fetcher.fetch_and_save()
        if success:
            logger.info("✓ 新闻获取测试成功")
        else:
            logger.warning("⚠ 新闻获取测试失败，但继续执行修复")
        
        # 5. 重启调度器
        logger.info("5. 重启调度器...")
        news_scheduler.start(interval_minutes=10)
        time.sleep(2)  # 等待启动
        
        if news_scheduler.is_alive():
            logger.info("✓ 调度器重启成功")
        else:
            logger.error("✗ 调度器重启失败")
            return False
        
        logger.info("=== 修复完成 ===")
        logger.info("建议继续监控系统状态，确保问题已解决")
        return True
        
    except Exception as e:
        logger.error(f"修复过程中出错: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def emergency_restart():
    """紧急重启 - 强制重启所有组件"""
    logger.info("=== 执行紧急重启 ===")
    
    try:
        # 强制停止调度器
        logger.info("强制停止调度器...")
        news_scheduler.stop()
        time.sleep(5)
        
        # 重置所有状态
        logger.info("重置系统状态...")
        news_fetcher.consecutive_failures = 0
        news_fetcher.last_fetch_time = None
        news_fetcher.news_hashes.clear()
        news_fetcher._load_existing_hashes()
        
        # 重启调度器
        logger.info("重启调度器...")
        news_scheduler.start(interval_minutes=10)
        time.sleep(3)
        
        if news_scheduler.is_alive():
            logger.info("✓ 紧急重启成功")
            return True
        else:
            logger.error("✗ 紧急重启失败")
            return False
            
    except Exception as e:
        logger.error(f"紧急重启失败: {e}")
        return False

def check_and_fix():
    """检查问题并自动修复"""
    logger.info("=== 自动检查和修复 ===")
    
    issues_found = []
    
    # 检查调度器状态
    if not news_scheduler.is_alive():
        issues_found.append("调度器未运行")
    
    # 检查连续失败次数
    if news_fetcher.consecutive_failures >= 3:
        issues_found.append(f"连续失败次数过多: {news_fetcher.consecutive_failures}")
    
    # 检查哈希缓存大小
    if len(news_fetcher.news_hashes) > news_fetcher.max_hash_size:
        issues_found.append(f"哈希缓存过大: {len(news_fetcher.news_hashes)}")
    
    # 检查最后获取时间
    if news_fetcher.last_fetch_time:
        hours_since_last = (datetime.now() - news_fetcher.last_fetch_time).total_seconds() / 3600
        if hours_since_last > 2:
            issues_found.append(f"距离上次获取时间过长: {hours_since_last:.1f} 小时")
    else:
        issues_found.append("从未成功获取过新闻")
    
    if issues_found:
        logger.warning("发现以下问题:")
        for i, issue in enumerate(issues_found, 1):
            logger.warning(f"  {i}. {issue}")
        
        logger.info("开始自动修复...")
        return fix_news_update_issues()
    else:
        logger.info("✓ 未发现明显问题")
        return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'fix':
            fix_news_update_issues()
        elif command == 'emergency':
            emergency_restart()
        elif command == 'auto':
            check_and_fix()
        else:
            print("用法: python fix_news_update.py [fix|emergency|auto]")
            print("  fix       - 标准修复流程")
            print("  emergency - 紧急重启")
            print("  auto      - 自动检查和修复")
    else:
        # 默认执行自动检查和修复
        check_and_fix()