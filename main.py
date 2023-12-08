import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import requests
import json

def parse_http_file(file_path):
    http_requests = []
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        parts = content.split('### Request')
        for part in parts:
            lines = part.strip().split('\n')
            if not lines:
                continue
            request = {'headers': {}, 'body': None, 'method': None, 'url': None}
            for i, line in enumerate(lines):
                if line.startswith('GET') or line.startswith('POST'):
                    parts = line.split(' ')
                    if len(parts) >= 2:
                        request['method'], request['url'] = parts[0:2]
                elif ':' in line and '{' not in line:
                    key, value = line.split(': ', 1)
                    request['headers'][key] = value
                elif '{' in line:
                    body_str = '\n'.join(lines[i:])  # Join the current and all following lines
                    try:
                        request['body'] = json.loads(body_str)
                    except json.JSONDecodeError:
                        print("JSON decode error in HTTP file.")
                        return []
                    break  # Exit the loop after processing the body
            if request['method'] and request['url']:  # Ensure both method and url are present
                http_requests.append(request)
    return http_requests



def send_request(method, url, headers, body=None):
    try:
        if method == 'POST':
            response = requests.post(url, headers=headers, json=body)
        elif method == 'GET':
            response = requests.get(url, headers=headers)
        else:
            return f"Unsupported method: {method}"
        return response.text
    except Exception as e:
        return f"Error: {e}"

def execute_request(req, text_widget):
    result = send_request(req['method'], req['url'], req['headers'], req.get('body'))
    text_widget.insert(tk.END, result + '\n\n')

def create_gui():
    root = tk.Tk()
    root.title("HTTP Request Executor")

    frame = ttk.Frame(root)
    frame.pack(padx=10, pady=10, fill='x')

    open_button = ttk.Button(frame, text="Open HTTP File", command=lambda: load_http_requests(root))
    open_button.pack(side=tk.LEFT)

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
    text_area.pack(padx=10, pady=10, fill='both', expand=True)

    return root, text_area

def load_http_requests(root):
    file_path = filedialog.askopenfilename(filetypes=[("HTTP Files", "*.http")])
    if file_path:
        http_requests = parse_http_file(file_path)
        for req in http_requests:
            frame = ttk.Frame(root)
            frame.pack(padx=10, pady=5, fill='x')

            label = ttk.Label(frame, text=f"{req['method']} {req['url']}")
            label.pack(side=tk.LEFT)

            button = ttk.Button(frame, text="Execute", command=lambda r=req, ta=text_area: execute_request(r, ta))
            button.pack(side=tk.RIGHT)

root, text_area = create_gui()
root.mainloop()
