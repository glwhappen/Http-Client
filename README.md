# HTTP Client

这是一个使用Tkinter和Python构建的简单HTTP客户端程序。它允许用户从`.http`文件中加载HTTP请求，并通过图形界面执行这些请求。

## 功能

- 从`.http`文件中加载HTTP请求。
- 支持GET和POST请求。
- 显示请求的完整HTTP内容。
- 显示请求的响应结果。

## 如何使用

1. **克隆仓库**:
   ```bash
   git clone https://github.com/glwhappen/Http-Client.git
   ```
2. **运行程序**:
   ```bash
   python http_client.py
   ```
3. **加载HTTP文件**:
   - 点击“Open HTTP File”按钮。
   - 选择一个`.http`文件。

4. **执行请求**:
   - 点击相应请求旁边的“Execute”按钮。
   - 查看底部文本区域中的响应结果。

## 注意

- 确保您的`.http`文件遵循正确的格式。
- 程序目前仅支持基本的GET和POST请求。

## 贡献

欢迎贡献！如果您有任何改进建议或功能请求，请开启一个issue或提交pull request。
