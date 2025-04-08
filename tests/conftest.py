import shutil
import time
from pathlib import Path
import pytest
from core.tlv_app import TLVApp
from utils.logger_config import default_logger as logger, default_allure_handler as allure_handler


@pytest.fixture(scope="session", autouse=True)
def init_logger():
    logger.info("===== 测试会话开始 =====")

def pytest_runtest_teardown(item, nextitem):
    """在每个测试用例结束后刷新日志"""
    allure_handler.flush()

@pytest.fixture(scope="session", autouse=True)
def clean_global_screenshots():
    """全局截图目录清理（整个测试运行只执行一次）"""
    base_dir = Path("logs/screenshots")
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)

@pytest.fixture(scope="function")
def app():
    """应用实例fixture"""
    app = TLVApp()
    app.insert_control("TLV Control")
    # app.resize_window()
    yield app
    time.sleep(1)
    app.close()
    time.sleep(3)

@pytest.fixture
def method_window(app):
    """方法窗口fixture"""
    window = app.main_page.open_method_window()
    yield window
