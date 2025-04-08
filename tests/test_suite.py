import pytest
import allure
from utils.data_loader import load_independent_cases
from utils.screenshot import take_screenshot

# 模块级别的CASES变量
CASES = []

def setup_module(module):
    """模块级别的设置，在所有测试开始前运行一次"""
    global CASES
    if not CASES:
        CASES.extend(load_independent_cases())

@allure.feature("TLV独立用例测试套件")
class TestTLVSuite:

    @pytest.mark.parametrize("case", CASES, ids=lambda c: f"{c.get('_meta', {}).get('path', 'unknown')}::{c.get('id', 'unknown')}" if isinstance(c, dict) else str(c))
    @allure.title("独立用例 - {case[id]}")  # 动态设置用例标题
    @allure.story("核心业务流程验证")
    def test_case(self, app, method_window, case):
        """独立用例执行器（集成Allure报告）"""
        # 添加用例元数据
        allure.dynamic.description(f"用例路径: {case['_meta']['path']}\n用例描述: {case.get('description', '')}")
        allure.dynamic.tag(case.get('category', '未分类'))

        for step_idx, step in enumerate(case['steps']):
            step_title = f"步骤 {step_idx + 1}: {step['method']}"
            with allure.step(step_title):
                # 执行方法调用
                if not method_window.get_state():
                    app.main_page.open_method_window()
                method_window.invoke_method(step['method'], step.get('params', []))

                # 添加参数详情
                params_str = ", ".join(map(str, step.get('params', [])))
                allure.attach(
                    name="调用参数",
                    body=f"Method: {step['method']}\nParams: [{params_str}]",
                    attachment_type=allure.attachment_type.TEXT
                )

                # 执行验证
                with allure.step("✓ 验证结果"):
                    for validation in step['validations']:
                        actual = method_window.get_property(validation['property'])
                        expected = validation['expected']

                        # 添加断言上下文
                        with allure.step(f"验证属性 {validation['property']}"):
                            allure.attach(
                                f"预期值: {expected}\n实际值: {actual}",
                                name="验证详情",
                                attachment_type=allure.attachment_type.TEXT
                            )
                            # 断言前截图
                            take_screenshot(
                                method_window.window,
                                suffix=f"{case['id']}_step{step_idx}_validation"
                            )
                            assert str(actual) == str(expected), (
                                f"属性验证失败: {validation['property']}\n"
                                f"预期: {expected}\n实际: {actual}"
                            )

                    # 条件关闭处理
                    if step.get('close_after', False):
                        with allure.step("验证画面变动"):
                            method_window.close_method()
                            take_screenshot(
                                app.main_window,
                                suffix=f"{case['id']}_{step_idx}_xdg"
                            )
