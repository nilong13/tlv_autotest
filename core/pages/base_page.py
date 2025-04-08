import logging
from pywinauto import timings
from core.wait_strategy import SmartWait


class BasePage:
    """页面对象基类"""

    def __init__(self, app_window):
        self.window = app_window

        logger_name = f"{self.__class__.__name__}"
        self.logger = logging.getLogger(logger_name)
        self.logger.debug(f"初始化页面对象: {logger_name}")

        self.wait = SmartWait(base_timeout=10)
        self._init_controls()
        self.logger.debug(f"页面对象: {logger_name}初始化成功")

    def _init_controls(self):
        """控件初始化(子类实现)"""
        raise NotImplementedError("子类必须实现控件初始化")

    def get_state(self) -> bool:
        """增强窗口状态检测"""
        try:
            return (
                self.window.exists()
                and self.window.is_visible()
                and self.window.is_enabled()
            )
        except timings.TimeoutError:
            return False
