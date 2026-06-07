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
        self.root.geometry("900x700")
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
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        ttk.Label(main_frame, text="CREDENTIAL SCANNER v2.0", font=('Arial', 16, 'bold')).grid(row=0, column=0, pady=10)
        
        input_frame = ttk.LabelFrame(main_frame, text="Input Selection", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="Folder Path:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(input_frame, textvariable=self.folder_path, width=60)
        self.folder_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5)
        ttk.Button(input_frame, text="Browse", command=self.browse_folder).grid(row=0, column=2, padx=5)
        
        ttk.Button(input_frame, text="Start Scan", command=self.start_scan, width=15).grid(row=1, column=1, pady=10)
        
        progress_frame = ttk.LabelFrame(main_frame, text="Scan Progress", padding="10")
        progress_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready", font=('Consolas', 9))
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.current_file_label = ttk.Label(progress_frame, text="", font=('Consolas', 8))
        self.current_file_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        log_frame = ttk.LabelFrame(main_frame, text="Console Output", padding="10")
        log_frame.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        stats_frame = ttk.LabelFrame(main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=5)
        stats_frame.columnconfigure(0, weight=1)
        
        self.stats_text = tk.Text(stats_frame, height=6, font=('Consolas', 9))
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
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
            self.log("Please select a folder first!")
            return
        
        if self.scanning:
            self.log("Scan already in progress!")
            return
        
        self.scanning = True
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
                file_name = os.path.basename(file_path)
                relative_path = os.path.relpath(file_path, folder_path)
                
                percent = (processed_files / total_files_count) * 100
                self.update_progress(percent, f"Processing: {processed_files}/{total_files_count}", f"File: {relative_path[:60]}")
                
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
            stats += f"📄 Files scanned:    {processed_files}\n"
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
            self.update_progress(100, "Complete!", "")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
        finally:
            self.scanning = False

if __name__ == "__main__":
    root = tk.Tk()
    app = CredentialScannerGUI(root)
    root.mainloop()
