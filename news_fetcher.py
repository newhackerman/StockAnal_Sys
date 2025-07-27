# news_fetcher.py
# -*- coding: utf-8 -*-
"""
智能分析系统（股票） - 新闻数据获取模块
功能: 获取财联社电报新闻数据并缓存到本地，避免重复内容
"""

import os
import json
import logging
import time
import hashlib
import threading
from datetime import datetime, timedelta, date
import akshare as ak
import pandas as pd

# 设置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('news_fetcher')

# 自定义JSON编码器，处理日期类型
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if pd.isna(obj):  # 处理pandas中的NaN
            return None
        return super(DateEncoder, self).default(obj)

class NewsFetcher:
    def __init__(self, save_dir="data/news"):
        """初始化新闻获取器"""
        self.save_dir = save_dir
        # 确保保存目录存在
        os.makedirs(self.save_dir, exist_ok=True)
        self.last_fetch_time = None
        self.consecutive_failures = 0  # 连续失败次数
        self.max_failures = 5  # 最大连续失败次数
        
        # 哈希集合用于快速判断新闻是否已存在
        self.news_hashes = set()
        self.max_hash_size = 10000  # 限制哈希集合大小，防止内存泄漏
        # 加载已有的新闻哈希
        self._load_existing_hashes()

    def _load_existing_hashes(self):
        """加载已有文件中的新闻哈希值"""
        try:
            # 获取最近3天的文件来加载哈希值
            today = datetime.now()
            for i in range(3):  # 检查今天和前两天的数据
                date = today - timedelta(days=i)
                filename = self.get_news_filename(date)

                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        try:
                            news_data = json.load(f)
                            for item in news_data:
                                # 如果有哈希字段就直接使用，否则计算新的哈希
                                if 'hash' in item:
                                    self.news_hashes.add(item['hash'])
                                else:
                                    content_hash = self._calculate_hash(item['content'])
                                    self.news_hashes.add(content_hash)
                        except json.JSONDecodeError:
                            logger.warning(f"文件 {filename} 格式错误，跳过加载哈希值")

            # 限制哈希集合大小，防止内存泄漏
            if len(self.news_hashes) > self.max_hash_size:
                # 转换为列表并保留最新的哈希值
                hash_list = list(self.news_hashes)
                self.news_hashes = set(hash_list[-self.max_hash_size:])
                logger.warning(f"哈希集合过大，已清理至 {len(self.news_hashes)} 条")

            logger.info(f"已加载 {len(self.news_hashes)} 条新闻哈希值")
        except Exception as e:
            logger.error(f"加载现有新闻哈希值时出错: {str(e)}")
            # 出错时清空哈希集合，保证程序可以继续运行
            self.news_hashes = set()

    def _cleanup_old_hashes(self):
        """清理过期的哈希值，防止内存泄漏"""
        if len(self.news_hashes) > self.max_hash_size:
            # 重新加载最近的哈希值
            self.news_hashes = set()
            self._load_existing_hashes()
            logger.info("已清理过期哈希值")

    def _calculate_hash(self, content):
        """计算新闻内容的哈希值"""
        # 使用MD5哈希算法计算内容的哈希值
        # 对于财经新闻，内容通常是唯一的标识，所以只对内容计算哈希
        return hashlib.md5(str(content).encode('utf-8')).hexdigest()

    def get_news_filename(self, date=None):
        """获取指定日期的新闻文件名"""
        if date is None:
            date = datetime.now().strftime('%Y%m%d')
        else:
            date = date.strftime('%Y%m%d')
        return os.path.join(self.save_dir, f"news_{date}.json")

    def fetch_and_save(self, max_retries=3):
        """获取新闻并保存到JSON文件，避免重复内容"""
        for attempt in range(max_retries):
            try:
                # 获取当前时间
                now = datetime.now()

                # 检查是否连续失败过多
                if self.consecutive_failures >= self.max_failures:
                    logger.error(f"连续失败 {self.consecutive_failures} 次，暂停获取新闻")
                    return False

                # 调用AKShare API获取财联社电报数据
                logger.info(f"开始获取财联社电报数据 (尝试 {attempt + 1}/{max_retries})")
                
                # 添加请求间隔，避免频率过高
                if self.last_fetch_time:
                    time_diff = (now - self.last_fetch_time).total_seconds()
                    if time_diff < 30:  # 至少间隔30秒
                        wait_time = 30 - time_diff
                        logger.info(f"距离上次请求间隔过短，等待 {wait_time:.1f} 秒")
                        time.sleep(wait_time)

                stock_info_global_cls_df = ak.stock_info_global_cls(symbol="全部")

                if stock_info_global_cls_df.empty:
                    logger.warning("获取的财联社电报数据为空")
                    if attempt < max_retries - 1:
                        logger.info(f"数据为空，{5} 秒后重试...")
                        time.sleep(5)
                        continue
                    else:
                        self.consecutive_failures += 1
                        return False

                # 打印DataFrame的信息和类型，帮助调试
                logger.info(f"获取的数据形状: {stock_info_global_cls_df.shape}")
                logger.info(f"数据列: {stock_info_global_cls_df.columns.tolist()}")
                logger.info(f"数据类型: \n{stock_info_global_cls_df.dtypes}")

                # 计数器
                total_count = 0
                new_count = 0

                # 转换为列表字典格式并添加哈希值
                news_list = []
                for _, row in stock_info_global_cls_df.iterrows():
                    total_count += 1

                    # 安全获取内容，确保为字符串
                    content = str(row.get("内容", ""))

                    # 计算内容哈希值
                    content_hash = self._calculate_hash(content)

                    # 检查是否已存在相同内容的新闻
                    if content_hash in self.news_hashes:
                        continue  # 跳过已存在的新闻

                    # 添加新的哈希值到集合
                    self.news_hashes.add(content_hash)
                    new_count += 1

                    # 安全获取日期和时间，确保为字符串格式
                    pub_date = row.get("发布日期", "")
                    if isinstance(pub_date, (datetime, date)):
                        pub_date = pub_date.isoformat()
                    else:
                        pub_date = str(pub_date)

                    pub_time = row.get("发布时间", "")
                    if isinstance(pub_time, (datetime, date)):
                        pub_time = pub_time.isoformat()
                    else:
                        pub_time = str(pub_time)

                    # 创建新闻项并添加哈希值
                    news_item = {
                        "title": str(row.get("标题", "")),
                        "content": content,
                        "date": pub_date,
                        "time": pub_time,
                        "datetime": f"{pub_date} {pub_time}",
                        "fetch_time": now.strftime('%Y-%m-%d %H:%M:%S'),
                        "hash": content_hash  # 保存哈希值以便后续使用
                    }
                    news_list.append(news_item)

                # 如果没有新的新闻，直接返回
                if not news_list:
                    logger.info(f"没有新的新闻数据需要保存 (共检查 {total_count} 条)")
                    # 清理连续失败计数器
                    self.consecutive_failures = 0
                    self.last_fetch_time = now
                    return True

                # 获取文件名
                filename = self.get_news_filename()

                # 如果文件已存在，则合并新旧数据
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        try:
                            existing_data = json.load(f)
                            # 合并数据，已经确保news_list中的内容都是新的
                            merged_news = existing_data + news_list
                            # 按时间排序
                            merged_news.sort(key=lambda x: x['datetime'], reverse=True)
                        except json.JSONDecodeError:
                            logger.warning(f"文件 {filename} 格式错误，使用新数据替换")
                            merged_news = sorted(news_list, key=lambda x: x['datetime'], reverse=True)
                else:
                    # 如果文件不存在，直接使用新数据
                    merged_news = sorted(news_list, key=lambda x: x['datetime'], reverse=True)

                # 保存合并后的数据，使用自定义编码器处理日期
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(merged_news, f, ensure_ascii=False, indent=2, cls=DateEncoder)

                logger.info(f"成功保存 {new_count} 条新闻数据 (共检查 {total_count} 条，过滤重复 {total_count - new_count} 条)")
                
                # 清理连续失败计数器和更新时间
                self.consecutive_failures = 0
                self.last_fetch_time = now
                
                # 定期清理哈希值，防止内存泄漏
                self._cleanup_old_hashes()
                
                return True

            except Exception as e:
                logger.error(f"获取或保存新闻数据时出错 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                import traceback
                logger.error(traceback.format_exc())
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10  # 递增等待时间
                    logger.info(f"{wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    self.consecutive_failures += 1
                    logger.error(f"所有重试都失败了，连续失败次数: {self.consecutive_failures}")
                    return False
        
        return False

    def get_latest_news(self, days=1, limit=50):
        """获取最近几天的新闻数据，并去除重复项"""
        news_data = []
        today = datetime.now()
        # 记录已处理的日期，便于日志
        processed_dates = []

        # 获取指定天数内的所有新闻
        for i in range(days):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y%m%d')
            filename = self.get_news_filename(date)

            if os.path.exists(filename):
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        news_data.extend(data)
                        processed_dates.append(date_str)
                        logger.info(f"已加载 {date_str} 新闻数据 {len(data)} 条")
                except Exception as e:
                    logger.error(f"读取文件 {filename} 时出错: {str(e)}")
            else:
                logger.warning(f"日期 {date_str} 的新闻文件不存在: {filename}")

        # 排序前记录总数
        total_before_sort = len(news_data)

        # 去除重复项
        # 使用内容哈希或已有的哈希字段作为唯一标识
        unique_news = {}
        duplicate_count = 0

        for item in news_data:
            # 优先使用已有的哈希值，如果没有则计算内容哈希
            item_hash = item.get('hash')
            if not item_hash and 'content' in item:
                item_hash = self._calculate_hash(item['content'])

            # 如果是新的哈希值，则添加到结果中
            if item_hash and item_hash not in unique_news:
                unique_news[item_hash] = item
            else:
                duplicate_count += 1

        # 转换回列表并按时间排序
        deduplicated_news = list(unique_news.values())
        deduplicated_news.sort(key=lambda x: x.get('datetime', ''), reverse=True)

        # 限制返回条数
        result = deduplicated_news[:limit]

        logger.info(f"获取最近 {days} 天新闻(处理日期:{','.join(processed_dates)}), "
                    f"共 {total_before_sort} 条, 去重后 {len(deduplicated_news)} 条, "
                    f"移除重复 {duplicate_count} 条, 返回最新 {len(result)} 条")

        return result

# 单例模式的新闻获取器
news_fetcher = NewsFetcher()

def fetch_news_task():
    """执行新闻获取任务"""
    logger.info("开始执行新闻获取任务")
    news_fetcher.fetch_and_save()
    logger.info("新闻获取任务完成")

class NewsScheduler:
    """新闻获取定时任务调度器"""
    def __init__(self):
        self.is_running = False
        self.scheduler_thread = None
        self.stop_event = threading.Event()
        
    def start(self, interval_minutes=10):
        """启动定时任务"""
        if self.is_running:
            logger.warning("定时任务已在运行中")
            return
            
        self.is_running = True
        self.stop_event.clear()
        
        def _run_scheduler():
            logger.info(f"新闻获取定时任务已启动，间隔 {interval_minutes} 分钟")
            
            while not self.stop_event.is_set():
                try:
                    # 执行新闻获取任务
                    success = news_fetcher.fetch_and_save()
                    
                    if success:
                        logger.info("新闻获取任务执行成功")
                    else:
                        logger.warning("新闻获取任务执行失败")
                        
                    # 等待指定时间或直到收到停止信号
                    if self.stop_event.wait(timeout=interval_minutes * 60):
                        break  # 收到停止信号
                        
                except Exception as e:
                    logger.error(f"定时任务执行出错: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                    
                    # 出错后等待较短时间再试
                    if self.stop_event.wait(timeout=60):
                        break
            
            logger.info("新闻获取定时任务已停止")
            self.is_running = False

        # 创建并启动定时任务线程
        self.scheduler_thread = threading.Thread(target=_run_scheduler, name="NewsScheduler")
        self.scheduler_thread.daemon = False  # 不使用daemon线程，确保正常退出
        self.scheduler_thread.start()
        
    def stop(self):
        """停止定时任务"""
        if not self.is_running:
            logger.warning("定时任务未在运行")
            return
            
        logger.info("正在停止新闻获取定时任务...")
        self.stop_event.set()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=10)  # 等待最多10秒
            
        self.is_running = False
        logger.info("新闻获取定时任务已停止")
        
    def is_alive(self):
        """检查定时任务是否还在运行"""
        return self.is_running and self.scheduler_thread and self.scheduler_thread.is_alive()

# 全局调度器实例
news_scheduler = NewsScheduler()

def start_news_scheduler(interval_minutes=10):
    """启动新闻获取定时任务"""
    news_scheduler.start(interval_minutes)

def stop_news_scheduler():
    """停止新闻获取定时任务"""
    news_scheduler.stop()

# 初始获取一次数据
if __name__ == "__main__":
    fetch_news_task()