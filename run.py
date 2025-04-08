import sys
import pytest
import logging
import argparse
import subprocess
from PyQt5.QtWidgets import QApplication
from gui.test_runner_controller import TestRunnerController
from utils.data_loader import load_independent_cases
from utils.logger_config import configure_logger
from tests import test_suite

def setup_logging(log_level=logging.DEBUG):
    """设置日志系统"""
    # 配置日志
    root_logger, _, log_file = configure_logger(log_level=log_level)
    logging.info(f"日志文件路径: {log_file}")
    return root_logger

def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='TLV 自动化测试工具')
    parser.add_argument('--cli', action='store_true', help='在命令行模式下运行')
    parser.add_argument('--no-report', action='store_true', help='不生成报告')

    return parser.parse_args()

def run_tests(args):
    """运行测试"""
    # 设置 CASES 变量
    test_suite.CASES.clear()
    test_suite.CASES.extend(load_independent_cases())

    # 运行测试，使用 pytest.ini 中的配置
    logging.info("运行测试: pytest")

    pytest_result = pytest.main([])

    if pytest_result != 0:
        logging.warning(f"测试执行完成，但存在失败的测试，返回码: {pytest_result}")

    # 生成报告
    if not args.no_report:
        generate_report()

    return pytest_result

def generate_report():
    """生成测试报告"""
    logging.info("生成测试报告")
    try:
        # 使用subprocess替代os.system
        result = subprocess.run(
            ["allure", "generate", "--clean"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            logging.info("报告生成成功")
        else:
            logging.error(f"报告生成失败: {result.stderr}")

    except FileNotFoundError:
        logging.error("未找到allure命令，请确保已正确安装allure")
    except Exception as e:
        logging.error(f"生成报告时出错: {str(e)}", exc_info=True)

def run_gui_mode():
    """运行GUI模式"""
    logging.info("以GUI模式运行")
    app = QApplication(sys.argv)
    controller = TestRunnerController()
    controller.view.show()
    return app.exec_()

def main():
    """主函数"""
    args = parse_arguments()

    # 设置日志级别
    setup_logging()

    try:
        if args.cli:
            # 命令行模式
            logging.info("以命令行模式运行")
            result = run_tests(args)
            sys.exit(result)
        else:
            # GUI模式
            exit_code = run_gui_mode()
            sys.exit(exit_code)
    except Exception as e:
        logging.error(f"运行时出错: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()