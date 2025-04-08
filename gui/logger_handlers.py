import logging

class QTextEditLogger(logging.Handler):
    """将日志重定向到QTextEdit的自定义日志处理器"""
    def __init__(self, signal):
        """
        初始化日志处理器

        Args:
            signal: PyQt信号，用于发送日志消息到GUI
        """
        super().__init__()
        self.signal = signal
        self.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)-8s] %(filename)s:%(lineno)d - %(message)s'
        ))

    def emit(self, record):
        """
        发出日志记录

        Args:
            record: 日志记录对象
        """
        msg = self.format(record)
        self.signal.emit(msg)