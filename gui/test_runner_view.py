from PyQt5.QtWidgets import (QMainWindow, QTreeWidget, QTreeWidgetItem,
                             QPushButton, QVBoxLayout, QHBoxLayout, QWidget,
                             QLabel, QSplitter, QPlainTextEdit, QMessageBox,
                             QStatusBar, QAction, QMenu, QShortcut, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QTextCursor, QKeySequence, QIcon
import subprocess
import os
import logging

# 配置日志记录器
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LogBuffer:
    """日志缓冲区，用于提高日志显示性能"""
    def __init__(self, text_widget, max_lines=1000, update_interval=100):
        self.text_widget = text_widget
        self.max_lines = max_lines
        self.buffer = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.flush)
        self.timer.start(update_interval)  # 每100毫秒更新一次
        self.auto_scroll = True

    def append(self, text):
        self.buffer.append(text)
        # 如果缓冲区过大，立即刷新
        if len(self.buffer) > 20:
            self.flush()

    def flush(self):
        if not self.buffer:
            return

        # 保存当前光标位置和选择
        cursor = self.text_widget.textCursor()
        current_position = cursor.position()
        anchor_position = cursor.anchor()

        # 将缓冲区中的所有文本一次性添加到文本控件
        text = "\n".join(self.buffer)
        self.text_widget.appendPlainText(text)
        self.buffer.clear()

        # 限制显示的行数
        document = self.text_widget.document()
        if document.blockCount() > self.max_lines:
            remove_cursor = QTextCursor(document.findBlockByNumber(0))
            remove_cursor.select(QTextCursor.BlockUnderCursor)
            remove_cursor.removeSelectedText()
            remove_cursor.deleteChar()  # 删除换行符

        # 恢复光标位置和选择
        cursor.setPosition(anchor_position)
        cursor.setPosition(current_position, QTextCursor.KeepAnchor)
        self.text_widget.setTextCursor(cursor)

        # 如果启用了自动滚动，则滚动到底部
        if self.auto_scroll:
            self.text_widget.moveCursor(QTextCursor.End)

    def toggle_auto_scroll(self):
        self.auto_scroll = not self.auto_scroll
        return self.auto_scroll

class TestRunnerView(QMainWindow):
    item_changed = pyqtSignal(QTreeWidgetItem, int)
    run_tests_signal = pyqtSignal()
    select_all_signal = pyqtSignal()
    deselect_all_signal = pyqtSignal()
    open_report_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.log_buffer = None  # 初始化为None，在init_ui中创建
        self.status_bar = self.statusBar()
        self.init_ui()
        self.setup_shortcuts()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle('TLV 自动化测试工具')
        self.setGeometry(100, 100, 1200, 800)

        # 创建菜单栏
        self.create_menu_bar()

        # 创建状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage('就绪')

        # 创建中心部件和主布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # 创建水平分割器（左右分割）
        h_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(h_splitter)

        # 创建左侧部件（用例树和按钮）
        left_widget = self.create_left_panel()
        h_splitter.addWidget(left_widget)

        # 创建右侧部件（状态和日志）
        right_widget = self.create_right_panel()
        h_splitter.addWidget(right_widget)

        # 设置分割器的初始大小
        h_splitter.setSizes([400, 800])

    def create_menu_bar(self):
        """创建菜单栏"""
        menu_bar = self.menuBar()

        # 文件菜单
        file_menu = menu_bar.addMenu('文件')

        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 测试菜单
        test_menu = menu_bar.addMenu('测试')

        run_action = QAction('运行测试', self)
        run_action.setShortcut('F5')
        run_action.triggered.connect(self.run_tests_signal.emit)
        test_menu.addAction(run_action)

        select_all_action = QAction('全选', self)
        select_all_action.setShortcut('Ctrl+A')
        select_all_action.triggered.connect(self.select_all_signal.emit)
        test_menu.addAction(select_all_action)

        deselect_all_action = QAction('取消全选', self)
        deselect_all_action.setShortcut('Ctrl+D')
        deselect_all_action.triggered.connect(self.deselect_all_signal.emit)
        test_menu.addAction(deselect_all_action)

        # 帮助菜单
        help_menu = menu_bar.addMenu('帮助')

        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_left_panel(self):
        """创建左侧面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 用例树标签
        top_label = QLabel('测试用例：')
        left_layout.addWidget(top_label)

        # 用例树
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(['测试用例'])
        self.tree_widget.setColumnWidth(0, 300)
        self.tree_widget.itemChanged.connect(self.item_changed.emit)
        self.tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.show_tree_context_menu)
        left_layout.addWidget(self.tree_widget)

        # 按钮布局
        button_layout = QHBoxLayout()

        self.select_all_btn = QPushButton('全选')
        self.select_all_btn.clicked.connect(self.select_all_signal.emit)
        button_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton('取消全选')
        self.deselect_all_btn.clicked.connect(self.deselect_all_signal.emit)
        button_layout.addWidget(self.deselect_all_btn)

        self.run_btn = QPushButton('执行用例')
        self.run_btn.clicked.connect(self.run_tests_signal.emit)
        button_layout.addWidget(self.run_btn)

        left_layout.addLayout(button_layout)
        return left_widget

    def create_right_panel(self):
        """创建右侧面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 创建垂直分割器（上下分割）
        v_splitter = QSplitter(Qt.Vertical)
        right_layout.addWidget(v_splitter)

        # 上部状态显示
        self.status_display = QPlainTextEdit()
        self.status_display.setReadOnly(True)
        self.status_display.setMaximumHeight(100)
        self.status_display.setFont(QFont("Consolas", 10))
        # 启用文本选择和复制
        self.status_display.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        v_splitter.addWidget(self.status_display)

        # 下部日志显示
        self.log_display = QPlainTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        # 启用文本选择
        self.log_display.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        # 确保能够接收鼠标事件
        self.log_display.viewport().setCursor(Qt.IBeamCursor)
        # 设置右键菜单策略
        self.log_display.setContextMenuPolicy(Qt.CustomContextMenu)
        self.log_display.customContextMenuRequested.connect(self.show_log_context_menu)
        v_splitter.addWidget(self.log_display)

        # 创建日志缓冲区
        self.log_buffer = LogBuffer(self.log_display, max_lines=2000, update_interval=100)

        # 创建底部按钮布局
        bottom_layout = QHBoxLayout()

        # 添加自动滚动切换按钮
        self.auto_scroll_btn = QPushButton("自动滚动: 开")
        self.auto_scroll_btn.clicked.connect(self.toggle_auto_scroll)
        bottom_layout.addWidget(self.auto_scroll_btn)

        # 添加打开Allure报告按钮
        self.open_report_btn = QPushButton("打开Allure报告")
        self.open_report_btn.clicked.connect(self.open_report_signal.emit)
        bottom_layout.addWidget(self.open_report_btn)

        right_layout.addLayout(bottom_layout)

        # 设置分割器的初始大小
        v_splitter.setSizes([100, 500])
        return right_widget

    def setup_shortcuts(self):
        """设置键盘快捷键"""
        # F5 运行测试
        run_shortcut = QShortcut(QKeySequence("F5"), self)
        run_shortcut.activated.connect(self.run_tests_signal.emit)

        # Ctrl+A 全选
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        select_all_shortcut.activated.connect(self.select_all_signal.emit)

        # Ctrl+D 取消全选
        deselect_all_shortcut = QShortcut(QKeySequence("Ctrl+D"), self)
        deselect_all_shortcut.activated.connect(self.deselect_all_signal.emit)

        # Ctrl+Shift+C 切换自动滚动
        toggle_scroll_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        toggle_scroll_shortcut.activated.connect(self.toggle_auto_scroll)

    def show_tree_context_menu(self, position):
        """显示树形控件的上下文菜单"""
        menu = QMenu()

        select_action = menu.addAction("选择")
        deselect_action = menu.addAction("取消选择")

        action = menu.exec_(self.tree_widget.mapToGlobal(position))

        if action == select_action:
            items = self.tree_widget.selectedItems()
            for item in items:
                item.setCheckState(0, Qt.Checked)
        elif action == deselect_action:
            items = self.tree_widget.selectedItems()
            for item in items:
                item.setCheckState(0, Qt.Unchecked)

    def show_log_context_menu(self, position):
        """显示日志控件的上下文菜单"""
        menu = QMenu()

        clear_action = menu.addAction("清除")
        toggle_scroll_action = menu.addAction("切换自动滚动")

        action = menu.exec_(self.log_display.mapToGlobal(position))

        if action == clear_action:
            self.log_display.clear()
        elif action == toggle_scroll_action:
            self.toggle_auto_scroll()

    def toggle_auto_scroll(self):
        is_auto_scroll = self.log_buffer.toggle_auto_scroll()
        self.auto_scroll_btn.setText(f"自动滚动: {'开' if is_auto_scroll else '关'}")

    def show_about(self):
        """显示关于对话框"""
        title = "关于"
        content = (
            "TLV 自动化测试工具\n\n"
            "版本: 1.0.0\n"
            "这是一个用于TLV自动化测试的GUI工具"
        )
        QMessageBox.about(self, title, content)

    def load_case_structure(self, case_structure):
        self.tree_widget.clear()
        for module, case_names in case_structure.items():
            module_item = QTreeWidgetItem(self.tree_widget)
            module_item.setText(0, module)
            module_item.setFlags(module_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsAutoTristate)
            module_item.setCheckState(0, Qt.Unchecked)

            for case_name in case_names:
                case_item = QTreeWidgetItem(module_item)
                case_item.setText(0, case_name)
                case_item.setFlags(case_item.flags() | Qt.ItemIsUserCheckable)
                case_item.setCheckState(0, Qt.Unchecked)

        self.tree_widget.expandAll()

    def select_all_items(self):
        root = self.tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            module_item = root.child(i)
            module_item.setCheckState(0, Qt.Checked)

    def deselect_all_items(self):
        root = self.tree_widget.invisibleRootItem()
        for i in range(root.childCount()):
            module_item = root.child(i)
            module_item.setCheckState(0, Qt.Unchecked)

    def update_status(self, message):
        self.status_display.appendPlainText(message)
        self.status_display.moveCursor(QTextCursor.End)

    def append_log(self, message):
        if self.log_buffer:
            self.log_buffer.append(message)
        else:
            # 如果缓冲区未初始化，直接添加到日志显示
            self.log_display.appendPlainText(message)
            self.log_display.moveCursor(QTextCursor.End)

    def clear_status(self):
        self.status_display.clear()

    def clear_log(self):
        self.log_display.clear()

    def show_warning(self, title, message):
        QMessageBox.warning(self, title, message)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def show_info(self, title, message):
        QMessageBox.information(self, title, message)

    def create_timer(self):
        return QTimer(self)

    def closeEvent(self, event):
        """关闭窗口时的事件处理"""
        # 刷新日志缓冲区
        if self.log_buffer:
            self.log_buffer.flush()
        event.accept()

    def open_allure_report(self):
        """打开Allure报告"""
        try:
            # 使用allure serve命令启动一个HTTP服务器来显示报告
            temps_dir = os.path.join(os.getcwd(), 'temps')  # 原始结果目录

            if os.path.exists(temps_dir) and os.listdir(temps_dir):
                # 使用子进程启动allure serve，不阻塞主线程
                self.status_display.appendPlainText("正在启动Allure报告服务器...")

                # 使用cmd来运行allure命令
                cmd = f'start cmd /c "allure serve {temps_dir}"'
                subprocess.Popen(cmd, shell=True)

                self.show_info(
                    "报告已打开",
                    "Allure报告服务器已启动，报告将在浏览器中自动打开。\n"
                    "服务器将在浏览器关闭后自动关闭。"
                )
            else:
                self.show_warning(
                    "报告数据不存在",
                    "Allure报告原始数据不存在。\n"
                    "请确保测试已执行完成并成功生成报告。\n"
                    f"期望的报告数据目录: {temps_dir}"
                )
                logging.debug(f"尝试打开报告失败，报告数据目录不存在或为空: {temps_dir}")
        except Exception as e:
            self.show_error("打开报告失败", f"无法打开Allure报告: {str(e)}")
            logging.error(f"打开报告失败: {str(e)}", exc_info=True)