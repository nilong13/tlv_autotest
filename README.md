```markdown
# TLV 自动化测试框架

基于 Python 和 PyWinAuto 的 GUI 自动化测试框架，专为 TLV 应用程序的核心业务流程验证设计，集成 Allure 测试报告和可视化测试运行器。

![框架架构](docs/images/framework-structure.png)

## 核心特性 ✨

- **跨平台支持** - 兼容 Windows 系统（通过 PyWinAuto）
- **动态用例管理** - YAML 驱动的测试用例配置
- **智能元素定位** - 自动重试机制和滚动查找算法
- **Allure 集成** - 美观的测试报告生成
- **可视化测试运行器** - 基于 PyQt5 的 GUI 控制台
- **实时日志系统** - 多端日志记录（控制台/文件/Allure）
- **自动截图追踪** - 关键操作步骤自动截图

## 环境要求 💻

- Python 3.8+
- TLV 应用程序（64位/32位）
- Windows 10/11 操作系统
- 推荐显示器分辨率：1920×1080

## 快速开始 🚀

```bash
# 克隆仓库
git clone https://github.com/yourusername/tlv-autotest-framework.git

# 安装依赖
pip install -r requirements.txt

# 运行GUI测试运行器
python gui/main.py
```

## 项目配置 ⚙️

1. **应用程序路径配置** (`configs/settings.yaml`)
```yaml
paths:
  tlv_exe:
    windows: "D:/Software/tlv/64位/tlv_app.exe"
```

2. **测试用例配置示例** (`tests/cases/demo_case.yaml`)
```yaml
id: "BASE-001"
description: "窗口基本操作验证"
steps:
  - method: "ResizeWindow"
    params: [800, 600]
    validations:
      - property: "window_size"
        expected: "(800, 600)"
```

## 目录结构 📁

```
├── configs/              # 配置文件
├── core/                 # 核心框架组件
│   ├── pages/            # 页面对象模型
│   └── tlv_app.py        # 应用控制入口
├── tests/                # 测试相关
│   ├── cases/            # YAML 测试用例
│   └── test_suite.py     # 测试执行器
├── utils/                # 工具模块
│   ├── data_loader.py    # 数据加载器
│   └── screenshot.py     # 截图工具
├── gui/                  # 图形界面
├── docs/                 # 文档资源
└── requirements.txt      # 依赖清单
```

## 核心功能演示 🎥

### 测试用例执行
```python
@allure.story("核心业务流程验证")
def test_payment_flow(app):
    app.main_page.open_payment_window()
    app.payment_page.process_transaction(amount=100)
    assert app.payment_page.get_status() == "SUCCESS"
```

### 可视化报告样例
![Allure 报告示例](docs/images/allure-report-demo.png)

## 贡献指南 🤝

欢迎通过 Issue 提交建议或通过 PR 参与开发：
1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/awesome-feature`)
3. 提交修改 (`git commit -am 'Add awesome feature'`)
4. 推送分支 (`git push origin feature/awesome-feature`)
5. 创建 Pull Request

## 许可协议 📜

本项目采用 MIT 许可协议 - 详情请参阅 [LICENSE](LICENSE) 文件
```

该 README 包含以下增强要素：

1. 结构化导航目录
2. 可视化元素（架构图/报告截图占位）
3. 代码块与配置文件示例
4. 明确的版本兼容性说明
5. 多级标题层次结构
6. Emoji 视觉分隔
7. 贡献流程标准化
8. 许可协议快速访问
9. 关键路径高亮显示
10. 跨平台特性说明

建议在实际使用时补充以下内容：
1. 添加真实的框架架构图
2. 替换实际的项目URL
3. 补充CI/CD徽章
4. 添加联系方式章节
5. 完善测试数据示例
6. 增加性能基准测试数据
7. 补充路线图章节
