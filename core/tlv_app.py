import logging
import platform
from pathlib import Path
from pywinauto import Application
from core.pages.main_page import MainPage
from utils.data_loader import read_yaml


class TLVApp:
    """TLV应用入口"""
    def __init__(self):
        self.logger = logging.getLogger(__name__)  # 自动继承根配置
        self.logger.info("TLV应用实例初始化开始")

        config = read_yaml("configs/settings.yaml")
        system = platform.system()
        exe_path = Path(config['paths']['tlv_exe'][system.lower()])
        if not exe_path.exists():
            raise FileNotFoundError(f"TLV可执行文件未找到: {exe_path}")

        self.app = Application(backend="uia").start(str(exe_path))
        self.main_window = self.app.window(title="Untitled - ActiveX Control Test Container", control_type="Window")
        self.main_page = MainPage(self.main_window)

    def insert_control(self, control_name: str) -> MainPage:
        """插入控件流程(使用Page Object)"""
        self.logger.info(f"正在进行控件: {control_name} 插入流程")
        self.main_page.open_insert_control().select_control(control_name).confirm_selection()
        self.logger.info(f"控件 {control_name} 插入流程结束")
        return

    def insert_method(self, method, params):
        self.logger.info(f"正在调用方法: {method}")
        self.main_page.open_method_window().invoke_method(method, params)
        self.logger.info(f"方法: {method} 调用成功")
        return

    def resize_window(self):
        self.main_page.set_window()

    def close(self):
        self.main_page.close()

