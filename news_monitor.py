# news_monitor.py
# -*- coding: utf-8 -*-
"""
新闻获取系统监控和诊断工具
用于检测和诊断新闻更新问题
"""

import os
import json
import logging
import time
from datetime import datetime, timedelta
from news_fetcher import news_fetcher, news_scheduler

# 设置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('news_monitor')

class NewsMonitor:
    """新闻系统监控器"""
    
    def __init__(self):
        self.last_check_time = None
        
    def check_system_status(self):
        """检查系统整体状态"""
        logger.info("=== 新闻系统状态检查 ===")
        
        # 1. 检查调度器状态
        scheduler_status = self._check_scheduler_status()
        
        # 2. 检查最近的新闻文件
        file_status = self._check_news_files()
        
        # 3. 检查新闻更新频率
        update_status = self._check_update_frequency()
        
        # 4. 检查系统资源
        resource_status = self._check_system_resources()
        
        # 5. 生成诊断报告
        self._generate_report(scheduler_status, file_status, update_status, resource_status)
        
        return {
            'scheduler': scheduler_status,
            'files': file_status,
            'updates': update_status,
            'resources': resource_status
        }
    
    def _check_scheduler_status(self):
        """检查调度器状态"""
        logger.info("检查调度器状态...")
        
        status = {
            'is_running': news_scheduler.is_alive(),
            'thread_alive': news_scheduler.scheduler_thread and news_scheduler.scheduler_thread.is_alive(),
            'consecutive_failures': news_fetcher.consecutive_failures,
            'last_fetch_time': news_fetcher.last_fetch_time
        }
        
        if status['is_running']:
            logger.info("✓ 调度器正在运行")
        else:
            logger.warning("✗ 调度器未运行")
            
        if status['consecutive_failures'] > 0:
            logger.warning(f"⚠ 连续失败次数: {status['consecutive_failures']}")
        else:
            logger.info("✓ 无连续失败记录")
            
        return status
    
    def _check_news_files(self):
        """检查新闻文件状态"""
        logger.info("检查新闻文件状态...")
        
        today = datetime.now()
        file_status = {}
        
        for i in range(3):  # 检查最近3天
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y%m%d')
            filename = news_fetcher.get_news_filename(date)
            
            if os.path.exists(filename):
                try:
                    # 获取文件信息
                    stat = os.stat(filename)
                    file_size = stat.st_size
                    modify_time = datetime.fromtimestamp(stat.st_mtime)
                    
                    # 读取新闻数量
                    with open(filename, 'r', encoding='utf-8') as f:
                        news_data = json.load(f)
                        news_count = len(news_data)
                        
                        # 获取最新新闻时间
                        latest_news_time = None
                        if news_data:
                            latest_news_time = news_data[0].get('fetch_time', '')
                    
                    file_status[date_str] = {
                        'exists': True,
                        'size': file_size,
                        'modify_time': modify_time,
                        'news_count': news_count,
                        'latest_news_time': latest_news_time
                    }
                    
                    logger.info(f"✓ {date_str}: {news_count} 条新闻, 文件大小 {file_size} 字节")
                    
                except Exception as e:
                    file_status[date_str] = {
                        'exists': True,
                        'error': str(e)
                    }
                    logger.error(f"✗ {date_str}: 文件读取错误 - {e}")
            else:
                file_status[date_str] = {'exists': False}
                logger.warning(f"✗ {date_str}: 文件不存在")
        
        return file_status
    
    def _check_update_frequency(self):
        """检查新闻更新频率"""
        logger.info("检查新闻更新频率...")
        
        try:
            # 获取最近的新闻
            recent_news = news_fetcher.get_latest_news(days=1, limit=100)
            
            if not recent_news:
                logger.warning("✗ 没有找到最近的新闻")
                return {'status': 'no_news', 'count': 0}
            
            # 分析新闻时间分布
            now = datetime.now()
            time_buckets = {
                '1小时内': 0,
                '1-6小时': 0,
                '6-12小时': 0,
                '12-24小时': 0,
                '超过24小时': 0
            }
            
            for news in recent_news:
                fetch_time_str = news.get('fetch_time', '')
                if fetch_time_str:
                    try:
                        fetch_time = datetime.strptime(fetch_time_str, '%Y-%m-%d %H:%M:%S')
                        hours_diff = (now - fetch_time).total_seconds() / 3600
                        
                        if hours_diff <= 1:
                            time_buckets['1小时内'] += 1
                        elif hours_diff <= 6:
                            time_buckets['1-6小时'] += 1
                        elif hours_diff <= 12:
                            time_buckets['6-12小时'] += 1
                        elif hours_diff <= 24:
                            time_buckets['12-24小时'] += 1
                        else:
                            time_buckets['超过24小时'] += 1
                    except ValueError:
                        continue
            
            # 检查最新新闻时间
            latest_news = recent_news[0]
            latest_time_str = latest_news.get('fetch_time', '')
            hours_since_latest = None
            
            if latest_time_str:
                try:
                    latest_time = datetime.strptime(latest_time_str, '%Y-%m-%d %H:%M:%S')
                    hours_since_latest = (now - latest_time).total_seconds() / 3600
                except ValueError:
                    pass
            
            logger.info(f"✓ 最近24小时新闻数量: {len(recent_news)}")
            for bucket, count in time_buckets.items():
                if count > 0:
                    logger.info(f"  {bucket}: {count} 条")
            
            if hours_since_latest is not None:
                if hours_since_latest > 2:
                    logger.warning(f"⚠ 最新新闻距今 {hours_since_latest:.1f} 小时，可能更新不及时")
                else:
                    logger.info(f"✓ 最新新闻距今 {hours_since_latest:.1f} 小时")
            
            return {
                'status': 'ok',
                'count': len(recent_news),
                'time_buckets': time_buckets,
                'hours_since_latest': hours_since_latest
            }
            
        except Exception as e:
            logger.error(f"✗ 检查更新频率时出错: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _check_system_resources(self):
        """检查系统资源状态"""
        logger.info("检查系统资源状态...")
        
        try:
            import psutil
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 磁盘使用率
            disk = psutil.disk_usage('.')
            disk_percent = disk.percent
            
            logger.info(f"✓ CPU使用率: {cpu_percent}%")
            logger.info(f"✓ 内存使用率: {memory_percent}%")
            logger.info(f"✓ 磁盘使用率: {disk_percent}%")
            
            # 检查是否有资源瓶颈
            warnings = []
            if cpu_percent > 80:
                warnings.append(f"CPU使用率过高: {cpu_percent}%")
            if memory_percent > 80:
                warnings.append(f"内存使用率过高: {memory_percent}%")
            if disk_percent > 90:
                warnings.append(f"磁盘使用率过高: {disk_percent}%")
            
            for warning in warnings:
                logger.warning(f"⚠ {warning}")
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent,
                'warnings': warnings
            }
            
        except ImportError:
            logger.warning("⚠ psutil未安装，无法检查系统资源")
            return {'status': 'psutil_not_available'}
        except Exception as e:
            logger.error(f"✗ 检查系统资源时出错: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def _generate_report(self, scheduler_status, file_status, update_status, resource_status):
        """生成诊断报告"""
        logger.info("=== 诊断报告 ===")
        
        issues = []
        recommendations = []
        
        # 分析调度器问题
        if not scheduler_status['is_running']:
            issues.append("调度器未运行")
            recommendations.append("重启新闻调度器: news_scheduler.start()")
        
        if scheduler_status['consecutive_failures'] >= 3:
            issues.append(f"连续失败次数过多: {scheduler_status['consecutive_failures']}")
            recommendations.append("检查网络连接和API状态，考虑重置失败计数器")
        
        # 分析文件问题
        today_str = datetime.now().strftime('%Y%m%d')
        if today_str not in file_status or not file_status[today_str].get('exists'):
            issues.append("今日新闻文件不存在")
            recommendations.append("手动执行一次新闻获取: news_fetcher.fetch_and_save()")
        
        # 分析更新频率问题
        if update_status.get('hours_since_latest', 0) > 4:
            issues.append("新闻更新不及时")
            recommendations.append("检查调度器状态和网络连接")
        
        # 分析资源问题
        if 'warnings' in resource_status and resource_status['warnings']:
            issues.extend(resource_status['warnings'])
            recommendations.append("优化系统资源使用或升级硬件")
        
        # 输出结果
        if issues:
            logger.warning("发现以下问题:")
            for i, issue in enumerate(issues, 1):
                logger.warning(f"  {i}. {issue}")
            
            logger.info("建议采取以下措施:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(f"  {i}. {rec}")
        else:
            logger.info("✓ 系统运行正常，未发现明显问题")
    
    def test_news_fetch(self):
        """测试新闻获取功能"""
        logger.info("=== 测试新闻获取功能 ===")
        
        try:
            # 记录开始时间
            start_time = datetime.now()
            
            # 执行获取
            success = news_fetcher.fetch_and_save()
            
            # 记录结束时间
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            if success:
                logger.info(f"✓ 新闻获取测试成功，耗时 {duration:.2f} 秒")
            else:
                logger.error(f"✗ 新闻获取测试失败，耗时 {duration:.2f} 秒")
            
            return success
            
        except Exception as e:
            logger.error(f"✗ 新闻获取测试异常: {e}")
            return False
    
    def restart_scheduler(self):
        """重启调度器"""
        logger.info("=== 重启新闻调度器 ===")
        
        try:
            # 停止现有调度器
            news_scheduler.stop()
            time.sleep(2)  # 等待停止
            
            # 启动新调度器
            news_scheduler.start()
            
            # 检查状态
            time.sleep(1)
            if news_scheduler.is_alive():
                logger.info("✓ 调度器重启成功")
                return True
            else:
                logger.error("✗ 调度器重启失败")
                return False
                
        except Exception as e:
            logger.error(f"✗ 重启调度器时出错: {e}")
            return False

# 创建监控器实例
monitor = NewsMonitor()

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'status':
            monitor.check_system_status()
        elif command == 'test':
            monitor.test_news_fetch()
        elif command == 'restart':
            monitor.restart_scheduler()
        else:
            print("用法: python news_monitor.py [status|test|restart]")
            print("  status  - 检查系统状态")
            print("  test    - 测试新闻获取")
            print("  restart - 重启调度器")
    else:
        # 默认执行状态检查
        monitor.check_system_status()

if __name__ == "__main__":
    main()