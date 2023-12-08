import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import requests
import json


def parse_request_line(line):
    parts = line.split(' ')
    if len(parts) < 2:
        return None, None
    method, path = parts[0], parts[1]
    return method, path

def parse_headers(lines):
    headers = {}
    for line in lines:
        # 如果遇到空行，停止处理头部
        if line.strip() == '':
            break
        if ':' in line and '###' not in line and '{' not in line:
            key, value = line.split(': ', 1)
            # 忽略行中的注释部分
            key, value = key.split('#', 1)[0], value.split('#', 1)[0]
            headers[key.strip()] = value.strip()
    print(headers)
    return headers

def parse_body(lines):
    body_str = ''.join(lines)
    try:
        return json.loads(body_str)
    except json.JSONDecodeError:
        print("JSON decode error in HTTP file.")
        return None

def parse_http_file(file_path):
    http_requests = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        # 使用正则表达式来匹配字符串的开始或每行的开始
        parts = re.split(r'(?m)^\s*###\s*', content)
        for part in parts:
            if not part.strip():
                continue
            # 跳过part变量的第一行
            part = part.split('\n')
            while part[0].find('HTTP/1.1') == -1:
                part = part[1:]
            part = '\n'.join(part)

            lines = part.strip().split('\n')
            method, path = parse_request_line(lines[0])
            if not method or not path:
                continue
            print(method, path)

            headers = parse_headers(lines[1:])
            # 找到第一个包含'{'的行，然后从那里开始解析body
            body_start_line = next((i for i, line in enumerate(lines) if '{' in line), len(lines))
            body = parse_body(lines[body_start_line:])

            url = 'http://' + headers.get("Host", "") + path
            print(url)
            http_requests.append({'method': method, 'url': url, 'headers': headers, 'body': body})

    return http_requests



def ensure_content_type_and_charset(headers, default_content_type='application/json'):
    content_type = headers.get('Content-Type', default_content_type)

    # 检查是否已经有charset设置
    if 'charset=' not in content_type:
        # 添加charset=utf-8
        content_type += '; charset=utf-8'

    headers['Content-Type'] = content_type
    return headers


def send_request(method, url, headers, body=None):
    try:
        headers = ensure_content_type_and_charset(headers)
        if method == 'POST':
            response = requests.post(url, headers=headers, json=body)
        elif method == 'GET':
            response = requests.get(url, headers=headers)
        else:
            return f"Unsupported method: {method}"
        # 设置响应的编码
        response.encoding = 'utf-8'
        result = response.text
        # 尝试将结果解析为JSON，然后转换为包含实际中文字符的字符串
        try:
            result_json = json.loads(result)
            result = json.dumps(result_json, indent=4, ensure_ascii=False)
        except json.JSONDecodeError:
            pass  # 如果结果不是JSON格式，保持原样
        return result

    except Exception as e:
        return f"Error: {e}"

def execute_request(req, button, text_widget):
    def thread_func():
        # 清空文本区域
        text_widget.delete('1.0', tk.END)

        # 更新按钮文本以反映正在进行的请求
        button.config(text="Requesting...")
        result = send_request(req['method'], req['url'], req['headers'], req.get('body'))

        # 请求完成后更新界面
        text_widget.after(0, lambda: text_widget.insert(tk.END, result + '\n\n'))
        button.config(text="Execute")  # 请求完成后恢复按钮文本

    # 创建并启动一个新线程来执行网络请求
    thread = threading.Thread(target=thread_func)
    thread.start()


class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "显示工具提示"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 25
        y = y + self.widget.winfo_rooty() + 25
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text):
    tooltip = ToolTip(widget)

    def enter(event):
        tooltip.showtip(text)

    def leave(event):
        tooltip.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


def create_gui():
    root = tk.Tk()
    root.title("HTTP Request Executor")

    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=10, fill='x')

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
    text_area.pack(padx=10, pady=10, fill='both', expand=True)

    open_button = ttk.Button(frame, text="Open HTTP File", command=lambda: load_http_requests(root, text_area))
    open_button.pack(side=tk.LEFT)

    return root, text_area

def load_http_requests(root, text_area):
    file_path = filedialog.askopenfilename(filetypes=[("HTTP Files", "*.http")])
    if file_path:
        http_requests = parse_http_file(file_path)
        for req in http_requests:
            frame = ttk.Frame(root)
            frame.pack(padx=10, pady=5, fill='x')

            label = ttk.Label(frame, text=f"{req['method']} {req['url']}")
            label.pack(side=tk.LEFT)

            # 构造要显示的完整HTTP请求内容
            http_content = f"Method: {req['method']} \nUrl: {req['url']}\n" + "\n".join(
                [f"{k}: {v}" for k, v in req['headers'].items()])
            if req['body']:
                http_content += "\n\n" + json.dumps(req['body'], indent=4, ensure_ascii=False)
            # 应用工具提示
            create_tooltip(label, http_content)

            button = ttk.Button(frame, text="Execute")
            button.config(command=lambda b=button, r=req: execute_request(r, b, text_area))
            button.pack(side=tk.RIGHT)

root, text_area = create_gui()
root.mainloop()
