import os
import re
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
from queue import Queue

class CredentialScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Credential Scanner v2.0")
        self.root.geometry("1200x800")
        self.root.minsize(900, 600)
        self.root.resizable(True, True)
        
        self.unique_android = {}
        self.unique_phone = {}
        self.unique_indian_phone = {}
        self.unique_email = {}
        self.unique_url = {}
        self.all_combos = {}
        
        self.scanning = False
        self.queue = Queue()
        
        self.setup_ui()
        self.apply_styles()
        
    def apply_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background='#1a1a2e')
        style.configure('TLabel', background='#1a1a2e', foreground='#eeeeee', font=('Segoe UI', 10))
        style.configure('TLabelframe', background='#1a1a2e', foreground='#00ff88', font=('Segoe UI', 10, 'bold'))
        style.configure('TLabelframe.Label', background='#1a1a2e', foreground='#00ff88')
        style.configure('TButton', background='#0f3460', foreground='#eeeeee', font=('Segoe UI', 10, 'bold'), padding=5)
        style.map('TButton', background=[('active', '#16213e')])
        style.configure('TEntry', fieldbackground='#0f3460', foreground='#eeeeee', font=('Segoe UI', 10))
        style.configure('TProgressbar', background='#00ff88', troughcolor='#0f3460', thickness=10)
        
    def setup_ui(self):
        self.root.configure(bg='#1a1a2e')
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.main_container = tk.Frame(self.root, bg='#1a1a2e')
        self.main_container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self.main_container.grid_rowconfigure(3, weight=3)
        self.main_container.grid_rowconfigure(4, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        header_frame = tk.Frame(self.main_container, bg='#1a1a2e')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="🔍 CREDENTIAL SCANNER v2.0", 
                                font=('Segoe UI', 20, 'bold'), fg='#00ff88', bg='#1a1a2e')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Advanced Credential Extraction Tool", 
                                   font=('Segoe UI', 10), fg='#888888', bg='#1a1a2e')
        subtitle_label.pack()
        
        input_frame = tk.LabelFrame(self.main_container, text=" INPUT SELECTION ", font=('Segoe UI', 11, 'bold'),
                                     fg='#00ff88', bg='#1a1a2e', bd=2, relief=tk.RIDGE)
        input_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10), ipady=8)
        
        path_frame = tk.Frame(input_frame, bg='#1a1a2e')
        path_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(path_frame, text="📁 Folder Path:", font=('Segoe UI', 10), 
                fg='#eeeeee', bg='#1a1a2e').pack(side=tk.LEFT, padx=(0, 10))
        
        self.folder_path = tk.StringVar()
        self.folder_entry = tk.Entry(path_frame, textvariable=self.folder_path, 
                                      font=('Segoe UI', 10), bg='#0f3460', fg='#eeeeee',
                                      insertbackground='#00ff88', relief=tk.FLAT, bd=0)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_frame, text="BROWSE", command=self.browse_folder,
                                font=('Segoe UI', 10, 'bold'), bg='#0f3460', fg='#00ff88',
                                activebackground='#16213e', activeforeground='#00ff88',
                                relief=tk.RAISED, bd=1, padx=15, pady=5)
        browse_btn.pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(input_frame, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        self.scan_btn = tk.Button(btn_frame, text="🚀 START SCAN", command=self.start_scan,
                                   font=('Segoe UI', 12, 'bold'), bg='#00ff88', fg='#1a1a2e',
                                   activebackground='#00cc66', activeforeground='#1a1a2e',
                                   relief=tk.RAISED, bd=2, padx=30, pady=8)
        self.scan_btn.pack()
        
        progress_frame = tk.LabelFrame(self.main_container, text=" SCAN PROGRESS ", font=('Segoe UI', 11, 'bold'),
                                        fg='#00ff88', bg='#1a1a2e', bd=2, relief=tk.RIDGE)
        progress_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10), ipady=8)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                             maximum=100, length=400, mode='determinate')
        self.progress_bar.pack(pady=(10, 5), padx=15, fill=tk.X)
        
        self.status_label = tk.Label(progress_frame, text="⚡ Ready to scan", font=('Segoe UI', 10),
                                      fg='#cccccc', bg='#1a1a2e')
        self.status_label.pack(pady=(5, 2))
        
        self.current_file_label = tk.Label(progress_frame, text="", font=('Segoe UI', 8),
                                            fg='#888888', bg='#1a1a2e')
        self.current_file_label.pack(pady=(0, 5))
        
        paned_window = ttk.PanedWindow(self.main_container, orient=tk.VERTICAL)
        paned_window.grid(row=3, column=0, sticky='nsew', pady=(0, 10))
        
        output_frame = tk.LabelFrame(paned_window, text=" CONSOLE OUTPUT ", font=('Segoe UI', 11, 'bold'),
                                      fg='#00ff88', bg='#1a1a2e', bd=2, relief=tk.RIDGE)
        
        text_frame = tk.Frame(output_frame, bg='#1a1a2e')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(text_frame, height=12, 
                                                    font=('Consolas', 9), bg='#0a0a0a', fg='#00ff88',
                                                    insertbackground='#00ff88', relief=tk.FLAT,
                                                    wrap=tk.WORD, bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        stats_frame = tk.LabelFrame(paned_window, text=" STATISTICS ", font=('Segoe UI', 11, 'bold'),
                                     fg='#00ff88', bg='#1a1a2e', bd=2, relief=tk.RIDGE)
        
        stats_text_frame = tk.Frame(stats_frame, bg='#1a1a2e')
        stats_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_text_frame, height=8, font=('Consolas', 9), 
                                   bg='#0a0a0a', fg='#ffaa00', relief=tk.FLAT, bd=0,
                                   wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        paned_window.add(output_frame, weight=2)
        paned_window.add(stats_frame, weight=1)
        
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
    
    def log(self, message, clear=False):
        self.queue.put(('log', message, clear))
    
    def update_stats(self, stats):
        self.queue.put(('stats', stats))
    
    def update_progress(self, value, status, current_file):
        self.queue.put(('progress', value, status, current_file))
    
    def start_scan(self):
        if not self.folder_path.get():
            self.log("❌ Please select a folder first!")
            return
        
        if self.scanning:
            self.log("⚠️ Scan already in progress!")
            return
        
        self.scanning = True
        self.scan_btn.config(state=tk.DISABLED, text="⏳ SCANNING...", bg='#ff6600')
        self.log_text.delete(1.0, tk.END)
        self.stats_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
        thread = threading.Thread(target=self.scan_folder, args=(self.folder_path.get(),))
        thread.daemon = True
        thread.start()
        self.process_queue()
    
    def process_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg[0] == 'log':
                    if msg[2]:
                        self.log_text.delete(1.0, tk.END)
                    self.log_text.insert(tk.END, msg[1] + '\n')
                    self.log_text.see(tk.END)
                elif msg[0] == 'stats':
                    self.stats_text.delete(1.0, tk.END)
                    self.stats_text.insert(tk.END, msg[1])
                elif msg[0] == 'progress':
                    self.progress_var.set(msg[1])
                    self.status_label.config(text=msg[2])
                    self.current_file_label.config(text=msg[3])
        except:
            pass
        finally:
            if self.scanning:
                self.root.after(100, self.process_queue)
    
    def is_indian_number(self, number):
        clean = re.sub(r'[^\d+]', '', str(number))
        if clean.startswith('+91'):
            clean = clean[3:]
        elif clean.startswith('91'):
            clean = clean[2:]
        return len(clean) == 10 and clean[0] in '6789'
    
    def scan_folder(self, folder_path):
        try:
            self.unique_android.clear()
            self.unique_phone.clear()
            self.unique_indian_phone.clear()
            self.unique_email.clear()
            self.unique_url.clear()
            self.all_combos.clear()
            
            script_location = os.path.dirname(os.path.abspath(__file__))
            output_folder = os.path.join(script_location, 'outputcombo')
            os.makedirs(output_folder, exist_ok=True)
            
            output_android_path = os.path.join(output_folder, 'package_android.txt')
            output_phone_path = os.path.join(output_folder, 'loginnumberpass.txt')
            output_indian_path = os.path.join(output_folder, 'indiannumberpass.txt')
            output_email_path = os.path.join(output_folder, 'emailuserpass.txt')
            output_url_path = os.path.join(output_folder, 'urlcombouserpass.txt')
            output_other_path = os.path.join(output_folder, 'other_usernames_passwords.txt')
            output_master_path = os.path.join(output_folder, 'ALL_CREDENTIALS_MASTER.txt')
            
            existing_android = set()
            existing_phone = set()
            existing_indian = set()
            existing_email = set()
            existing_url = set()
            existing_other = set()
            
            if os.path.exists(output_android_path):
                with open(output_android_path, 'r', encoding='utf-8', errors='ignore') as f:
                    existing_android.update(line.strip() for line in f if line.strip())
            if os.path.exists(output_phone_path):
                with open(output_phone_path, 'r', encoding='utf-8', errors='ignore') as f:
                    existing_phone.update(line.strip() for line in f if line.strip())
            if os.path.exists(output_indian_path):
                with open(output_indian_path, 'r', encoding='utf-8', errors='ignore') as f:
                    existing_indian.update(line.strip() for line in f if line.strip())
            if os.path.exists(output_email_path):
                with open(output_email_path, 'r', encoding='utf-8', errors='ignore') as f:
                    existing_email.update(line.strip() for line in f if line.strip())
            if os.path.exists(output_url_path):
                with open(output_url_path, 'r', encoding='utf-8', errors='ignore') as f:
                    existing_url.update(line.strip() for line in f if line.strip())
            if os.path.exists(output_other_path):
                with open(output_other_path, 'r', encoding='utf-8', errors='ignore') as f:
                    existing_other.update(line.strip() for line in f if line.strip())
            
            all_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith('.txt'):
                        all_files.append(os.path.join(root, file))
            
            total_files_count = len(all_files)
            total_folders = len(set(os.path.dirname(f) for f in all_files))
            
            self.log(f"{'='*70}")
            self.log(f"🔍 CREDENTIAL SCANNER v2.0")
            self.log(f"{'='*70}")
            self.log(f"📁 Input:  {folder_path}")
            self.log(f"💾 Output: {output_folder}")
            self.log(f"📄 TXT files found: {total_files_count}")
            self.log(f"{'='*70}\n")
            
            processed_files = 0
            total_lines = 0
            
            for file_path in all_files:
                processed_files += 1
                relative_path = os.path.relpath(file_path, folder_path)
                
                percent = (processed_files / total_files_count) * 100
                self.update_progress(percent, f"📄 Processing: {processed_files}/{total_files_count}", f"📁 {relative_path[:70]}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.splitlines()
                        total_lines += len(lines)
                        
                        current_host = ""
                        current_login = ""
                        current_password = ""
                        
                        for i, line in enumerate(lines):
                            line = line.strip()
                            if not line:
                                continue
                            
                            line_lower = line.lower()
                            
                            if 'host:' in line_lower:
                                host_match = re.search(r'host:\s*(.+)', line, re.IGNORECASE)
                                if host_match:
                                    current_host = host_match.group(1).strip()
                            
                            if 'login:' in line_lower or 'username:' in line_lower or 'user:' in line_lower or 'email:' in line_lower:
                                login_match = re.search(r'(?:login|username|user|email):\s*(.+)', line, re.IGNORECASE)
                                if login_match:
                                    current_login = login_match.group(1).strip()
                                    if current_login and len(current_login) > 40:
                                        current_login = ""
                            
                            if 'password:' in line_lower or 'pass:' in line_lower or 'pwd:' in line_lower:
                                pass_match = re.search(r'(?:password|pass|pwd):\s*(.+)', line, re.IGNORECASE)
                                if pass_match:
                                    current_password = pass_match.group(1).strip()
                                    if current_password and len(current_password) > 40:
                                        current_password = ""
                                    
                                    if current_host and current_login and current_password:
                                        if 'android://' in current_host:
                                            android_match = re.search(r'android://[^@]+@([^/]+)/?', current_host)
                                            if android_match:
                                                package = android_match.group(1)
                                                if current_login and current_password:
                                                    if len(current_login) <= 40 and len(current_password) <= 40:
                                                        entry = f"{package}:{current_login}:{current_password}"
                                                        key = f"{package}:{current_login}"
                                                        if key not in self.unique_android and entry not in existing_android:
                                                            self.unique_android[key] = current_password
                                        elif current_host.startswith('http'):
                                            entry = f"{current_host}:{current_login}:{current_password}"
                                            key = f"{current_host}:{current_login}"
                                            if key not in self.unique_url and entry not in existing_url:
                                                if len(current_login) <= 40 and len(current_password) <= 40:
                                                    self.unique_url[key] = current_password
                                        else:
                                            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', current_login):
                                                entry = f"{current_login}:{current_password}"
                                                key = current_login
                                                if key not in self.unique_email and entry not in existing_email:
                                                    if len(current_login) <= 40 and len(current_password) <= 40:
                                                        self.unique_email[key] = current_password
                                            elif re.match(r'^\+?[\d\s\-\(\)]{8,}$', current_login):
                                                clean_num = re.sub(r'[^\d+]', '', current_login)
                                                entry = f"{clean_num}:{current_password}"
                                                key = clean_num
                                                if key not in self.unique_phone and entry not in existing_phone:
                                                    if len(clean_num) <= 40 and len(current_password) <= 40:
                                                        self.unique_phone[key] = current_password
                                                        if self.is_indian_number(clean_num):
                                                            if entry not in existing_indian:
                                                                self.unique_indian_phone[key] = current_password
                                            else:
                                                entry = f"{current_login}:{current_password}"
                                                key = current_login
                                                if key not in self.all_combos and entry not in existing_other:
                                                    if len(current_login) <= 40 and len(current_password) <= 40:
                                                        self.all_combos[key] = current_password
                                    
                                    current_host = ""
                                    current_login = ""
                                    current_password = ""
                            
                            if 'android://' in line:
                                parts = line.split('@')
                                if len(parts) >= 2:
                                    package_part = parts[1]
                                    if '/:' in package_part:
                                        split_parts = package_part.split('/:', 1)
                                        if len(split_parts) == 2:
                                            package = split_parts[0]
                                            creds = split_parts[1]
                                            if ':' in creds:
                                                username, password = creds.split(':', 1)
                                                if username and password and len(username) <= 40 and len(password) <= 40:
                                                    entry = f"{package}:{username}:{password}"
                                                    key = f"{package}:{username}"
                                                    if key not in self.unique_android and entry not in existing_android:
                                                        self.unique_android[key] = password
                                    else:
                                        colon_pos = line.find(':/')
                                        if colon_pos != -1:
                                            creds_start = line.find(':', colon_pos + 2)
                                            if creds_start != -1:
                                                after_colon = line[creds_start + 1:]
                                                if ':' in after_colon:
                                                    username, password = after_colon.split(':', 1)
                                                    if username and password and len(username) <= 40 and len(password) <= 40:
                                                        package = package_part.split('/')[0] if '/' in package_part else package_part
                                                        entry = f"{package}:{username}:{password}"
                                                        key = f"{package}:{username}"
                                                        if key not in self.unique_android and entry not in existing_android:
                                                            self.unique_android[key] = password
                            
                            if '://' in line and 'android://' not in line:
                                url_match = re.search(r'(https?://[^:/\s]+)', line)
                                if url_match:
                                    url_base = url_match.group(1)
                                    remaining = line[line.find(url_base) + len(url_base):]
                                    if remaining.startswith(':') and ':' in remaining[1:]:
                                        cred_parts = remaining[1:].split(':', 1)
                                        if len(cred_parts) == 2:
                                            username, password = cred_parts[0].strip(), cred_parts[1].strip()
                                            if username and password and len(username) <= 40 and len(password) <= 40:
                                                entry = f"{url_base}:{username}:{password}"
                                                key = f"{url_base}:{username}"
                                                if key not in self.unique_url and entry not in existing_url:
                                                    self.unique_url[key] = password
                            
                            if ':' in line and not any(x in line_lower for x in ['soft:', 'host:', 'login:', 'password:', 'username:', 'user:', 'email:', 'pass:', 'pwd:', 'android://', 'https://', 'http://']):
                                if line.count(':') == 1:
                                    username, password = line.split(':', 1)
                                    username, password = username.strip(), password.strip()
                                    if username and password and len(username) <= 40 and len(password) <= 40:
                                        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', username):
                                            entry = f"{username}:{password}"
                                            key = username
                                            if key not in self.unique_email and entry not in existing_email:
                                                self.unique_email[key] = password
                                        elif re.match(r'^\+?[\d\s\-\(\)]{8,}$', username) or username.isdigit():
                                            clean_num = re.sub(r'[^\d+]', '', username)
                                            entry = f"{clean_num}:{password}"
                                            key = clean_num
                                            if key not in self.unique_phone and entry not in existing_phone:
                                                self.unique_phone[clean_num] = password
                                                if self.is_indian_number(clean_num):
                                                    if entry not in existing_indian:
                                                        self.unique_indian_phone[clean_num] = password
                                            elif len(username) >= 3:
                                                entry = f"{username}:{password}"
                                                key = username
                                                if key not in self.all_combos and entry not in existing_other:
                                                    self.all_combos[username] = password
                                
                                elif line.count(':') > 1:
                                    parts = line.split(':')
                                    if len(parts) >= 3:
                                        username = parts[-2].strip()
                                        password = parts[-1].strip()
                                        if username and password and len(username) <= 40 and len(password) <= 40:
                                            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', username):
                                                entry = f"{username}:{password}"
                                                key = username
                                                if key not in self.unique_email and entry not in existing_email:
                                                    self.unique_email[username] = password
                                            elif username.isdigit() or (username.startswith('+') and username[1:].isdigit()):
                                                clean_num = re.sub(r'[^\d+]', '', username)
                                                entry = f"{clean_num}:{password}"
                                                key = clean_num
                                                if key not in self.unique_phone and entry not in existing_phone:
                                                    self.unique_phone[clean_num] = password
                                                    if self.is_indian_number(clean_num):
                                                        if entry not in existing_indian:
                                                            self.unique_indian_phone[clean_num] = password
                                            elif len(username) >= 3:
                                                entry = f"{username}:{password}"
                                                key = username
                                                if key not in self.all_combos and entry not in existing_other:
                                                    self.all_combos[username] = password
                        
                        if current_host and current_login and current_password:
                            if 'android://' in current_host:
                                android_match = re.search(r'android://[^@]+@([^/]+)/?', current_host)
                                if android_match:
                                    package = android_match.group(1)
                                    if current_login and current_password:
                                        if len(current_login) <= 40 and len(current_password) <= 40:
                                            entry = f"{package}:{current_login}:{current_password}"
                                            key = f"{package}:{current_login}"
                                            if key not in self.unique_android and entry not in existing_android:
                                                self.unique_android[key] = current_password
                        
                except Exception as e:
                    pass
            
            new_android = [f"{k}:{v}" for k, v in self.unique_android.items()]
            new_phone = [f"{k}:{v}" for k, v in self.unique_phone.items()]
            new_indian = [f"{k}:{v}" for k, v in self.unique_indian_phone.items()]
            new_email = [f"{k}:{v}" for k, v in self.unique_email.items()]
            new_url = [f"{k}:{v}" for k, v in self.unique_url.items()]
            new_other = [f"{k}:{v}" for k, v in self.all_combos.items()]
            
            if new_android:
                with open(output_android_path, 'a', encoding='utf-8') as f:
                    f.write('\n'.join(new_android) + '\n')
            if new_phone:
                with open(output_phone_path, 'a', encoding='utf-8') as f:
                    f.write('\n'.join(new_phone) + '\n')
            if new_indian:
                with open(output_indian_path, 'a', encoding='utf-8') as f:
                    f.write('\n'.join(new_indian) + '\n')
            if new_email:
                with open(output_email_path, 'a', encoding='utf-8') as f:
                    f.write('\n'.join(new_email) + '\n')
            if new_url:
                with open(output_url_path, 'a', encoding='utf-8') as f:
                    f.write('\n'.join(new_url) + '\n')
            if new_other:
                with open(output_other_path, 'a', encoding='utf-8') as f:
                    f.write('\n'.join(new_other) + '\n')
            
            all_master = []
            for tag, data in [("[ANDROID]", new_android), ("[PHONE]", new_phone), ("[INDIAN]", new_indian), ("[EMAIL]", new_email), ("[URL]", new_url), ("[OTHER]", new_other)]:
                for item in data:
                    all_master.append(f"{tag} {item}")
            
            if all_master:
                with open(output_master_path, 'a', encoding='utf-8') as f:
                    f.write('\n'.join(all_master) + '\n')
            
            stats = f"{'='*70}\n"
            stats += f"✅ SCAN COMPLETE\n"
            stats += f"{'='*70}\n"
            stats += f"📊 FINAL STATISTICS\n"
            stats += f"{'─'*70}\n"
            stats += f"📁 Folders scanned: {total_folders}\n"
            stats += f"📄 Files scanned:    {processed_files:,}\n"
            stats += f"📝 Lines analyzed:   {total_lines:,}\n"
            stats += f"{'─'*70}\n"
            stats += f"📱 Android:     {len(new_android):>5} new  (total: {len(existing_android)+len(new_android):>5})\n"
            stats += f"📞 Phone:       {len(new_phone):>5} new  (total: {len(existing_phone)+len(new_phone):>5})\n"
            stats += f"🇮🇳 Indian:     {len(new_indian):>5} new  (total: {len(existing_indian)+len(new_indian):>5})\n"
            stats += f"✉️  Email:       {len(new_email):>5} new  (total: {len(existing_email)+len(new_email):>5})\n"
            stats += f"🔗 URL:         {len(new_url):>5} new  (total: {len(existing_url)+len(new_url):>5})\n"
            stats += f"🔑 Other:       {len(new_other):>5} new  (total: {len(existing_other)+len(new_other):>5})\n"
            stats += f"{'─'*70}\n"
            stats += f"🎯 TOTAL NEW:   {len(new_android)+len(new_phone)+len(new_indian)+len(new_email)+len(new_url)+len(new_other):>5}\n"
            stats += f"{'='*70}\n"
            stats += f"📁 Output folder: {output_folder}\n"
            stats += f"{'='*70}\n"
            
            self.update_stats(stats)
            self.log(f"\n✅ Scan completed successfully!", True)
            self.update_progress(100, "✅ SCAN COMPLETE!", "")
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
        finally:
            self.scanning = False
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="🚀 START SCAN", bg='#00ff88'))

if __name__ == "__main__":
    root = tk.Tk()
    app = CredentialScannerGUI(root)
    root.mainloop()
