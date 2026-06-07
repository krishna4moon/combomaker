import os
import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import threading
from queue import Queue
import base64
import configparser
import sqlite3
import zipfile
import tarfile

class AdvancedServerCredentialScanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Server Credential Scanner v4.0")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        self.root.resizable(True, True)
        
        self.unique_ftp = {}
        self.unique_sftp = {}
        self.unique_ssh = {}
        self.unique_cpanel = {}
        self.unique_whm = {}
        self.unique_plesk = {}
        self.unique_directadmin = {}
        self.unique_mysql = {}
        self.unique_postgres = {}
        self.unique_mongodb = {}
        self.unique_redis = {}
        self.unique_elasticsearch = {}
        self.unique_rabbitmq = {}
        self.unique_aws = {}
        self.unique_azure = {}
        self.unique_gcp = {}
        self.unique_docker = {}
        self.unique_kubernetes = {}
        self.unique_jenkins = {}
        self.unique_nexus = {}
        self.unique_sonarqube = {}
        self.unique_git = {}
        self.unique_vps = {}
        self.unique_hosting = {}
        self.unique_configs = {}
        
        self.scanning = False
        self.queue = Queue()
        
        self.common_ports = {
            'FTP': ['21'],
            'SFTP': ['22'],
            'SSH': ['22'],
            'CPanel': ['2082', '2083', '2086', '2087', '2095', '2096'],
            'WHM': ['2086', '2087'],
            'Plesk': ['8443', '8880'],
            'DirectAdmin': ['2222'],
            'MySQL': ['3306'],
            'PostgreSQL': ['5432', '5433'],
            'MongoDB': ['27017', '27018', '27019'],
            'Redis': ['6379'],
            'Elasticsearch': ['9200', '9300'],
            'RabbitMQ': ['15672', '5672'],
            'Docker': ['2375', '2376'],
            'Kubernetes': ['6443', '10250'],
            'Jenkins': ['8080'],
            'Nexus': ['8081'],
            'SonarQube': ['9000'],
            'Git': ['22', '9418'],
            'VPS': ['22', '3389', '5900', '5901'],
            'WebHosting': ['8080', '8443', '8880', '2082', '2083']
        }
        
        self.file_extensions = ['.txt', '.xml', '.json', '.ini', '.conf', '.cfg', '.config', '.log', 
                                '.sql', '.db', '.sqlite', '.env', '.yml', '.yaml', '.properties',
                                '.ftp', '.sftp', '.ssh', '.pem', '.key', '.crt', '.cer', '.p12',
                                '.ovpn', '.rdp', '.rdg', '.vnc', '.remote', '.rpd']
        
        self.setup_ui()
        self.apply_styles()
        
    def apply_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('TFrame', background='#0a0a0a')
        style.configure('TLabel', background='#0a0a0a', foreground='#00ff00', font=('Consolas', 10))
        style.configure('TLabelframe', background='#0a0a0a', foreground='#00ff00', font=('Consolas', 10, 'bold'))
        style.configure('TLabelframe.Label', background='#0a0a0a', foreground='#00ff00')
        style.configure('TButton', background='#1a1a1a', foreground='#00ff00', font=('Consolas', 10, 'bold'), padding=5)
        style.map('TButton', background=[('active', '#2a2a2a')])
        style.configure('TEntry', fieldbackground='#1a1a1a', foreground='#00ff00', font=('Consolas', 10))
        style.configure('TProgressbar', background='#00ff00', troughcolor='#1a1a1a', thickness=10)
        
    def setup_ui(self):
        self.root.configure(bg='#0a0a0a')
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.main_container = tk.Frame(self.root, bg='#0a0a0a')
        self.main_container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self.main_container.grid_rowconfigure(4, weight=3)
        self.main_container.grid_rowconfigure(5, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        header_frame = tk.Frame(self.main_container, bg='#0a0a0a')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="🔐 ADVANCED SERVER CREDENTIAL SCANNER v4.0", 
                                font=('Consolas', 20, 'bold'), fg='#00ff00', bg='#0a0a0a')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="FTP | SFTP | SSH | VPS | Hosting | CPanel | WHM | Plesk | MySQL | PostgreSQL | MongoDB | Redis | AWS | Azure | GCP | Docker | Kubernetes | Jenkins | Git",
                                   font=('Consolas', 9), fg='#666666', bg='#0a0a0a')
        subtitle_label.pack()
        
        input_frame = tk.LabelFrame(self.main_container, text=" INPUT SELECTION ", font=('Consolas', 11, 'bold'),
                                     fg='#00ff00', bg='#0a0a0a', bd=2, relief=tk.RIDGE)
        input_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10), ipady=8)
        
        path_frame = tk.Frame(input_frame, bg='#0a0a0a')
        path_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(path_frame, text="📁 TARGET PATH:", font=('Consolas', 10), 
                fg='#00ff00', bg='#0a0a0a').pack(side=tk.LEFT, padx=(0, 10))
        
        self.folder_path = tk.StringVar()
        self.folder_entry = tk.Entry(path_frame, textvariable=self.folder_path, 
                                      font=('Consolas', 10), bg='#1a1a1a', fg='#00ff00',
                                      insertbackground='#00ff00', relief=tk.FLAT, bd=0)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = tk.Button(path_frame, text="[ BROWSE ]", command=self.browse_folder,
                                font=('Consolas', 10, 'bold'), bg='#1a1a1a', fg='#00ff00',
                                activebackground='#2a2a2a', activeforeground='#00ff00',
                                relief=tk.RAISED, bd=1, padx=15, pady=5)
        browse_btn.pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(input_frame, bg='#0a0a0a')
        btn_frame.pack(pady=10)
        
        self.scan_btn = tk.Button(btn_frame, text="[ 🚀 START SCAN ]", command=self.start_scan,
                                   font=('Consolas', 12, 'bold'), bg='#00ff00', fg='#0a0a0a',
                                   activebackground='#00cc00', activeforeground='#0a0a0a',
                                   relief=tk.RAISED, bd=2, padx=30, pady=8)
        self.scan_btn.pack()
        
        progress_frame = tk.LabelFrame(self.main_container, text=" SCAN PROGRESS ", font=('Consolas', 11, 'bold'),
                                        fg='#00ff00', bg='#0a0a0a', bd=2, relief=tk.RIDGE)
        progress_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10), ipady=8)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                             maximum=100, length=400, mode='determinate')
        self.progress_bar.pack(pady=(10, 5), padx=15, fill=tk.X)
        
        self.status_label = tk.Label(progress_frame, text="⚡ SYSTEM READY", font=('Consolas', 10),
                                      fg='#00ff00', bg='#0a0a0a')
        self.status_label.pack(pady=(5, 2))
        
        self.current_file_label = tk.Label(progress_frame, text="", font=('Consolas', 8),
                                            fg='#666666', bg='#0a0a0a')
        self.current_file_label.pack(pady=(0, 5))
        
        paned_window = ttk.PanedWindow(self.main_container, orient=tk.VERTICAL)
        paned_window.grid(row=3, column=0, sticky='nsew', pady=(0, 10))
        
        output_frame = tk.LabelFrame(paned_window, text=" CONSOLE OUTPUT ", font=('Consolas', 11, 'bold'),
                                      fg='#00ff00', bg='#0a0a0a', bd=2, relief=tk.RIDGE)
        
        text_frame = tk.Frame(output_frame, bg='#0a0a0a')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(text_frame, height=14, 
                                                    font=('Consolas', 9), bg='#0a0a0a', fg='#00ff00',
                                                    insertbackground='#00ff00', relief=tk.FLAT,
                                                    wrap=tk.WORD, bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        stats_frame = tk.LabelFrame(paned_window, text=" STATISTICS ", font=('Consolas', 11, 'bold'),
                                     fg='#00ff00', bg='#0a0a0a', bd=2, relief=tk.RIDGE)
        
        stats_text_frame = tk.Frame(stats_frame, bg='#0a0a0a')
        stats_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_text_frame, height=6, font=('Consolas', 9), 
                                   bg='#0a0a0a', fg='#ffff00', relief=tk.FLAT, bd=0,
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
            self.log("[!] Please select a target folder!")
            return
        
        if self.scanning:
            self.log("[!] Scan already in progress!")
            return
        
        self.scanning = True
        self.scan_btn.config(state=tk.DISABLED, text="[ ⏳ SCANNING... ]", bg='#ff6600')
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
    
    def detect_server_type(self, host, port, username, content=''):
        host_lower = host.lower()
        user_lower = username.lower() if username else ''
        content_lower = content.lower()
        
        if any(x in content_lower for x in ['aws', 'amazon', 's3', 'ec2', 'rds', 'lambda']):
            return 'AWS'
        if any(x in content_lower for x in ['azure', 'microsoft', 'az', 'blob']):
            return 'Azure'
        if any(x in content_lower for x in ['gcp', 'google cloud', 'compute engine', 'bigquery']):
            return 'GCP'
        if any(x in content_lower for x in ['docker', 'container', 'image', 'dockerfile']):
            return 'Docker'
        if any(x in content_lower for x in ['kubectl', 'k8s', 'kubernetes', 'pod', 'service']):
            return 'Kubernetes'
        if any(x in content_lower for x in ['jenkins', 'job', 'build', 'pipeline']):
            return 'Jenkins'
        if any(x in content_lower for x in ['nexus', 'repository', 'artifact']):
            return 'Nexus'
        if any(x in content_lower for x in ['sonarqube', 'sonar', 'quality gate']):
            return 'SonarQube'
        if any(x in content_lower for x in ['git', 'github', 'gitlab', 'bitbucket']):
            return 'Git'
        if any(x in content_lower for x in ['vps', 'virtual private server', 'vultr', 'digitalocean', 'linode']):
            return 'VPS'
        if any(x in content_lower for x in ['hosting', 'shared hosting', 'cpanel', 'whm']):
            return 'Hosting'
        
        if port in self.common_ports['FTP'] or 'ftp' in host_lower:
            return 'FTP'
        if port in self.common_ports['SFTP'] or 'sftp' in host_lower:
            return 'SFTP'
        if port in self.common_ports['SSH'] or 'ssh' in host_lower:
            return 'SSH'
        if port in self.common_ports['CPanel'] or 'cpanel' in host_lower:
            return 'CPanel'
        if port in self.common_ports['WHM'] or 'whm' in host_lower:
            return 'WHM'
        if port in self.common_ports['Plesk'] or 'plesk' in host_lower:
            return 'Plesk'
        if port in self.common_ports['DirectAdmin'] or 'directadmin' in host_lower:
            return 'DirectAdmin'
        if port in self.common_ports['MySQL'] or 'mysql' in host_lower or 'mariadb' in host_lower:
            return 'MySQL'
        if port in self.common_ports['PostgreSQL'] or 'postgres' in host_lower:
            return 'PostgreSQL'
        if port in self.common_ports['MongoDB'] or 'mongo' in host_lower:
            return 'MongoDB'
        if port in self.common_ports['Redis'] or 'redis' in host_lower:
            return 'Redis'
        if port in self.common_ports['Elasticsearch'] or 'elastic' in host_lower:
            return 'Elasticsearch'
        if port in self.common_ports['RabbitMQ'] or 'rabbit' in host_lower:
            return 'RabbitMQ'
        if port in self.common_ports['VPS']:
            return 'VPS'
        
        return 'Unknown'
    
    def extract_credentials_from_text(self, content):
        credentials = []
        
        patterns = [
            # Standard formats
            r'(?:ftp|sftp|ssh)://([^:]+):(\d+):([^:]+):([^\s]+)',
            r'(?:host|server)[=:\s]+([^\s]+)[\s\n]+(?:port)[=:\s]+(\d+)[\s\n]+(?:user|username)[=:\s]+([^\s]+)[\s\n]+(?:password|pass)[=:\s]+([^\s]+)',
            r'(?:user|username)[=:\s]+([^\s]+)[\s\n]+(?:password|pass)[=:\s]+([^\s]+)[\s\n]+(?:host|server)[=:\s]+([^\s]+)[\s\n]+(?:port)[=:\s]+(\d+)',
            r'(\d+\.\d+\.\d+\.\d+):(\d+):([^:]+):([^\s]+)',
            r'([a-zA-Z0-9\.\-]+):(\d+):([^:]+):([^\s]+)',
            
            # URL formats
            r'(?:mysql|postgres|mongodb|redis)://([^:]+):([^@]+)@([^:]+):(\d+)',
            r'(?:ftp|sftp|ssh)://([^:]+):([^@]+)@([^:]+):(\d+)',
            
            # Environment variable formats
            r'(?:DB_HOST|DATABASE_HOST|DB_SERVER)[=:\s]+([^\s]+)[\n\r]+(?:DB_PORT|DATABASE_PORT)[=:\s]+(\d+)[\n\r]+(?:DB_USER|DATABASE_USER|DB_USERNAME)[=:\s]+([^\s]+)[\n\r]+(?:DB_PASS|DB_PASSWORD|DATABASE_PASSWORD)[=:\s]+([^\s]+)',
            r'(?:FTP_HOST|SFTP_HOST)[=:\s]+([^\s]+)[\n\r]+(?:FTP_PORT|SFTP_PORT)[=:\s]+(\d+)[\n\r]+(?:FTP_USER|SFTP_USER)[=:\s]+([^\s]+)[\n\r]+(?:FTP_PASS|SFTP_PASS)[=:\s]+([^\s]+)',
            
            # Simple formats
            r'host[=:\s]+([^\s]+).*?port[=:\s]+(\d+).*?user[=:\s]+([^\s]+).*?pass[=:\s]+([^\s]+)',
            r'server[=:\s]+([^\s]+).*?port[=:\s]+(\d+).*?username[=:\s]+([^\s]+).*?password[=:\s]+([^\s]+)',
            
            # IP:PORT:USER:PASS format
            r'(\d+\.\d+\.\d+\.\d+):(\d+):([^:]+):([^\s]+)',
            r'([a-zA-Z0-9\.\-]+):(\d+):([^:]+):([^\s]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if len(match) == 4:
                    host, port, user, password = match
                    credentials.append((host, port, user, password))
        
        lines = content.split('\n')
        current_host = None
        current_port = None
        current_user = None
        current_password = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if re.search(r'(?:host|server|hostname|address)[=:\s]+', line, re.IGNORECASE):
                match = re.search(r'(?:host|server|hostname|address)[=:\s]+([^\s]+)', line, re.IGNORECASE)
                if match:
                    current_host = match.group(1)
            elif re.search(r'port[=:\s]+', line, re.IGNORECASE):
                match = re.search(r'port[=:\s]+(\d+)', line, re.IGNORECASE)
                if match:
                    current_port = match.group(1)
            elif re.search(r'(?:user|username|login|uid)[=:\s]+', line, re.IGNORECASE):
                match = re.search(r'(?:user|username|login|uid)[=:\s]+([^\s]+)', line, re.IGNORECASE)
                if match:
                    current_user = match.group(1)
            elif re.search(r'(?:password|pass|pwd|secret|key)[=:\s]+', line, re.IGNORECASE):
                match = re.search(r'(?:password|pass|pwd|secret|key)[=:\s]+([^\s]+)', line, re.IGNORECASE)
                if match:
                    current_password = match.group(1)
                    if current_host and current_user and current_password:
                        credentials.append((current_host, current_port, current_user, current_password))
                        current_host = current_port = current_user = current_password = None
        
        return credentials
    
    def scan_folder(self, folder_path):
        try:
            self.unique_ftp.clear()
            self.unique_sftp.clear()
            self.unique_ssh.clear()
            self.unique_cpanel.clear()
            self.unique_whm.clear()
            self.unique_plesk.clear()
            self.unique_directadmin.clear()
            self.unique_mysql.clear()
            self.unique_postgres.clear()
            self.unique_mongodb.clear()
            self.unique_redis.clear()
            self.unique_elasticsearch.clear()
            self.unique_rabbitmq.clear()
            self.unique_aws.clear()
            self.unique_azure.clear()
            self.unique_gcp.clear()
            self.unique_docker.clear()
            self.unique_kubernetes.clear()
            self.unique_jenkins.clear()
            self.unique_nexus.clear()
            self.unique_sonarqube.clear()
            self.unique_git.clear()
            self.unique_vps.clear()
            self.unique_hosting.clear()
            self.unique_configs.clear()
            
            script_location = os.path.dirname(os.path.abspath(__file__))
            output_folder = os.path.join(script_location, 'server_credentials')
            os.makedirs(output_folder, exist_ok=True)
            
            output_files = {
                'all': os.path.join(output_folder, 'all_server_credentials.txt'),
                'configs': os.path.join(output_folder, 'extracted_configs.txt'),
                'ftp': os.path.join(output_folder, 'ftp_credentials.txt'),
                'sftp': os.path.join(output_folder, 'sftp_credentials.txt'),
                'ssh': os.path.join(output_folder, 'ssh_credentials.txt'),
                'cpanel': os.path.join(output_folder, 'cpanel_whm_credentials.txt'),
                'plesk': os.path.join(output_folder, 'plesk_directadmin_credentials.txt'),
                'database': os.path.join(output_folder, 'database_credentials.txt'),
                'nosql': os.path.join(output_folder, 'nosql_credentials.txt'),
                'cloud': os.path.join(output_folder, 'cloud_provider_credentials.txt'),
                'devops': os.path.join(output_folder, 'devops_credentials.txt'),
                'vps': os.path.join(output_folder, 'vps_hosting_credentials.txt')
            }
            
            existing = {key: set() for key in output_files}
            for file_type, file_path in output_files.items():
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        existing[file_type].update(line.strip() for line in f if line.strip())
            
            all_files = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in self.file_extensions):
                        all_files.append(os.path.join(root, file))
            
            archives = []
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(('.zip', '.tar', '.gz', '.bz2', '.7z')):
                        archives.append(os.path.join(root, file))
            
            total_files_count = len(all_files) + len(archives)
            total_folders = len(set(os.path.dirname(f) for f in all_files))
            
            self.log(f"{'='*80}")
            self.log(f"[+] ADVANCED SERVER CREDENTIAL SCANNER v4.0")
            self.log(f"[+] TARGET: {folder_path}")
            self.log(f"[+] OUTPUT: {output_folder}")
            self.log(f"[+] CONFIG FILES: {len(all_files)}")
            self.log(f"[+] ARCHIVES: {len(archives)}")
            self.log(f"{'='*80}\n")
            
            processed_files = 0
            total_lines = 0
            
            for file_path in all_files:
                processed_files += 1
                relative_path = os.path.relpath(file_path, folder_path)
                
                percent = (processed_files / total_files_count) * 100
                self.update_progress(percent, f"[SCANNING] {processed_files}/{total_files_count}", f"{relative_path[:80]}")
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.splitlines()
                        total_lines += len(lines)
                        
                        credentials = self.extract_credentials_from_text(content)
                        
                        for host, port, user, password in credentials:
                            if not port:
                                for p in self.common_ports.values():
                                    if any(p in host for p in p):
                                        for pp in p:
                                            if pp in host:
                                                port = pp
                                                break
                            
                            server_type = self.detect_server_type(host, port, user, content)
                            display_host = f"{host}:{port}" if port else host
                            entry = f"{display_host}|{user}|{password}"
                            key = f"{display_host}|{user}"
                            
                            if server_type == 'FTP' and key not in self.unique_ftp and entry not in existing['ftp']:
                                self.unique_ftp[key] = password
                            elif server_type == 'SFTP' and key not in self.unique_sftp and entry not in existing['sftp']:
                                self.unique_sftp[key] = password
                            elif server_type == 'SSH' and key not in self.unique_ssh and entry not in existing['sftp']:
                                self.unique_ssh[key] = password
                            elif server_type in ['CPanel', 'WHM'] and key not in self.unique_cpanel and entry not in existing['cpanel']:
                                self.unique_cpanel[key] = password
                            elif server_type in ['Plesk', 'DirectAdmin'] and key not in self.unique_plesk and entry not in existing['plesk']:
                                self.unique_plesk[key] = password
                            elif server_type in ['MySQL', 'PostgreSQL'] and key not in self.unique_mysql and entry not in existing['database']:
                                self.unique_mysql[key] = password
                            elif server_type in ['MongoDB', 'Redis', 'Elasticsearch', 'RabbitMQ'] and key not in self.unique_mongodb and entry not in existing['nosql']:
                                self.unique_mongodb[key] = password
                            elif server_type in ['AWS', 'Azure', 'GCP'] and key not in self.unique_aws and entry not in existing['cloud']:
                                self.unique_aws[key] = password
                            elif server_type in ['Docker', 'Kubernetes', 'Jenkins', 'Nexus', 'SonarQube', 'Git'] and key not in self.unique_docker and entry not in existing['devops']:
                                self.unique_docker[key] = password
                            elif server_type in ['VPS', 'Hosting'] and key not in self.unique_vps and entry not in existing['vps']:
                                self.unique_vps[key] = password
                            else:
                                if key not in self.unique_configs and entry not in existing['configs']:
                                    self.unique_configs[key] = password
                        
                        if credentials:
                            self.log(f"   [+] Found {len(credentials)} credentials in {os.path.basename(file_path)}")
                        
                except Exception as e:
                    pass
            
            all_new = {}
            for name, data in [('ftp', self.unique_ftp), ('sftp', self.unique_sftp), ('ssh', self.unique_ssh),
                               ('cpanel', self.unique_cpanel), ('plesk', self.unique_plesk), ('database', self.unique_mysql),
                               ('nosql', self.unique_mongodb), ('cloud', self.unique_aws), ('devops', self.unique_docker),
                               ('vps', self.unique_vps), ('configs', self.unique_configs)]:
                all_new[name] = [f"{k}:{v}" for k, v in data.items()]
            
            for file_type, new_data in all_new.items():
                if new_data:
                    with open(output_files[file_type], 'a', encoding='utf-8') as f:
                        f.write('\n'.join(new_data) + '\n')
            
            all_credentials = []
            for tag, data in [("[FTP]", all_new['ftp']), ("[SFTP/SSH]", all_new['sftp'] + all_new['ssh']), 
                              ("[CPANEL/WHM]", all_new['cpanel']), ("[PLESK/DIRECTADMIN]", all_new['plesk']),
                              ("[DATABASE]", all_new['database']), ("[NoSQL]", all_new['nosql']),
                              ("[CLOUD]", all_new['cloud']), ("[DEVOPS]", all_new['devops']),
                              ("[VPS/HOSTING]", all_new['vps']), ("[CONFIGS]", all_new['configs'])]:
                for item in data:
                    all_credentials.append(f"{tag} {item}")
            
            if all_credentials:
                with open(output_files['all'], 'a', encoding='utf-8') as f:
                    f.write('\n'.join(all_credentials) + '\n')
            
            total_new = sum(len(data) for data in all_new.values())
            
            stats = f"{'='*80}\n"
            stats += f"[✓] SCAN COMPLETED SUCCESSFULLY\n"
            stats += f"{'='*80}\n"
            stats += f"[📊] FINAL STATISTICS\n"
            stats += f"{'─'*80}\n"
            stats += f"[📁] Folders Scanned:     {total_folders}\n"
            stats += f"[📄] Files Scanned:       {processed_files:,}\n"
            stats += f"[📝] Lines Analyzed:      {total_lines:,}\n"
            stats += f"{'─'*80}\n"
            stats += f"[🔐] FTP:                 {len(all_new['ftp']):>5} new\n"
            stats += f"[🔐] SFTP/SSH:            {len(all_new['sftp'])+len(all_new['ssh']):>5} new\n"
            stats += f"[🔐] CPanel/WHM:          {len(all_new['cpanel']):>5} new\n"
            stats += f"[🔐] Plesk/DirectAdmin:   {len(all_new['plesk']):>5} new\n"
            stats += f"[🔐] Database (MySQL/PG): {len(all_new['database']):>5} new\n"
            stats += f"[🔐] NoSQL (Mongo/Redis): {len(all_new['nosql']):>5} new\n"
            stats += f"[🔐] Cloud (AWS/Azure/GCP):{len(all_new['cloud']):>5} new\n"
            stats += f"[🔐] DevOps (Docker/K8s/Jenkins):{len(all_new['devops']):>5} new\n"
            stats += f"[🔐] VPS/Hosting:         {len(all_new['vps']):>5} new\n"
            stats += f"[🔐] Other Configs:       {len(all_new['configs']):>5} new\n"
            stats += f"{'─'*80}\n"
            stats += f"[🎯] TOTAL NEW:           {total_new:>5}\n"
            stats += f"{'='*80}\n"
            stats += f"[💾] OUTPUT: {output_folder}\n"
            stats += f"{'='*80}\n"
            
            self.update_stats(stats)
            self.log(f"[✓] SCAN COMPLETED! Found {total_new} new credentials.", True)
            self.update_progress(100, "[✓] SCAN COMPLETE", "")
            
        except Exception as e:
            self.log(f"[✗] ERROR: {str(e)}")
        finally:
            self.scanning = False
            self.root.after(0, lambda: self.scan_btn.config(state=tk.NORMAL, text="[ 🚀 START SCAN ]", bg='#00ff00'))

if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedServerCredentialScanner(root)
    root.mainloop()
