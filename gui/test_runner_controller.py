import pytest
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer, Qt
from PyQt5.QtWidgets import QApplication
from gui.test_runner_model import TestRunnerModel
from gui.test_runner_view import TestRunnerView
from gui.logger_handlers import QTextEditLogger
from tests import test_suite
from utils.logger_config import configure_logger

class TestRunnerController(QObject):
    class TestSignals(QObject):
        test_completed = pyqtSignal(bool, str, int)
        status_update = pyqtSignal(str)
        log_update = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.model = TestRunnerModel()
        self.view = TestRunnerView()
        self.signals = self.TestSignals()
        self.thread_pool = ThreadPoolExecutor(max_workers=1)
        self.current_test_future = None
        self.gui_handler = None

        self.connect_signals()
        self.setup_logging()
        self.load_case_structure()

    def __del__(self):
        """清理资源"""
        if self.gui_handler:
            root_logger = logging.getLogger()
            root_logger.removeHandler(self.gui_handler)

        if hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=True)

    def connect_signals(self):
        """连接所有信号和槽"""
        self.view.item_changed.connect(self.on_item_changed)
        self.view.run_tests_signal.connect(self.run_tests)
        self.view.select_all_signal.connect(self.select_all)
        self.view.deselect_all_signal.connect(self.deselect_all)
        self.view.open_report_signal.connect(self.view.open_allure_report)
        self.signals.test_completed.connect(self.handle_test_completion)
        self.signals.status_update.connect(self.view.update_status)
        self.signals.log_update.connect(self.view.append_log)

    def setup_logging(self):
        """设置日志系统"""
        # 配置根日志记录器
        root_logger, _, _ = configure_logger()

        # 添加自定义处理器，将日志重定向到GUI
        self.gui_handler = QTextEditLogger(self.signals.log_update)
        self.gui_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(self.gui_handler)

        logging.info("日志系统初始化完成")

    def load_case_structure(self):
        """加载测试用例结构"""
        case_structure = self.model.load_case_structure()
        self.view.load_case_structure(case_structure)

    def on_item_changed(self, item, column):
        """处理测试用例选择状态改变"""
        if item.parent() is None:
            # 处理父节点（模块）的改变
            module = item.text(0)
            check_state = item.checkState(0)
            for i in range(item.childCount()):
                case_item = item.child(i)
                case_name = case_item.text(0)
                self.model.update_selected_cases(module, case_name, check_state == Qt.Checked)
        else:
            # 处理子节点（测试用例）的改变
            module = item.parent().text(0)
            case_name = item.text(0)
            check_state = item.checkState(0)
            self.model.update_selected_cases(module, case_name, check_state == Qt.Checked)

    def select_all(self):
        """选择所有测试用例"""
        case_structure = self.model.load_case_structure()
        self.model.select_all_cases(case_structure)
        self.view.select_all_items()

    def deselect_all(self):
        """取消选择所有测试用例"""
        self.model.deselect_all_cases()
        self.view.deselect_all_items()

    def run_tests(self):
        """运行选中的测试用例"""
        if not self.model.selected_cases:
            self.view.show_warning('警告', '请至少选择一个测试用例')
            return

        if self.current_test_future and not self.current_test_future.done():
            self.view.show_warning('警告', '测试正在执行中，请等待当前测试完成')
            return

        try:
            # 清空状态和日志显示
            self.view.clear_status()
            self.view.clear_log()

            # 获取选中的用例
            cases = self.model.get_selected_cases()
            test_suite.CASES.clear()
            test_suite.CASES.extend(cases)

            # 显示正在执行的状态
            selected_cases_info = ", ".join([
                f"{module}:{case}"
                for module, cases_list in self.model.selected_cases.items()
                for case in cases_list
            ])
            self.signals.status_update.emit(f"正在执行测试用例: {selected_cases_info}")

            # 使用线程池执行测试
            self.current_test_future = self.thread_pool.submit(self.run_test_thread)

        except Exception as e:
            self.view.show_error('错误', f'执行测试时出错: {str(e)}')
            logging.error(f"执行测试时出错: {str(e)}", exc_info=True)

    def run_test_thread(self):
        """在独立线程中运行测试"""
        try:
            # 运行测试
            self.signals.status_update.emit("测试执行中...")
            logging.info("开始执行测试用例")

            # 运行pytest，不捕获其输出
            pytest_result = pytest.main(['--capture=no', '-v', 'tests/test_suite.py'])

            if pytest_result == 0:  # 测试成功
                # 生成报告
                self.signals.status_update.emit("生成测试报告...")

                # 使用subprocess替代os.system，更安全和可控
                try:
                    result = subprocess.run(
                        ["allure", "generate", "./temps", "-o", "./reports/allure-results", "--clean"],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    if result.stdout:
                        logging.info(result.stdout)
                    if result.stderr:
                        logging.warning(result.stderr)
                except subprocess.CalledProcessError as e:
                    logging.error(f"生成报告失败: {str(e)}")
                except FileNotFoundError:
                    logging.error("未找到allure命令，请确保已正确安装allure")

                # 完成测试
                self.signals.test_completed.emit(True, "测试完成", len(self.model.get_selected_cases()))
            else:
                error_msg = "测试执行失败，请查看日志了解详细信息"
                logging.error(error_msg)
                self.signals.test_completed.emit(False, error_msg, 0)

        except Exception as e:
            logging.error(f"测试执行失败: {str(e)}", exc_info=True)
            self.signals.test_completed.emit(False, str(e), 0)

    @pyqtSlot(bool, str, int)
    def handle_test_completion(self, success, message, case_count):
        """处理测试完成的回调"""
        if success:
            status_msg = f"测试完成: 成功执行了 {case_count} 个测试用例"
            self.signals.status_update.emit(status_msg)
            logging.info(f"成功执行了 {case_count} 个测试用例，报告已生成在 ./reports/allure-results 目录")
            # 提示用户可以查看报告
            self.view.show_info("测试完成", "测试执行完成，您可以点击'打开Allure报告'按钮查看详细报告。")
        else:
            status_msg = f"测试失败: {message}"
            self.signals.status_update.emit(status_msg)
            logging.error(f"测试执行失败: {message}")

        QApplication.processEvents()