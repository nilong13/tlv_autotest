import logging
import sys
from pathlib import Path
import allure
from io import StringIO

class AllureLogHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.log_buffer = StringIO()

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_buffer.write(msg + '\n')
        except Exception as e:
            sys.stderr.write(f"Allure日志错误: {str(e)}")

    def flush(self):
        log_content = self.log_buffer.getvalue()
        if log_content:
            allure.attach(log_content, "Runtime Log", allure.attachment_type.TEXT)
        self.log_buffer.truncate(0)
        self.log_buffer.seek(0)

def configure_logger(log_level=logging.DEBUG, log_file='tlv_auto.log', log_dir='logs'):
    """配置根记录器"""
    logger = logging.getLogger()

    # 重置已存在的配置
    if logger.handlers:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    logger.setLevel(log_level)

    # 创建日志目录
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 统一格式
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 文件处理器
    file_handler = logging.FileHandler(log_dir / log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)

    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)

    # Allure处理器
    allure_handler = AllureLogHandler()
    allure_handler.setLevel(log_level)
    allure_handler.setFormatter(formatter)

    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.addHandler(allure_handler)

    return logger, allure_handler, str(log_dir / log_file)  # 返回logger、allure_handler和日志文件路径

# 默认配置
default_logger, default_allure_handler, default_log_file = configure_logger()
