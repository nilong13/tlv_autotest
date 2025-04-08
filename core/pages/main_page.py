from core.pages.base_page import BasePage
from core.set_size import set_size


class MainPage(BasePage):
    """主界面页面对象"""
    def _init_controls(self):
        # 菜单项定位
        self.max_btn = self.window.child_window(title="最大化", control_type="Button")
        self.close_btn = self.window.child_window(title="关闭", control_type="Button")

    def open_insert_control(self) -> 'InsertControlPage':  # 使用字符串类型提示
        """打开插入控件窗口"""
        from core.pages.insert_control_page import InsertControlPage
        self.logger.info("打开插入控件窗口")
        self.window.menu_select("Edit->Insert New Control")
        insert_dlg = self.window.child_window(title="Insert Control", control_type="Window")
        self.wait.until_element_ready(insert_dlg)
        self.logger.info("插入控件窗口打开成功")
        return InsertControlPage(insert_dlg)

    def open_method_window(self) -> 'MethodWindowPage':
        """打开方法调用窗口"""
        from core.pages.method_window_page import MethodWindowPage
        self.logger.info("打开方法调用窗口")
        self.window.menu_select("Control->Invoke Methods")
        method_wnd = self.window.child_window(title="Invoke Methods", control_type="Window")
        self.wait.until_element_ready(method_wnd)
        self.logger.info("方法调用窗口打开成功")
        return MethodWindowPage(method_wnd)

    def set_window(self):
        self.maximize_window()
        self.adjust_layout()

    def maximize_window(self):
        self.wait.until_element_ready(self.max_btn)  # 新增等待
        self.max_btn.click()

    def adjust_layout(self):
        """调整控件布局"""
        self.logger.info("调整控件布局")
        pane = self.window["Pane4"]
        self.wait.until_element_ready(pane)  # 新增等待
        edit_down = self.window.child_window(auto_id="59664", control_type="Edit")
        set_size(edit_down, 0, (0, 300))
        set_size(pane, 7, (1000, 600))
        self.logger.info("控件布局调整完成")

    def close(self):
        self.wait.until_element_ready(self.close_btn)
        self.logger.info("关闭主页面")
        self.close_btn.click()
