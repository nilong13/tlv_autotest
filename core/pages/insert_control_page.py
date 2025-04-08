from core.find_item import find_list_item
from core.pages.base_page import BasePage


class InsertControlPage(BasePage):
    """插入控件窗口页面对象"""
    def _init_controls(self):
        # 控件定位
        self.control_list = self.window.child_window(auto_id="1053", control_type="List")
        self.ok_btn = self.window.child_window(title="OK", auto_id="1", control_type="Button")

    def select_control(self, control_name: str):
        """选择指定控件"""
        self.logger.info(f"正在查找控件: {control_name}")
        self.wait.until_element_ready(self.control_list)
        target_item = find_list_item(self.control_list, control_name)
        target_item.click_input()
        self.logger.info(f"控件: {control_name}查找并选择")
        return self  # 支持链式调用

    def confirm_selection(self):
        """确认选择"""
        self.wait.until_element_ready(self.ok_btn)
        self.logger.info(f"关闭插入控件的窗口")
        self.ok_btn.click()

