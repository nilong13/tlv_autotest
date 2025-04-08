import time
from pywinauto.timings import TimeoutError


class SmartWait:
    """基础智能等待实现"""

    def __init__(self, base_timeout=10.0, base_interval=0.5):
        """
        :param base_timeout: 基础超时时间（默认10秒）
        :param base_interval: 检查间隔（默认0.5秒）
        """
        self.base_timeout = base_timeout
        self.base_interval = base_interval

    def until_element_ready(self, control):
        """
        等待控件准备就绪（存在、可见、可操作）
        """
        end_time = time.time() + self.base_timeout
        while time.time() < end_time:
            if control.exists() and control.is_visible() and control.is_enabled():
                return True
            print("等待控件出现")
            time.sleep(self.base_interval)
        raise TimeoutError(f"控件 {control} 超时未就绪")
