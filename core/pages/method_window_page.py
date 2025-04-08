from pywinauto import ElementNotFoundError
from core.find_item import find_list_item
from core.pages.base_page import BasePage
from utils.retry import retry


class MethodWindowPage(BasePage):
    """方法调用窗口页面对象"""
    def _init_controls(self):
        # 核心控件定位
        self.method_combo = self.window.child_window(title="Method Name:", auto_id="1008", control_type="ComboBox")
        self.invoke_btn = self.window.child_window(title="Invoke", auto_id="1015", control_type="Button")
        self.return_value = self.window.child_window(title="Return Value:", auto_id="1016", control_type="Edit")
        self.close_btn = self.window.child_window(title="Close", auto_id="1", control_type="Button")
        self.list_box = self.window.app.window(title="Method Name:", control_type="List")

    def invoke_method(self, method_name, parameters):
        """执行完整方法调用流程"""
        self.logger.info(f"执行完整方法调用流程")
        self.select_method(method_name)
        self.set_parameters(parameters)
        self.execute_invoke()
        self.logger.info(f"完整方法调用流程执行完毕")
        return self

    @retry(max_attempts=5, exceptions=ElementNotFoundError)
    def select_method(self, method_name: str):
        """选择方法"""
        self.wait.until_element_ready(self.method_combo)
        self.logger.info(f"查找并选择方法 {method_name}")
        self.method_combo.expand()
        self.wait.until_element_ready(self.list_box)
        item = find_list_item(self.list_box, method_name)
        item.click_input()
        self.logger.info(f"方法 {method_name}已找到并选择")
        return self

    def set_parameters(self, parameters):
        """输入参数"""
        self.logger.info(f"开始输入参数")
        for param in parameters:
            ctrl = self.window.child_window(
                title="Parameter Value:",
                control_type="ComboBox" if isinstance(param, bool) else "Edit"
            )
            self.wait.until_element_ready(ctrl)  # 新增等待
            self.logger.debug(f"输入参数: {str(param)}")
            ctrl.type_keys(str(param))
            self.window.child_window(title="Set Value", auto_id="1013", control_type="Button").click()
        self.logger.info(f"参数输入完毕")
        return self

    def execute_invoke(self):
        """执行调用"""
        self.logger.info(f"执行调用")
        self.wait.until_element_ready(self.invoke_btn)
        self.invoke_btn.click()
        return self  # 保持当前页面上下文

    def get_property(self, prop):
        if prop == "return_value":
            return self.return_value.get_value()

    def close_method(self):
        self.logger.info(f"关闭方法窗口")
        self.wait.until_element_ready(self.close_btn)
        self.close_btn.click()


