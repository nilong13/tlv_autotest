import logging
from datetime import datetime
from pathlib import Path
from io import BytesIO
import allure
from pywinauto.findwindows import ElementNotFoundError


logger = logging.getLogger("utils.screenshot")


def take_screenshot(window, suffix=None, screenshot_dir="logs/screenshots"):
    """窗口截图工具（修正版）"""
    logger.debug(f"开始截图操作，后缀参数: {suffix}")
    try:
        # 检查窗口状态
        if not window.is_visible():
            logger.warning("窗口不可见，尝试等待可见状态")
            window.wait("visible", timeout=5)

        # 创建目录
        dir_path = Path(screenshot_dir)
        dir_path.mkdir(parents=True, exist_ok=True)

        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}"
        if suffix:
            filename += f"_{suffix.replace(' ', '_')}"
        filename += ".png"

        # 保存截图到本地
        img = window.capture_as_image()
        img.save(str(dir_path / filename))

        # 附加到Allure报告
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        allure.attach(
            buffer.getvalue(),
            name=f"Screenshot: {suffix}" if suffix else "操作截图",
            attachment_type=allure.attachment_type.PNG
        )
        return str(dir_path / filename)
    except ElementNotFoundError:
        error_msg = "截图失败：目标窗口未找到"
        allure.attach(error_msg, name="SCREENSHOT_ERROR", attachment_type=allure.attachment_type.TEXT)
        raise
    except Exception as e:
        logger.error(f"截图失败: {str(e)}", exc_info=True)
        error_msg = f"截图失败：{str(e)}"
        allure.attach(error_msg, name="SCREENSHOT_ERROR", attachment_type=allure.attachment_type.TEXT)
        raise
