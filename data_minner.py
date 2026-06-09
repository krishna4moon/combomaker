import os
import re
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox, simpledialog
import threading
from queue import Queue
import traceback
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys
from collections import defaultdict
import hashlib

class CredentialScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 COMBO MAKER BY KRISHNA - ULTIMATE EDITION v6.3")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        self.root.resizable(True, True)
        self.root.configure(bg='#1a1a2e')
        
        # Data storage - All Types
        self.unique_android = {}
        self.unique_phone = {}
        self.unique_indian_phone = {}
        self.unique_email = {}
        self.unique_url = {}
        self.all_combos = {}
        self.android_package_combos = {}
        self.host_combos = {}
        
        # Advanced Sensitive Data Storage
        self.social_media = defaultdict(set)
        self.bank_accounts = defaultdict(set)
        self.api_keys = defaultdict(set)
        self.crypto_wallets = defaultdict(set)
        self.leaked_hashes = defaultdict(set)
        self.jwt_tokens = set()
        self.oauth_tokens = defaultdict(set)
        self.session_cookies = defaultdict(set)
        self.credit_cards = defaultdict(set)
        self.credit_cards_detailed = []  # Store card details with expiry, cvv, type
        self.bank_logins = defaultdict(set)
        self.payment_gateways = defaultdict(set)
        self.database_credentials = defaultdict(set)
        self.cloud_credentials = defaultdict(set)
        self.private_keys = defaultdict(set)
        self.backup_codes = set()
        self.vpn_configs = defaultdict(set)
        self.ssh_keys = set()
        self.wifi_credentials = defaultdict(set)
        self.discord_tokens = set()
        self.telegram_tokens = set()
        self.slack_tokens = set()
        
        # NEW: Gift Cards, Promo Codes, Vouchers
        self.gift_cards = defaultdict(set)  # type -> set of codes
        self.promo_codes = defaultdict(set)  # platform -> set of codes
        self.vouchers = defaultdict(set)  # type -> set of codes
        self.coupons = defaultdict(set)  # store -> set of coupons
        self.reward_codes = set()  # generic reward codes
        
        # Gift card patterns by brand
        self.gift_card_patterns = {
            'amazon': [r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}', r'[A-Z0-9]{16,20}'],
            'google_play': [r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}'],
            'itunes': [r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}'],
            'steam': [r'[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}'],
            'netflix': [r'[A-Z0-9]{10,20}', r'Gift\s*Code:\s*([A-Z0-9-]+)'],
            'spotify': [r'[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}'],
            'playstation': [r'[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}'],
            'xbox': [r'[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}'],
            'target': [r'TGT[0-9]{12}', r'[0-9]{16}'],
            'walmart': [r'[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}'],
            'starbucks': [r'[0-9]{16}', r'[A-Z0-9]{8}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{12}'],
            'visa_gift': [r'[0-9]{16}', r'[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{4}'],
            'mastercard_gift': [r'5[1-5][0-9]{14}', r'2[2-7][0-9]{14}'],
            'amex_gift': [r'3[47][0-9]{13}'],
            'discover_gift': [r'6011[0-9]{12}']
        }
        
        # Promo code patterns
        self.promo_patterns = {
            'amazon': [r'PROMO[0-9A-Z]{8,}', r'[A-Z0-9]{5,10}'],
            'flipkart': [r'FLIPKART[A-Z0-9]{6,}', r'[A-Z]{2}[0-9]{12}'],
            'myntra': [r'MYNTRA[0-9]{6,}', r'[A-Z0-9]{8,15}'],
            'zomato': [r'ZOMATO[A-Z0-9]{6,}', r'[A-Z0-9]{8}'],
            'swiggy': [r'SWIGGY[A-Z0-9]{6,}', r'[A-Z0-9]{6,12}'],
            'uber': [r'UBER[A-Z0-9]{6,}', r'[A-Z0-9]{6,10}'],
            'generic': [r'(?:promo|code|coupon)\s*[:=]\s*([A-Z0-9]{6,20})']
        }
        
        # Voucher patterns
        self.voucher_patterns = {
            'hotel': [r'HOTEL[0-9]{6,}', r'[A-Z]{2}[0-9]{8,12}'],
            'travel': [r'TRAVEL[A-Z0-9]{6,}', r'[A-Z0-9]{8,16}'],
            'event': [r'EVENT[0-9]{6,}', r'TICKET[0-9]{8,}'],
            'generic': [r'(?:voucher|code)\s*[:=]\s*([A-Z0-9]{6,20})']
        }
        
        # Key search storage
        self.keyword_matches = {}
        self.search_keywords = []
        
        # Threading controls
        self.scanning = False
        self.pause_scan = False
        self.stop_scan = False
        self.queue = Queue()
        self.executor = None
        self.batch_size = 30
        
        # Settings
        self.settings_file = self.get_settings_path()
        self.max_threads = 15
        self.output_location = ""
        self.exclude_folders = ['cookies', 'cache', 'temp', 'tmp', 'backup', 'old', 'logs', 'node_modules']
        self.min_length = 3
        self.max_length = 100
        self.smart_filter = True
        self.extract_hashes = True
        self.extract_jwt = True
        self.extract_financial = True
        self.extract_gift_cards = True
        self.verify_credit_cards = True
        
        # Statistics
        self.skipped_files = []
        self.error_count = 0
        self.processed_files = 0
        self.total_credentials = 0
        self.filtered_count = 0
        
        # Sensitive data counters
        self.social_count = 0
        self.bank_count = 0
        self.api_count = 0
        self.crypto_count = 0
        self.hash_count = 0
        self.jwt_count = 0
        self.oauth_count = 0
        self.cookie_count = 0
        self.card_count = 0
        self.bank_login_count = 0
        self.payment_count = 0
        self.db_count = 0
        self.cloud_count = 0
        self.private_key_count = 0
        self.backup_code_count = 0
        self.ssh_key_count = 0
        self.wifi_count = 0
        self.discord_count = 0
        self.telegram_count = 0
        
        # NEW counters
        self.gift_card_count = 0
        self.promo_count = 0
        self.voucher_count = 0
        
        self.lock = threading.Lock()
        
        # Performance
        self.scan_start_time = None
        self.scan_end_time = None
        self.current_output_folder = None
        
        # Load settings
        self.load_settings()
        
        self.setup_ui()
        self.apply_styles()
        
        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)
        self.start_queue_processor()
    
    def get_settings_path(self):
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(application_path, 'combo_maker_settings.json')
    
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.max_threads = settings.get('max_threads', 15)
                    self.output_location = settings.get('output_location', '')
                    self.exclude_folders = settings.get('exclude_folders', ['cookies', 'cache', 'temp', 'tmp'])
                    self.min_length = settings.get('min_length', 3)
                    self.max_length = settings.get('max_length', 100)
                    self.search_keywords = settings.get('search_keywords', [])
                    self.smart_filter = settings.get('smart_filter', True)
                    self.extract_hashes = settings.get('extract_hashes', True)
                    self.extract_jwt = settings.get('extract_jwt', True)
                    self.extract_financial = settings.get('extract_financial', True)
                    self.extract_gift_cards = settings.get('extract_gift_cards', True)
                    self.verify_credit_cards = settings.get('verify_credit_cards', True)
        except:
            pass
    
    def save_settings(self):
        try:
            settings = {
                'max_threads': self.max_threads,
                'output_location': self.output_location,
                'exclude_folders': self.exclude_folders,
                'min_length': self.min_length,
                'max_length': self.max_length,
                'search_keywords': self.search_keywords,
                'smart_filter': self.smart_filter,
                'extract_hashes': self.extract_hashes,
                'extract_jwt': self.extract_jwt,
                'extract_financial': self.extract_financial,
                'extract_gift_cards': self.extract_gift_cards,
                'verify_credit_cards': self.verify_credit_cards
            }
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)
            return True
        except:
            return False
    
    def get_datetime_folder(self):
        now = datetime.now()
        timestamp = now.strftime("%d%b%Y_%I%M%p").upper()
        timestamp = re.sub(r'^0', '', timestamp)
        return f"COMBO_MAKER_{timestamp}"
    
    def get_output_folder(self):
        if self.output_location and os.path.exists(self.output_location):
            base_folder = self.output_location
        else:
            if getattr(sys, 'frozen', False):
                base_folder = os.path.dirname(sys.executable)
            else:
                base_folder = os.path.dirname(os.path.abspath(__file__))
        
        datetime_folder = self.get_datetime_folder()
        output_folder = os.path.join(base_folder, datetime_folder)
        os.makedirs(output_folder, exist_ok=True)
        
        os.makedirs(os.path.join(output_folder, "CREDENTIALS"), exist_ok=True)
        os.makedirs(os.path.join(output_folder, "SENSITIVE_DATA"), exist_ok=True)
        os.makedirs(os.path.join(output_folder, "ANDROID_COMBOS"), exist_ok=True)
        os.makedirs(os.path.join(output_folder, "GIFT_CARDS_VOUCHERS"), exist_ok=True)
        
        self.current_output_folder = output_folder
        return output_folder
    
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
        style.configure('TNotebook', background='#1a1a2e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#0f3460', foreground='#00ff88', padding=[15, 5])
        style.map('TNotebook.Tab', background=[('selected', '#00ff88')], foreground=[('selected', '#1a1a2e')])
    
    def setup_ui(self):
        self.root.configure(bg='#1a1a2e')
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.main_container = tk.Frame(self.root, bg='#1a1a2e')
        self.main_container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        self.main_container.grid_rowconfigure(3, weight=3)
        self.main_container.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = tk.Frame(self.main_container, bg='#1a1a2e')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))
        
        title_label = tk.Label(header_frame, text="⚡ COMBO MAKER BY KRISHNA - ULTIMATE EDITION v6.3 ⚡", 
                                font=('Segoe UI', 18, 'bold'), fg='#00ff88', bg='#1a1a2e')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame, text="Captures ALL Combos | Gift Cards | Promo Codes | Credit Card Verification", 
                                   font=('Segoe UI', 9), fg='#888888', bg='#1a1a2e')
        subtitle_label.pack()
        
        # Input Frame
        input_frame = tk.LabelFrame(self.main_container, text=" INPUT SELECTION ", font=('Segoe UI', 11, 'bold'),
                                     fg='#00ff88', bg='#1a1a2e', bd=2, relief=tk.RIDGE)
        input_frame.grid(row=1, column=0, sticky='ew', pady=(0, 10), ipady=8)
        
        # Row 1: Folder Path
        path_frame = tk.Frame(input_frame, bg='#1a1a2e')
        path_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(path_frame, text="📁 Input Folder:", font=('Segoe UI', 10), 
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
        
        # Row 2: Settings
        settings_frame = tk.Frame(input_frame, bg='#1a1a2e')
        settings_frame.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Label(settings_frame, text="🧵 Threads:", font=('Segoe UI', 10), 
                fg='#eeeeee', bg='#1a1a2e').pack(side=tk.LEFT, padx=(0, 5))
        
        self.threads_var = tk.IntVar(value=self.max_threads)
        self.threads_spinbox = tk.Spinbox(settings_frame, from_=1, to=32, width=5,
                                          textvariable=self.threads_var,
                                          bg='#0f3460', fg='#eeeeee', font=('Segoe UI', 10))
        self.threads_spinbox.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(settings_frame, text="Min Len:", font=('Segoe UI', 10), 
                fg='#eeeeee', bg='#1a1a2e').pack(side=tk.LEFT, padx=(0, 5))
        
        self.min_len_var = tk.IntVar(value=self.min_length)
        self.min_len_spinbox = tk.Spinbox(settings_frame, from_=1, to=10, width=3,
                                          textvariable=self.min_len_var,
                                          bg='#0f3460', fg='#eeeeee', font=('Segoe UI', 10))
        self.min_len_spinbox.pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Label(settings_frame, text="Max Len:", font=('Segoe UI', 10), 
                fg='#eeeeee', bg='#1a1a2e').pack(side=tk.LEFT, padx=(0, 5))
        
        self.max_len_var = tk.IntVar(value=self.max_length)
        self.max_len_spinbox = tk.Spinbox(settings_frame, from_=10, to=200, width=4,
                                          textvariable=self.max_len_var,
                                          bg='#0f3460', fg='#eeeeee', font=('Segoe UI', 10))
        self.max_len_spinbox.pack(side=tk.LEFT)
        
        # Row 3: Checkboxes
        checkbox_frame = tk.Frame(input_frame, bg='#1a1a2e')
        checkbox_frame.pack(fill=tk.X, padx=15, pady=5)
        
        self.smart_filter_var = tk.BooleanVar(value=self.smart_filter)
        smart_check = tk.Checkbutton(checkbox_frame, text="🔍 Smart Filter", variable=self.smart_filter_var,
                                      command=self.toggle_smart_filter, bg='#1a1a2e', fg='#00ff88',
                                      selectcolor='#1a1a2e', activebackground='#1a1a2e')
        smart_check.pack(side=tk.LEFT, padx=10)
        
        self.jwt_extract_var = tk.BooleanVar(value=self.extract_jwt)
        jwt_check = tk.Checkbutton(checkbox_frame, text="🎫 Extract JWT", variable=self.jwt_extract_var,
                                    command=self.toggle_jwt_extract, bg='#1a1a2e', fg='#00ff88',
                                    selectcolor='#1a1a2e', activebackground='#1a1a2e')
        jwt_check.pack(side=tk.LEFT, padx=10)
        
        self.hash_extract_var = tk.BooleanVar(value=self.extract_hashes)
        hash_check = tk.Checkbutton(checkbox_frame, text="🔒 Extract Hashes", variable=self.hash_extract_var,
                                     command=self.toggle_hash_extract, bg='#1a1a2e', fg='#00ff88',
                                     selectcolor='#1a1a2e', activebackground='#1a1a2e')
        hash_check.pack(side=tk.LEFT, padx=10)
        
        self.financial_extract_var = tk.BooleanVar(value=self.extract_financial)
        financial_check = tk.Checkbutton(checkbox_frame, text="💳 Financial Data", variable=self.financial_extract_var,
                                          command=self.toggle_financial_extract, bg='#1a1a2e', fg='#00ff88',
                                          selectcolor='#1a1a2e', activebackground='#1a1a2e')
        financial_check.pack(side=tk.LEFT, padx=10)
        
        self.gift_extract_var = tk.BooleanVar(value=self.extract_gift_cards)
        gift_check = tk.Checkbutton(checkbox_frame, text="🎁 Gift Cards", variable=self.gift_extract_var,
                                     command=self.toggle_gift_extract, bg='#1a1a2e', fg='#00ff88',
                                     selectcolor='#1a1a2e', activebackground='#1a1a2e')
        gift_check.pack(side=tk.LEFT, padx=10)
        
        apply_btn = tk.Button(checkbox_frame, text="APPLY", command=self.apply_quick_settings,
                               font=('Segoe UI', 9, 'bold'), bg='#00ff88', fg='#1a1a2e',
                               activebackground='#00cc66', activeforeground='#1a1a2e',
                               relief=tk.RAISED, bd=1, padx=15, pady=3)
        apply_btn.pack(side=tk.RIGHT, padx=10)
        
        # Row 4: Control Buttons
        btn_frame = tk.Frame(input_frame, bg='#1a1a2e')
        btn_frame.pack(pady=10)
        
        self.scan_btn = tk.Button(btn_frame, text="🚀 START SCAN", command=self.start_scan,
                                   font=('Segoe UI', 12, 'bold'), bg='#00ff88', fg='#1a1a2e',
                                   activebackground='#00cc66', activeforeground='#1a1a2e',
                                   relief=tk.RAISED, bd=2, padx=30, pady=8)
        self.scan_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = tk.Button(btn_frame, text="⏸ PAUSE", command=self.pause_scanning,
                                    font=('Segoe UI', 10, 'bold'), bg='#ff6600', fg='#ffffff',
                                    activebackground='#cc5500', activeforeground='#ffffff',
                                    relief=tk.RAISED, bd=2, padx=20, pady=8, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(btn_frame, text="⏹ STOP", command=self.stop_scanning,
                                   font=('Segoe UI', 10, 'bold'), bg='#ff0000', fg='#ffffff',
                                   activebackground='#cc0000', activeforeground='#ffffff',
                                   relief=tk.RAISED, bd=2, padx=20, pady=8, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress Frame
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
        
        # Counter Frame
        counter_frame = tk.Frame(progress_frame, bg='#1a1a2e')
        counter_frame.pack(pady=5)
        
        self.files_counter = tk.Label(counter_frame, text="📄 Files: 0", font=('Segoe UI', 9, 'bold'),
                                       fg='#00ff88', bg='#1a1a2e')
        self.files_counter.pack(side=tk.LEFT, padx=10)
        
        self.creds_counter = tk.Label(counter_frame, text="🔑 Creds: 0", font=('Segoe UI', 9, 'bold'),
                                       fg='#ffff00', bg='#1a1a2e')
        self.creds_counter.pack(side=tk.LEFT, padx=10)
        
        self.filtered_counter = tk.Label(counter_frame, text="🚫 Filtered: 0", font=('Segoe UI', 9, 'bold'),
                                          fg='#ff6600', bg='#1a1a2e')
        self.filtered_counter.pack(side=tk.LEFT, padx=10)
        
        self.errors_counter = tk.Label(counter_frame, text="⚠️ Errors: 0", font=('Segoe UI', 9, 'bold'),
                                        fg='#ff0000', bg='#1a1a2e')
        self.errors_counter.pack(side=tk.LEFT, padx=10)
        
        self.thread_status = tk.Label(counter_frame, text="", font=('Segoe UI', 9, 'bold'),
                                       fg='#00ff88', bg='#1a1a2e')
        self.thread_status.pack(side=tk.LEFT, padx=10)
        
        # Create Notebook for Tabs
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.grid(row=3, column=0, sticky='nsew', pady=(0, 10))
        
        # Tab 1: Console Output
        console_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(console_tab, text="📝 CONSOLE OUTPUT")
        
        text_frame = tk.Frame(console_tab, bg='#1a1a2e')
        text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(text_frame, height=15, 
                                                    font=('Consolas', 9), bg='#0a0a0a', fg='#00ff88',
                                                    insertbackground='#00ff88', relief=tk.FLAT,
                                                    wrap=tk.WORD, bd=0)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_text.tag_config("success", foreground="#00ff88")
        self.log_text.tag_config("error", foreground="#ff0000")
        self.log_text.tag_config("warning", foreground="#ffaa00")
        self.log_text.tag_config("info", foreground="#00aaff")
        self.log_text.tag_config("found", foreground="#ffff00")
        self.log_text.tag_config("critical", foreground="#ff00ff")
        
        console_bottom = tk.Frame(console_tab, bg='#1a1a2e')
        console_bottom.pack(fill=tk.X, pady=5)
        
        self.auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = tk.Checkbutton(console_bottom, text="Auto-scroll", variable=self.auto_scroll_var,
                                           bg='#1a1a2e', fg='#00ff88', selectcolor='#1a1a2e')
        auto_scroll_check.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(console_bottom, text="CLEAR", command=self.clear_output,
                               font=('Segoe UI', 9, 'bold'), bg='#0f3460', fg='#ff6600',
                               activebackground='#16213e', padx=15, pady=3)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        save_log_btn = tk.Button(console_bottom, text="SAVE LOG", command=self.save_full_log,
                                  font=('Segoe UI', 9, 'bold'), bg='#0f3460', fg='#00ff88',
                                  activebackground='#16213e', padx=15, pady=3)
        save_log_btn.pack(side=tk.LEFT, padx=5)
        
        # Tab 2: Keyword Searcher
        self.keyword_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(self.keyword_tab, text="🔎 KEYWORD SEARCHER")
        self.setup_keyword_searcher()
        
        # Tab 3: Sensitive Data
        sensitive_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(sensitive_tab, text="🔐 SENSITIVE DATA")
        self.setup_sensitive_tab(sensitive_tab)
        
        # Tab 4: Gift Cards & Vouchers
        gift_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(gift_tab, text="🎁 GIFT CARDS & VOUCHERS")
        self.setup_gift_tab(gift_tab)
        
        # Tab 5: Statistics
        stats_tab = tk.Frame(self.notebook, bg='#1a1a2e')
        self.notebook.add(stats_tab, text="📊 STATISTICS")
        
        stats_text_frame = tk.Frame(stats_tab, bg='#1a1a2e')
        stats_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_text_frame, font=('Consolas', 10), 
                                   bg='#0a0a0a', fg='#ffaa00', relief=tk.FLAT, bd=0,
                                   wrap=tk.WORD)
        self.stats_text.pack(fill=tk.BOTH, expand=True)
        
        refresh_stats_btn = tk.Button(stats_tab, text="REFRESH STATS", command=self.refresh_stats,
                                       font=('Segoe UI', 9, 'bold'), bg='#0f3460', fg='#00ff88',
                                       activebackground='#16213e', padx=15, pady=3)
        refresh_stats_btn.pack(pady=5)
    
    def setup_gift_tab(self, parent):
        """Setup the Gift Cards & Vouchers display tab"""
        main_frame = tk.Frame(parent, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for different gift types
        gift_notebook = ttk.Notebook(main_frame)
        gift_notebook.pack(fill=tk.BOTH, expand=True)
        
        tabs_config = [
            ("🎁 Gift Cards", "gift_cards"),
            ("🏷️ Promo Codes", "promo_codes"),
            ("🎫 Vouchers", "vouchers"),
            ("💰 Coupons", "coupons")
        ]
        
        self.gift_texts = {}
        
        for tab_name, key in tabs_config:
            frame = tk.Frame(gift_notebook, bg='#1a1a2e')
            gift_notebook.add(frame, text=tab_name)
            
            text_frame = tk.Frame(frame, bg='#1a1a2e')
            text_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
            
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, bg='#0a0a0a', fg='#00ff88', font=('Consolas', 9),
                                   wrap=tk.WORD, yscrollcommand=scrollbar.set)
            text_widget.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=text_widget.yview)
            
            self.gift_texts[key] = text_widget
        
        refresh_btn = tk.Button(parent, text="🔄 REFRESH GIFT DATA", command=self.refresh_gift_display,
                                 bg='#0f3460', fg='#00ff88', font=('Segoe UI', 9, 'bold'), padx=15, pady=3)
        refresh_btn.pack(pady=5)
    
    def setup_keyword_searcher(self):
        main_frame = tk.Frame(self.keyword_tab, bg='#1a1a2e')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left_panel = tk.Frame(main_frame, bg='#1a1a2e', width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        keywords_frame = tk.LabelFrame(left_panel, text=" KEYWORDS (one per line) ", 
                                        font=('Segoe UI', 10, 'bold'), fg='#00ff88', bg='#1a1a2e')
        keywords_frame.pack(fill=tk.BOTH, expand=True)
        
        self.keywords_text = tk.Text(keywords_frame, height=15, width=35, bg='#0f3460', fg='#00ff88', 
                                      insertbackground='#00ff88', font=('Consolas', 10), relief=tk.FLAT, bd=0)
        self.keywords_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if self.search_keywords:
            self.keywords_text.insert(1.0, '\n'.join(self.search_keywords))
        
        btn_frame = tk.Frame(keywords_frame, bg='#1a1a2e')
        btn_frame.pack(pady=5)
        
        load_btn = tk.Button(btn_frame, text="📂 LOAD FILE", command=self.load_keywords_from_file,
                              bg='#0f3460', fg='#00ff88', font=('Segoe UI', 9, 'bold'), padx=10)
        load_btn.pack(side=tk.LEFT, padx=2)
        
        save_btn = tk.Button(btn_frame, text="💾 SAVE", command=self.save_keywords,
                              bg='#0f3460', fg='#00ff88', font=('Segoe UI', 9, 'bold'), padx=10)
        save_btn.pack(side=tk.LEFT, padx=2)
        
        clear_btn = tk.Button(btn_frame, text="🗑 CLEAR", command=self.clear_keywords,
                               bg='#0f3460', fg='#ff6600', font=('Segoe UI', 9, 'bold'), padx=10)
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        search_btn = tk.Button(btn_frame, text="🔎 START SEARCH", command=self.start_keyword_search,
                                bg='#00ff88', fg='#1a1a2e', font=('Segoe UI', 10, 'bold'), padx=20)
        search_btn.pack(side=tk.LEFT, padx=10)
        
        right_panel = tk.Frame(main_frame, bg='#1a1a2e')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        results_frame = tk.LabelFrame(right_panel, text=" SEARCH RESULTS ", 
                                       font=('Segoe UI', 10, 'bold'), fg='#00ff88', bg='#1a1a2e')
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        results_text_frame = tk.Frame(results_frame, bg='#1a1a2e')
        results_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        results_scrollbar = tk.Scrollbar(results_text_frame)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_text = tk.Text(results_text_frame, height=15, bg='#0a0a0a', fg='#00ff88', font=('Consolas', 9),
                                     wrap=tk.WORD, yscrollcommand=results_scrollbar.set)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        results_scrollbar.config(command=self.results_text.yview)
        
        export_btn = tk.Button(results_frame, text="📥 EXPORT RESULTS", command=self.export_keyword_results,
                                bg='#ffaa00', fg='#1a1a2e', font=('Segoe UI', 10, 'bold'), padx=15, pady=5)
        export_btn.pack(pady=5)
    
    def setup_sensitive_tab(self, parent):
        sensitive_notebook = ttk.Notebook(parent)
        sensitive_notebook.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        tabs_config = [
            ("🎫 JWT TOKENS", "jwt"),
            ("🔐 API KEYS", "api"),
            ("💳 CREDIT CARDS", "cards"),
            ("💰 CRYPTO WALLETS", "crypto"),
            ("🔒 HASHES", "hashes"),
            ("💬 DISCORD TOKENS", "discord"),
            ("📨 TELEGRAM TOKENS", "telegram")
        ]
        
        self.sensitive_texts = {}
        
        for tab_name, key in tabs_config:
            frame = tk.Frame(sensitive_notebook, bg='#1a1a2e')
            sensitive_notebook.add(frame, text=tab_name)
            
            text_frame = tk.Frame(frame, bg='#1a1a2e')
            text_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
            
            scrollbar = tk.Scrollbar(text_frame)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_widget = tk.Text(text_frame, bg='#0a0a0a', fg='#00ff88', font=('Consolas', 9),
                                   wrap=tk.WORD, yscrollcommand=scrollbar.set)
            text_widget.pack(fill=tk.BOTH, expand=True)
            scrollbar.config(command=text_widget.yview)
            
            self.sensitive_texts[key] = text_widget
        
        refresh_btn = tk.Button(parent, text="🔄 REFRESH SENSITIVE DATA", command=self.refresh_sensitive_display,
                                 bg='#0f3460', fg='#00ff88', font=('Segoe UI', 9, 'bold'), padx=15, pady=3)
        refresh_btn.pack(pady=5)
    
    def start_queue_processor(self):
        try:
            for _ in range(100):
                try:
                    msg = self.queue.get_nowait()
                    self.process_message(msg)
                except:
                    break
        finally:
            self.root.after(50, self.start_queue_processor)
    
    def process_message(self, msg):
        try:
            if msg[0] == 'log':
                text = msg[1]
                tag = msg[2] if len(msg) > 2 else None
                if tag and tag in self.log_text.tag_names():
                    self.log_text.insert(tk.END, text + '\n', tag)
                else:
                    self.log_text.insert(tk.END, text + '\n')
                if self.auto_scroll_var.get():
                    self.log_text.see(tk.END)
                self.root.update_idletasks()
                
            elif msg[0] == 'stats':
                self.stats_text.delete(1.0, tk.END)
                self.stats_text.insert(tk.END, msg[1])
                self.root.update_idletasks()
                
            elif msg[0] == 'progress':
                self.progress_var.set(msg[1])
                self.status_label.config(text=msg[2])
                self.current_file_label.config(text=msg[3][:70] if msg[3] else "")
                self.root.update_idletasks()
                
            elif msg[0] == 'counters':
                self.files_counter.config(text=f"📄 Files: {msg[1]}")
                self.creds_counter.config(text=f"🔑 Creds: {msg[2]}")
                self.filtered_counter.config(text=f"🚫 Filtered: {msg[3]}")
                self.errors_counter.config(text=f"⚠️ Errors: {msg[4]}")
                self.root.update_idletasks()
                
            elif msg[0] == 'threads':
                self.thread_status.config(text=f"🧵 Active: {msg[1]}")
                self.root.update_idletasks()
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.log(f"✅ Selected folder: {folder}", "success")
    
    def toggle_smart_filter(self):
        self.smart_filter = self.smart_filter_var.get()
        self.save_settings()
        self.log(f"🔍 Smart filtering {'ENABLED' if self.smart_filter else 'DISABLED'}", "info")
    
    def toggle_jwt_extract(self):
        self.extract_jwt = self.jwt_extract_var.get()
        self.save_settings()
        self.log(f"🎫 JWT extraction {'ENABLED' if self.extract_jwt else 'DISABLED'}", "info")
    
    def toggle_hash_extract(self):
        self.extract_hashes = self.hash_extract_var.get()
        self.save_settings()
        self.log(f"🔒 Hash extraction {'ENABLED' if self.extract_hashes else 'DISABLED'}", "info")
    
    def toggle_financial_extract(self):
        self.extract_financial = self.financial_extract_var.get()
        self.save_settings()
        self.log(f"💳 Financial data extraction {'ENABLED' if self.extract_financial else 'DISABLED'}", "info")
    
    def toggle_gift_extract(self):
        self.extract_gift_cards = self.gift_extract_var.get()
        self.save_settings()
        self.log(f"🎁 Gift card extraction {'ENABLED' if self.extract_gift_cards else 'DISABLED'}", "info")
    
    def apply_quick_settings(self):
        self.max_threads = self.threads_var.get()
        self.min_length = self.min_len_var.get()
        self.max_length = self.max_len_var.get()
        
        if self.min_length >= self.max_length:
            self.log(f"❌ Min length must be less than max length!", "error")
            return
        
        self.save_settings()
        self.log(f"✅ Settings applied: {self.max_threads} threads, {self.min_length}-{self.max_length} chars", "success")
    
    def load_keywords_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Keywords File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.keywords_text.delete(1.0, tk.END)
                    self.keywords_text.insert(1.0, content)
                self.log(f"✅ Loaded keywords from {os.path.basename(file_path)}", "success")
            except Exception as e:
                self.log(f"❌ Failed to load: {str(e)}", "error")
    
    def save_keywords(self):
        content = self.keywords_text.get(1.0, tk.END).strip()
        if not content:
            self.log(f"⚠️ No keywords to save", "warning")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Keywords",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.search_keywords = [k.strip().lower() for k in content.splitlines() if k.strip()]
                self.save_settings()
                self.log(f"✅ Keywords saved to {os.path.basename(file_path)}", "success")
            except Exception as e:
                self.log(f"❌ Failed to save: {str(e)}", "error")
    
    def clear_keywords(self):
        self.keywords_text.delete(1.0, tk.END)
        self.log(f"🗑 Cleared all keywords", "info")
    
    def start_keyword_search(self):
        keyword_text = self.keywords_text.get(1.0, tk.END).strip()
        if not keyword_text:
            self.log(f"⚠️ Please enter keywords to search", "warning")
            return
        
        keywords = [k.strip().lower() for k in keyword_text.splitlines() if k.strip()]
        self.search_keywords = keywords
        self.save_settings()
        
        if not self.all_combos and not self.unique_android and not self.unique_url:
            self.log(f"⚠️ No credentials loaded. Run a scan first.", "warning")
            return
        
        self.results_text.delete(1.0, tk.END)
        self.keyword_matches = {}
        
        self.results_text.insert(tk.END, "="*70 + "\n")
        self.results_text.insert(tk.END, "🔎 KEYWORD SEARCH RESULTS\n")
        self.results_text.insert(tk.END, "="*70 + "\n\n")
        self.results_text.insert(tk.END, f"📝 Keywords: {', '.join(keywords)}\n")
        self.results_text.insert(tk.END, f"🔍 Scanning {len(self.all_combos)} credentials...\n\n")
        
        total_matches = 0
        
        for keyword in keywords:
            matches = []
            
            for key in self.unique_android.keys():
                if keyword in key.lower():
                    if ':' in key:
                        username_part = key.split(':', 1)[1] if ':' in key else key
                        if keyword in username_part.lower():
                            matches.append(f"[ANDROID] {key}:{self.unique_android[key]}")
            
            for key in self.unique_url.keys():
                if keyword in key.lower():
                    matches.append(f"[URL] {key}:{self.unique_url[key]}")
            
            for username, password in self.all_combos.items():
                if keyword in username.lower():
                    matches.append(f"[COMBO] {username}:{password}")
            
            for email, password in self.unique_email.items():
                if keyword in email.lower():
                    matches.append(f"[EMAIL] {email}:{password}")
            
            if matches:
                self.keyword_matches[keyword] = matches
                total_matches += len(matches)
                
                self.results_text.insert(tk.END, f"\n{'─'*50}\n")
                self.results_text.insert(tk.END, f"🔑 KEYWORD: '{keyword}' - {len(matches)} matches\n")
                self.results_text.insert(tk.END, f"{'─'*50}\n")
                for match in matches[:100]:
                    self.results_text.insert(tk.END, f"  • {match}\n")
                if len(matches) > 100:
                    self.results_text.insert(tk.END, f"  ... and {len(matches)-100} more\n")
        
        self.results_text.insert(tk.END, f"\n{'='*70}\n")
        self.results_text.insert(tk.END, f"✅ SEARCH COMPLETE - {total_matches} total matches\n")
        self.results_text.insert(tk.END, f"{'='*70}\n")
        
        self.log(f"✅ Keyword search complete: {total_matches} matches found", "success")
    
    def export_keyword_results(self):
        if not self.keyword_matches:
            self.log(f"⚠️ No search results to export", "warning")
            return
        
        output_folder = self.get_output_folder()
        keyword_folder = os.path.join(output_folder, "KEYWORD_SEARCH_RESULTS")
        os.makedirs(keyword_folder, exist_ok=True)
        
        for keyword, matches in self.keyword_matches.items():
            safe_keyword = re.sub(r'[<>:"/\\|?*]', '_', keyword)
            file_path = os.path.join(keyword_folder, f"{safe_keyword}_matches.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                for match in matches:
                    clean_match = re.sub(r'^\[(ANDROID|URL|COMBO|EMAIL)\] ', '', match)
                    f.write(clean_match + "\n")
        
        self.log(f"✅ Exported {len(self.keyword_matches)} keyword results", "success")
        messagebox.showinfo("Export Complete", f"Results exported to:\n{keyword_folder}")
    
    def refresh_gift_display(self):
        """Refresh the Gift Cards & Vouchers display"""
        try:
            if 'gift_cards' in self.gift_texts:
                self.gift_texts['gift_cards'].delete(1.0, tk.END)
                for card_type, cards in self.gift_cards.items():
                    self.gift_texts['gift_cards'].insert(tk.END, f"\n┌{'─'*60}┐\n")
                    self.gift_texts['gift_cards'].insert(tk.END, f"│ 🎁 {card_type.upper()} GIFT CARDS ({len(cards)} found)\n")
                    self.gift_texts['gift_cards'].insert(tk.END, f"└{'─'*60}┘\n")
                    for card in list(cards)[:500]:
                        self.gift_texts['gift_cards'].insert(tk.END, f"  • {card}\n")
                    if len(cards) > 500:
                        self.gift_texts['gift_cards'].insert(tk.END, f"  ... and {len(cards)-500} more\n")
                    self.gift_texts['gift_cards'].insert(tk.END, "\n")
            
            if 'promo_codes' in self.gift_texts:
                self.gift_texts['promo_codes'].delete(1.0, tk.END)
                for platform, codes in self.promo_codes.items():
                    self.gift_texts['promo_codes'].insert(tk.END, f"\n┌{'─'*60}┐\n")
                    self.gift_texts['promo_codes'].insert(tk.END, f"│ 🏷️ {platform.upper()} PROMO CODES ({len(codes)} found)\n")
                    self.gift_texts['promo_codes'].insert(tk.END, f"└{'─'*60}┘\n")
                    for code in list(codes)[:500]:
                        self.gift_texts['promo_codes'].insert(tk.END, f"  • {code}\n")
                    if len(codes) > 500:
                        self.gift_texts['promo_codes'].insert(tk.END, f"  ... and {len(codes)-500} more\n")
                    self.gift_texts['promo_codes'].insert(tk.END, "\n")
            
            if 'vouchers' in self.gift_texts:
                self.gift_texts['vouchers'].delete(1.0, tk.END)
                for voucher_type, vouchers in self.vouchers.items():
                    self.gift_texts['vouchers'].insert(tk.END, f"\n┌{'─'*60}┐\n")
                    self.gift_texts['vouchers'].insert(tk.END, f"│ 🎫 {voucher_type.upper()} VOUCHERS ({len(vouchers)} found)\n")
                    self.gift_texts['vouchers'].insert(tk.END, f"└{'─'*60}┘\n")
                    for voucher in list(vouchers)[:500]:
                        self.gift_texts['vouchers'].insert(tk.END, f"  • {voucher}\n")
                    if len(vouchers) > 500:
                        self.gift_texts['vouchers'].insert(tk.END, f"  ... and {len(vouchers)-500} more\n")
                    self.gift_texts['vouchers'].insert(tk.END, "\n")
            
            if 'coupons' in self.gift_texts:
                self.gift_texts['coupons'].delete(1.0, tk.END)
                for store, coupons in self.coupons.items():
                    self.gift_texts['coupons'].insert(tk.END, f"\n┌{'─'*60}┐\n")
                    self.gift_texts['coupons'].insert(tk.END, f"│ 💰 {store.upper()} COUPONS ({len(coupons)} found)\n")
                    self.gift_texts['coupons'].insert(tk.END, f"└{'─'*60}┘\n")
                    for coupon in list(coupons)[:500]:
                        self.gift_texts['coupons'].insert(tk.END, f"  • {coupon}\n")
                    if len(coupons) > 500:
                        self.gift_texts['coupons'].insert(tk.END, f"  ... and {len(coupons)-500} more\n")
                    self.gift_texts['coupons'].insert(tk.END, "\n")
                    
        except Exception as e:
            self.log(f"⚠️ Error refreshing gift display: {str(e)}", "warning")
    
    def refresh_sensitive_display(self):
        try:
            if 'jwt' in self.sensitive_texts:
                self.sensitive_texts['jwt'].delete(1.0, tk.END)
                if self.jwt_tokens:
                    for token in list(self.jwt_tokens)[:500]:
                        self.sensitive_texts['jwt'].insert(tk.END, token + "\n")
                    if len(self.jwt_tokens) > 500:
                        self.sensitive_texts['jwt'].insert(tk.END, f"\n... and {len(self.jwt_tokens)-500} more\n")
            
            if 'discord' in self.sensitive_texts:
                self.sensitive_texts['discord'].delete(1.0, tk.END)
                if self.discord_tokens:
                    for token in list(self.discord_tokens)[:500]:
                        self.sensitive_texts['discord'].insert(tk.END, token + "\n")
                    if len(self.discord_tokens) > 500:
                        self.sensitive_texts['discord'].insert(tk.END, f"\n... and {len(self.discord_tokens)-500} more\n")
            
            if 'cards' in self.sensitive_texts:
                self.sensitive_texts['cards'].delete(1.0, tk.END)
                if self.credit_cards_detailed:
                    for card in self.credit_cards_detailed[:500]:
                        card_str = f"[{card['type'].upper()}] {card['number']}"
                        if card.get('expiry'):
                            card_str += f" | Exp: {card['expiry']}"
                        if card.get('cvv'):
                            card_str += f" | CVV: {card['cvv']}"
                        if card.get('valid'):
                            card_str += " | ✓ Valid (Luhn)"
                        else:
                            card_str += " | ✗ Invalid (Luhn)"
                        self.sensitive_texts['cards'].insert(tk.END, card_str + "\n")
                    if len(self.credit_cards_detailed) > 500:
                        self.sensitive_texts['cards'].insert(tk.END, f"\n... and {len(self.credit_cards_detailed)-500} more\n")
                elif self.credit_cards:
                    for card_type, cards in self.credit_cards.items():
                        for card in list(cards)[:100]:
                            self.sensitive_texts['cards'].insert(tk.END, f"[{card_type.upper()}] {card}\n")
            
            if 'api' in self.sensitive_texts:
                self.sensitive_texts['api'].delete(1.0, tk.END)
                for key_type, keys in self.api_keys.items():
                    self.sensitive_texts['api'].insert(tk.END, f"\n┌{'─'*60}┐\n")
                    self.sensitive_texts['api'].insert(tk.END, f"│ 🔑 {key_type.upper()} API KEYS ({len(keys)} found)\n")
                    self.sensitive_texts['api'].insert(tk.END, f"└{'─'*60}┘\n")
                    for key in list(keys)[:100]:
                        self.sensitive_texts['api'].insert(tk.END, f"  • {key}\n")
                    if len(keys) > 100:
                        self.sensitive_texts['api'].insert(tk.END, f"  ... and {len(keys)-100} more\n")
                    self.sensitive_texts['api'].insert(tk.END, "\n")
            
            if 'crypto' in self.sensitive_texts:
                self.sensitive_texts['crypto'].delete(1.0, tk.END)
                for wallet_type, addresses in self.crypto_wallets.items():
                    self.sensitive_texts['crypto'].insert(tk.END, f"\n┌{'─'*60}┐\n")
                    self.sensitive_texts['crypto'].insert(tk.END, f"│ 💰 {wallet_type.upper()} WALLETS ({len(addresses)} found)\n")
                    self.sensitive_texts['crypto'].insert(tk.END, f"└{'─'*60}┘\n")
                    for addr in list(addresses)[:100]:
                        self.sensitive_texts['crypto'].insert(tk.END, f"  • {addr}\n")
                    if len(addresses) > 100:
                        self.sensitive_texts['crypto'].insert(tk.END, f"  ... and {len(addresses)-100} more\n")
                    self.sensitive_texts['crypto'].insert(tk.END, "\n")
            
            if 'hashes' in self.sensitive_texts:
                self.sensitive_texts['hashes'].delete(1.0, tk.END)
                for hash_type, hashes in self.leaked_hashes.items():
                    self.sensitive_texts['hashes'].insert(tk.END, f"\n┌{'─'*60}┐\n")
                    self.sensitive_texts['hashes'].insert(tk.END, f"│ 🔒 {hash_type.upper()} HASHES ({len(hashes)} found)\n")
                    self.sensitive_texts['hashes'].insert(tk.END, f"└{'─'*60}┘\n")
                    for h in list(hashes)[:100]:
                        self.sensitive_texts['hashes'].insert(tk.END, f"  • {h}\n")
                    if len(hashes) > 100:
                        self.sensitive_texts['hashes'].insert(tk.END, f"  ... and {len(hashes)-100} more\n")
                    self.sensitive_texts['hashes'].insert(tk.END, "\n")
            
            if 'telegram' in self.sensitive_texts:
                self.sensitive_texts['telegram'].delete(1.0, tk.END)
                if self.telegram_tokens:
                    for token in list(self.telegram_tokens)[:500]:
                        self.sensitive_texts['telegram'].insert(tk.END, token + "\n")
                    if len(self.telegram_tokens) > 500:
                        self.sensitive_texts['telegram'].insert(tk.END, f"\n... and {len(self.telegram_tokens)-500} more\n")
                    
        except Exception as e:
            self.log(f"⚠️ Error refreshing display: {str(e)}", "warning")
    
    def refresh_stats(self):
        duration = ""
        if self.scan_start_time and self.scan_end_time:
            duration_sec = (self.scan_end_time - self.scan_start_time).total_seconds()
            duration = f"\n⏱️ Duration: {duration_sec:.2f} seconds"
        
        stats = f"""
{'='*70}
⚡ COMBO MAKER BY KRISHNA - ULTIMATE EDITION v6.3 ⚡
{'='*70}

📁 SCAN STATISTICS:
   📄 Files Processed....: {self.processed_files:,}
   🔑 Credentials Found..: {self.total_credentials:,}
   🚫 Filtered...........: {self.filtered_count:,}
   ⚠️ Errors.............: {self.error_count}{duration}

{'─'*70}
📊 CREDENTIALS BREAKDOWN:
   📦 Android Package Combos: {len(self.android_package_combos):,}
   📱 Android.........: {len(self.unique_android):,}
   🔗 URL.............: {len(self.unique_url):,}
   ✉️ Email...........: {len(self.unique_email):,}
   📞 Phone...........: {len(self.unique_phone):,}
   🔑 Total Combos....: {len(self.all_combos):,}

{'─'*70}
🎁 GIFT CARDS & VOUCHERS:
   🎫 Gift Cards......: {self.gift_card_count}
   🏷️ Promo Codes.....: {self.promo_count}
   🎫 Vouchers........: {self.voucher_count}

{'─'*70}
🔐 SENSITIVE DATA:
   🎫 JWT Tokens.......: {self.jwt_count}
   🔐 API Keys.........: {self.api_count}
   💳 Credit Cards.....: {self.card_count}
   💰 Crypto Wallets..: {self.crypto_count}
   💬 Discord Tokens..: {self.discord_count}
   📨 Telegram Tokens..: {self.telegram_count}

{'─'*70}
📁 Output Folder: {self.current_output_folder if self.current_output_folder else 'Not started'}

{'='*70}
"""
        self.update_stats(stats)
    
    def update_stats(self, stats):
        self.queue.put(('stats', stats))
    
    def log(self, message, tag=None):
        self.queue.put(('log', message, tag))
    
    def update_progress(self, value, status, current_file):
        self.queue.put(('progress', value, status, current_file))
    
    def update_counters(self, files, creds, filtered, errors):
        self.queue.put(('counters', files, creds, filtered, errors))
    
    def update_thread_status(self, active_threads):
        self.queue.put(('threads', active_threads))
    
    def clear_output(self):
        self.log_text.delete(1.0, tk.END)
        self.log(f"🗑 Console cleared", "info")
    
    def save_full_log(self):
        content = self.log_text.get(1.0, tk.END)
        if not content.strip():
            self.log(f"⚠️ No log content to save", "warning")
            return
        
        output_folder = self.get_output_folder()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(output_folder, f"scan_log_{timestamp}.txt")
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.log(f"✅ Log saved to {log_file}", "success")
        messagebox.showinfo("Log Saved", f"Log saved to:\n{log_file}")
    
    def start_scan(self):
        if not self.folder_path.get():
            self.log(f"❌ Please select a folder first!", "error")
            return
        
        if self.scanning:
            self.log(f"⚠️ Scan already in progress!", "warning")
            return
        
        self.max_threads = self.threads_var.get()
        self.min_length = self.min_len_var.get()
        self.max_length = self.max_len_var.get()
        
        if self.min_length >= self.max_length:
            self.log(f"❌ Min length must be less than max length!", "error")
            return
        
        self.scanning = True
        self.pause_scan = False
        self.stop_scan = False
        self.scan_start_time = datetime.now()
        self.skipped_files = []
        self.error_count = 0
        self.processed_files = 0
        self.total_credentials = 0
        self.filtered_count = 0
        
        self.reset_all_data()
        
        self.scan_btn.config(state=tk.DISABLED, text="⏳ SCANNING...", bg='#ff6600')
        self.pause_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        
        self.current_output_folder = self.get_output_folder()
        self.log(f"📁 Output will be saved to: {self.current_output_folder}", "success")
        
        scan_thread = threading.Thread(target=self.scan_folder_advanced, args=(self.folder_path.get(),), daemon=True)
        scan_thread.start()
    
    def reset_all_data(self):
        with self.lock:
            self.unique_android.clear()
            self.unique_phone.clear()
            self.unique_indian_phone.clear()
            self.unique_email.clear()
            self.unique_url.clear()
            self.all_combos.clear()
            self.android_package_combos.clear()
            self.jwt_tokens.clear()
            self.discord_tokens.clear()
            self.telegram_tokens.clear()
            self.credit_cards.clear()
            self.credit_cards_detailed.clear()
            self.api_keys.clear()
            self.crypto_wallets.clear()
            self.leaked_hashes.clear()
            self.gift_cards.clear()
            self.promo_codes.clear()
            self.vouchers.clear()
            self.coupons.clear()
            self.reward_codes.clear()
            
            # Reset counters
            self.gift_card_count = 0
            self.promo_count = 0
            self.voucher_count = 0
    
    def pause_scanning(self):
        if self.scanning and not self.pause_scan:
            self.pause_scan = True
            self.pause_btn.config(text="▶ RESUME", bg='#00cc66')
            self.log(f"⏸ SCAN PAUSED - Click RESUME to continue", "warning")
        elif self.pause_scan:
            self.pause_scan = False
            self.pause_btn.config(text="⏸ PAUSE", bg='#ff6600')
            self.log(f"▶ SCAN RESUMED", "success")
    
    def stop_scanning(self):
        if self.scanning:
            self.stop_scan = True
            self.pause_scan = False
            self.log(f"⏹ STOPPING SCAN...", "error")
            if self.executor:
                self.executor.shutdown(wait=False, cancel_futures=True)
    
    def safe_exit(self):
        if self.scanning:
            if messagebox.askyesno("Exit", "Scan in progress. Stop and exit?"):
                self.stop_scan = True
                self.root.after(500, self.root.destroy)
        else:
            self.root.destroy()
    
    def clean_phone_number(self, number):
        clean = re.sub(r'[^\d+]', '', str(number))
        if clean.startswith('+'):
            return clean
        return clean
    
    def is_valid_mobile(self, number):
        clean = self.clean_phone_number(number)
        return 7 <= len(clean) <= 15
    
    def is_indian_number(self, number):
        clean = self.clean_phone_number(number)
        if clean.startswith('+91'):
            clean = clean[3:]
        elif clean.startswith('91'):
            clean = clean[2:]
        return len(clean) == 10 and clean[0] in '6789'
    
    def remove_country_code(self, number):
        clean = self.clean_phone_number(number)
        if clean.startswith('+91'):
            clean = clean[3:]
        elif clean.startswith('91'):
            clean = clean[2:]
        return clean
    
    def is_valid_credential(self, username, password):
        if len(username) < self.min_length or len(username) > self.max_length:
            return False
        if len(password) < self.min_length or len(password) > self.max_length:
            return False
        if ' ' in password:
            return False
        
        if self.smart_filter:
            invalid_passwords = ['password', '123456', 'admin', 'test', 'user', 'pass', 'demo']
            if password.lower() in invalid_passwords:
                return False
            if username.isdigit() and len(username) > 8:
                return False
        
        return True
    
    def verify_credit_card_luhn(self, card_number):
        """Verify credit card number using Luhn algorithm"""
        card_number = re.sub(r'\D', '', card_number)
        if not card_number.isdigit() or len(card_number) < 13 or len(card_number) > 19:
            return False
        
        total = 0
        reverse_digits = card_number[::-1]
        
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n = n - 9
            total += n
        
        return total % 10 == 0
    
    def detect_card_type(self, card_number):
        """Detect credit card type from number"""
        card_number = re.sub(r'\D', '', card_number)
        
        patterns = {
            'visa': r'^4[0-9]{12}(?:[0-9]{3})?$',
            'mastercard': r'^(5[1-5][0-9]{14}|2[2-7][0-9]{14})$',
            'amex': r'^3[47][0-9]{13}$',
            'discover': r'^6011[0-9]{12}$',
            'jcb': r'^(?:2131|1800|35[0-9]{3})[0-9]{11}$',
            'diners': r'^3(?:0[0-5]|[68][0-9])[0-9]{11}$'
        }
        
        for card_type, pattern in patterns.items():
            if re.match(pattern, card_number):
                return card_type
        return 'unknown'
    
    def extract_credit_card_with_details(self, content):
        """Extract credit card numbers with possible expiry and CVV"""
        cards_found = []
        
        # Combined pattern for card number, expiry, and CVV
        card_pattern = r'''
            (?P<number>\b(?:\d[ -]*?){13,16}\b)
            (?:[^\d]*?(?:exp|expiry|expiration|valid|thru|until)[^\d]*?
            (?P<expiry>\d{1,2}[/-]\d{2,4}))?
            (?:[^\d]*?(?:cvv|cvv2|cvc|security code)[^\d]*?
            (?P<cvv>\b\d{3,4}\b))?
        '''
        
        matches = re.finditer(card_pattern, content, re.IGNORECASE | re.VERBOSE)
        
        for match in matches:
            number = re.sub(r'[\s-]', '', match.group('number'))
            
            # Basic validation
            if len(number) < 13 or len(number) > 19:
                continue
            
            # Detect card type
            card_type = self.detect_card_type(number)
            if card_type == 'unknown' and not self.verify_credit_card_luhn(number):
                continue
            
            is_valid = self.verify_credit_card_luhn(number)
            
            expiry = match.group('expiry')
            if expiry:
                # Normalize expiry format
                expiry = re.sub(r'[/-]', '/', expiry)
                if len(expiry.split('/')[1]) == 2 and int(expiry.split('/')[1]) < 30:
                    expiry = f"{expiry.split('/')[0]}/20{expiry.split('/')[1]}"
            
            cvv = match.group('cvv')
            
            card_info = {
                'number': number,
                'type': card_type,
                'expiry': expiry if expiry else 'Unknown',
                'cvv': cvv if cvv else 'Unknown',
                'valid': is_valid
            }
            cards_found.append(card_info)
        
        return cards_found
    
    def extract_gift_cards_and_vouchers(self, content):
        """Extract gift cards, promo codes, and vouchers"""
        findings = {
            'gift_cards': defaultdict(set),
            'promo_codes': defaultdict(set),
            'vouchers': defaultdict(set),
            'coupons': defaultdict(set)
        }
        
        # Extract gift cards
        for brand, patterns in self.gift_card_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    findings['gift_cards'][brand].add(match.strip())
        
        # Extract promo codes
        for platform, patterns in self.promo_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    findings['promo_codes'][platform].add(match.strip())
        
        # Extract vouchers
        for voucher_type, patterns in self.voucher_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0]
                    findings['vouchers'][voucher_type].add(match.strip())
        
        # Extract coupons from various sources
        coupon_patterns = [
            r'coupon(?:\s+code)?\s*[:=]\s*([A-Z0-9]{6,20})',
            r'coupon\s+([A-Z0-9]{6,20})',
            r'(\d{4}-\d{4}-\d{4})'  # Common coupon format
        ]
        
        for pattern in coupon_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                findings['coupons']['generic'].add(match.strip())
        
        return findings
    
    def extract_android_combos(self, line):
        combos = []
        
        # Pattern: package:login:password
        pattern = r'^([a-z][a-z0-9_\.]+):([^:]+):(.+)$'
        match = re.match(pattern, line.strip())
        if match:
            package = match.group(1)
            login = match.group(2).strip()
            password = match.group(3).strip()
            if package and login and password:
                combos.append((package, login, password))
        
        return combos
    
    def scan_folder_advanced(self, folder_path):
        try:
            output_folder = self.current_output_folder
            
            all_files = []
            for root, dirs, files in os.walk(folder_path):
                if self.stop_scan:
                    break
                dirs[:] = [d for d in dirs if d.lower() not in self.exclude_folders]
                for file in files:
                    if file.lower().endswith('.txt'):
                        all_files.append(os.path.join(root, file))
            
            total_files = len(all_files)
            
            self.log(f"\n{'='*70}", "info")
            self.log(f"🔍 COMBO MAKER - ULTIMATE SCAN v6.3", "success")
            self.log(f"{'='*70}", "info")
            self.log(f"📁 Input Folder: {folder_path}", "info")
            self.log(f"💾 Output Folder: {output_folder}", "info")
            self.log(f"🧵 Threads: {self.max_threads}", "info")
            self.log(f"📄 Text Files Found: {total_files}", "info")
            self.log(f"{'='*70}\n", "info")
            
            processed = 0
            
            for i in range(0, len(all_files), self.batch_size):
                if self.stop_scan:
                    break
                
                batch = all_files[i:i+self.batch_size]
                self.executor = ThreadPoolExecutor(max_workers=min(self.max_threads, len(batch)))
                futures = []
                
                for file_path in batch:
                    if self.stop_scan:
                        break
                    future = self.executor.submit(self.process_single_file, file_path)
                    futures.append(future)
                
                for future in futures:
                    if self.stop_scan:
                        break
                    
                    try:
                        result = future.result(timeout=15)
                        processed += 1
                        
                        percent = (processed / total_files) * 100
                        self.update_progress(percent, f"Processing: {processed}/{total_files}", 
                                           os.path.basename(result.get('file', '')) if result else '')
                        self.processed_files = processed
                        
                        if result and result.get('error'):
                            with self.lock:
                                self.error_count += 1
                        elif result and result.get('results'):
                            with self.lock:
                                local = result['results']
                                
                                self.unique_android.update(local.get('android', {}))
                                self.unique_url.update(local.get('url', {}))
                                self.unique_email.update(local.get('email', {}))
                                self.unique_phone.update(local.get('phone', {}))
                                self.unique_indian_phone.update(local.get('indian', {}))
                                self.all_combos.update(local.get('all_combos', {}))
                                
                                for combo in local.get('android_package_combos', []):
                                    self.android_package_combos[combo] = True
                                
                                self.total_credentials += local.get('credentials_found', 0)
                                self.filtered_count += local.get('filtered_count', 0)
                                
                                adv = local.get('advanced_data', {})
                                
                                for token in adv.get('jwt', []):
                                    self.jwt_tokens.add(token)
                                    self.jwt_count = len(self.jwt_tokens)
                                
                                for token in adv.get('discord', []):
                                    self.discord_tokens.add(token)
                                    self.discord_count = len(self.discord_tokens)
                                
                                for token in adv.get('telegram', []):
                                    self.telegram_tokens.add(token)
                                    self.telegram_count = len(self.telegram_tokens)
                                
                                # Credit Cards with verification
                                for card_info in adv.get('credit_cards_detailed', []):
                                    self.credit_cards_detailed.append(card_info)
                                    self.card_count = len(self.credit_cards_detailed)
                                
                                for key_type, keys in adv.get('api_keys', {}).items():
                                    for key in keys:
                                        self.api_keys[key_type].add(key)
                                        self.api_count = sum(len(v) for v in self.api_keys.values())
                                
                                for wallet_type, addresses in adv.get('crypto', {}).items():
                                    for addr in addresses:
                                        self.crypto_wallets[wallet_type].add(addr)
                                        self.crypto_count = sum(len(v) for v in self.crypto_wallets.values())
                                
                                # Gift Cards & Vouchers
                                gift_data = adv.get('gift_data', {})
                                
                                for brand, codes in gift_data.get('gift_cards', {}).items():
                                    for code in codes:
                                        self.gift_cards[brand].add(code)
                                        self.gift_card_count = sum(len(v) for v in self.gift_cards.values())
                                
                                for platform, codes in gift_data.get('promo_codes', {}).items():
                                    for code in codes:
                                        self.promo_codes[platform].add(code)
                                        self.promo_count = sum(len(v) for v in self.promo_codes.values())
                                
                                for vtype, vouchers in gift_data.get('vouchers', {}).items():
                                    for voucher in vouchers:
                                        self.vouchers[vtype].add(voucher)
                                        self.voucher_count = sum(len(v) for v in self.vouchers.values())
                                
                                for store, coupons in gift_data.get('coupons', {}).items():
                                    for coupon in coupons:
                                        self.coupons[store].add(coupon)
                            
                            self.update_counters(processed, self.total_credentials, self.filtered_count, self.error_count)
                            self.update_thread_status(len([f for f in futures if not f.done()]))
                    
                    except Exception as e:
                        with self.lock:
                            self.error_count += 1
                        self.log(f"⚠️ Error: {str(e)[:50]}", "error")
                
                if self.executor:
                    self.executor.shutdown(wait=True)
                
                while self.pause_scan and not self.stop_scan:
                    time.sleep(0.1)
            
            self.scan_end_time = datetime.now()
            
            if not self.stop_scan:
                self.save_all_results(output_folder)
                self.display_final_stats()
                self.refresh_sensitive_display()
                self.refresh_gift_display()
                self.refresh_stats()
            
        except Exception as e:
            self.log(f"❌ ERROR: {str(e)}", "error")
            self.log(traceback.format_exc(), "error")
        finally:
            self.scanning = False
            self.pause_scan = False
            self.stop_scan = False
            self.scan_btn.config(state=tk.NORMAL, text="🚀 START SCAN", bg='#00ff88')
            self.pause_btn.config(state=tk.DISABLED, text="⏸ PAUSE", bg='#ff6600')
            self.stop_btn.config(state=tk.DISABLED, text="⏹ STOP", bg='#ff0000')
            self.status_label.config(text="✅ SCAN COMPLETE")
            self.update_thread_status(0)
    
    def process_single_file(self, file_path):
        if self.stop_scan:
            return None
        
        while self.pause_scan and not self.stop_scan:
            time.sleep(0.05)
        
        local_results = {
            'android': {}, 'url': {}, 'email': {}, 'phone': {}, 'indian': {},
            'all_combos': {}, 'android_package_combos': [],
            'credentials_found': 0, 'filtered_count': 0,
            'error': None, 'advanced_data': {}
        }
        
        try:
            content = None
            for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
                        content = f.read()
                        if content:
                            break
                except:
                    continue
            
            if not content:
                return {'file': file_path, 'error': 'Could not read file', 'results': local_results}
            
            # Extract advanced sensitive data
            local_results['advanced_data'] = self.extract_advanced_sensitive_data(content)
            
            # Process each line for Android package combos and simple login:pass
            lines = content.splitlines()
            
            # State machine for parsing Soft/Host/Login/Password format
            current_soft = None
            current_host = None
            current_login = None
            current_password = None
            
            for line in lines:
                original_line = line
                line = line.strip()
                if not line:
                    continue
                
                # Parse Soft: line
                soft_match = re.match(r'Soft:\s*(.*?)(?:\s*$)', line, re.IGNORECASE)
                if soft_match:
                    current_soft = soft_match.group(1).strip()
                    continue
                
                # Parse Host: line
                host_match = re.match(r'Host:\s*(.*?)(?:\s*$)', line, re.IGNORECASE)
                if host_match:
                    current_host = host_match.group(1).strip()
                    continue
                
                # Parse Login: line
                login_match = re.match(r'Login:\s*(.*?)(?:\s*$)', line, re.IGNORECASE)
                if login_match:
                    current_login = login_match.group(1).strip()
                    continue
                
                # Parse Password: line
                password_match = re.match(r'Password:\s*(.*?)(?:\s*$)', line, re.IGNORECASE)
                if password_match:
                    current_password = password_match.group(1).strip()
                    
                    # We have a complete record
                    if current_host and current_login and current_password:
                        if current_login and current_password:
                            if self.is_valid_credential(current_login, current_password):
                                local_results['credentials_found'] += 1
                                
                                # Check for android:// in host
                                if 'android://' in current_host.lower():
                                    android_match = re.search(r'android://[^@]+@([^/]+)', current_host)
                                    if android_match:
                                        package = android_match.group(1)
                                        combo_line = f"{package}:{current_login}:{current_password}"
                                        if combo_line not in local_results['android_package_combos']:
                                            local_results['android_package_combos'].append(combo_line)
                                        
                                        android_key = f"{package}:{current_login}"
                                        if android_key not in local_results['android']:
                                            local_results['android'][android_key] = current_password
                                
                                # Regular URL credential
                                elif current_host.startswith(('http://', 'https://')):
                                    key = f"{current_host}:{current_login}"
                                    if key not in local_results['url']:
                                        local_results['url'][key] = current_password
                                
                                # Add to all combos
                                if current_login not in local_results['all_combos']:
                                    local_results['all_combos'][current_login] = current_password
                                
                                # Check email format
                                if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', current_login):
                                    if current_login not in local_results['email']:
                                        local_results['email'][current_login] = current_password
                                
                                # Check phone number
                                elif self.is_valid_mobile(current_login):
                                    clean_num = self.clean_phone_number(current_login)
                                    if clean_num not in local_results['phone']:
                                        local_results['phone'][clean_num] = current_password
                                        if self.is_indian_number(clean_num):
                                            indian_num = self.remove_country_code(clean_num)
                                            if indian_num not in local_results['indian']:
                                                local_results['indian'][indian_num] = current_password
                    
                    # Reset for next record
                    current_soft = None
                    current_host = None
                    current_login = None
                    current_password = None
                    continue
                
                # Extract Android package combos (package:login:password)
                android_combos = self.extract_android_combos(line)
                for package, login, password in android_combos:
                    if self.is_valid_credential(login, password):
                        combo_line = f"{package}:{login}:{password}"
                        if combo_line not in local_results['android_package_combos']:
                            local_results['android_package_combos'].append(combo_line)
                            local_results['credentials_found'] += 1
                            
                            android_key = f"{package}:{login}"
                            if android_key not in local_results['android']:
                                local_results['android'][android_key] = password
                            
                            if login not in local_results['all_combos']:
                                local_results['all_combos'][login] = password
                            
                            self.log(f"  📱 {package}:{login[:30]}:{password[:20]}", "found")
                            
                            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', login):
                                if login not in local_results['email']:
                                    local_results['email'][login] = password
                            
                            elif self.is_valid_mobile(login):
                                clean_num = self.clean_phone_number(login)
                                if clean_num not in local_results['phone']:
                                    local_results['phone'][clean_num] = password
                                    if self.is_indian_number(clean_num):
                                        indian_num = self.remove_country_code(clean_num)
                                        if indian_num not in local_results['indian']:
                                            local_results['indian'][indian_num] = password
                
                # Extract simple login:password format (only if not already processed as part of Soft/Host block)
                if ':' in line and not line.lower().startswith(('soft:', 'host:', 'login:', 'password:')):
                    if line.count(':') == 1:
                        login, password = line.split(':', 1)
                        login, password = login.strip(), password.strip()
                        
                        if login and password and self.is_valid_credential(login, password):
                            if login not in local_results['all_combos']:
                                local_results['all_combos'][login] = password
                                local_results['credentials_found'] += 1
                                
                                if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', login):
                                    if login not in local_results['email']:
                                        local_results['email'][login] = password
                                
                                elif self.is_valid_mobile(login):
                                    clean_num = self.clean_phone_number(login)
                                    if clean_num not in local_results['phone']:
                                        local_results['phone'][clean_num] = password
                                        if self.is_indian_number(clean_num):
                                            indian_num = self.remove_country_code(clean_num)
                                            if indian_num not in local_results['indian']:
                                                local_results['indian'][indian_num] = password
            
            return {'file': file_path, 'error': None, 'results': local_results}
        except Exception as e:
            return {'file': file_path, 'error': str(e), 'results': local_results}
    
    def extract_advanced_sensitive_data(self, content):
        findings = {
            'jwt': [], 'discord': [], 'telegram': [],
            'credit_cards': defaultdict(set), 'credit_cards_detailed': [],
            'api_keys': defaultdict(set), 'crypto': defaultdict(set), 'hashes': defaultdict(set),
            'gift_data': {'gift_cards': defaultdict(set), 'promo_codes': defaultdict(set), 
                         'vouchers': defaultdict(set), 'coupons': defaultdict(set)}
        }
        
        # JWT tokens
        jwt_pattern = r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+'
        findings['jwt'] = re.findall(jwt_pattern, content)
        
        # Discord tokens
        discord_pattern = r'[mM][0-9a-zA-Z]{23,25}'
        findings['discord'] = re.findall(discord_pattern, content)
        
        # Telegram Bot Tokens
        telegram_pattern = r'\d{8,10}:[a-zA-Z0-9_-]{35}'
        findings['telegram'] = re.findall(telegram_pattern, content)
        
        # Credit Cards with verification
        if self.extract_financial:
            findings['credit_cards_detailed'] = self.extract_credit_card_with_details(content)
            # Also store simple credit cards
            for card_info in findings['credit_cards_detailed']:
                findings['credit_cards'][card_info['type']].add(card_info['number'])
        
        # API Keys
        api_patterns = {
            'api_key': r'api[_-]?key[\s:=]+([A-Za-z0-9]{16,})',
            'aws_key': r'AKIA[0-9A-Z]{16}',
            'google_api': r'AIza[0-9A-Za-z\-_]{35}',
            'stripe_key': r'sk_live_[0-9a-zA-Z]{24}',
            'github_token': r'ghp_[0-9a-zA-Z]{36}'
        }
        for key_type, pattern in api_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                findings['api_keys'][key_type].add(match[:50] if len(match) > 50 else match)
        
        # Crypto Wallets
        crypto_patterns = {
            'bitcoin': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
            'ethereum': r'\b0x[a-fA-F0-9]{40}\b',
            'ltc': r'\bL[a-km-zA-HJ-NP-Z1-9]{26,33}\b',
            'doge': r'\bD[a-km-zA-HJ-NP-Z1-9]{25,34}\b'
        }
        for wallet_type, pattern in crypto_patterns.items():
            matches = re.findall(pattern, content)
            for match in matches:
                findings['crypto'][wallet_type].add(match)
        
        # Hash detection
        hash_patterns = {
            'md5': r'\b[a-fA-F0-9]{32}\b',
            'sha1': r'\b[a-fA-F0-9]{40}\b',
            'sha256': r'\b[a-fA-F0-9]{64}\b',
            'bcrypt': r'\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}\b'
        }
        for hash_type, pattern in hash_patterns.items():
            matches = re.findall(pattern, content)
            for match in matches:
                findings['hashes'][hash_type].add(match)
        
        # Gift Cards, Promo Codes, Vouchers
        if self.extract_gift_cards:
            findings['gift_data'] = self.extract_gift_cards_and_vouchers(content)
        
        return findings
    
    def save_all_results(self, output_folder):
        try:
            credentials_folder = os.path.join(output_folder, "CREDENTIALS")
            sensitive_folder = os.path.join(output_folder, "SENSITIVE_DATA")
            android_folder = os.path.join(output_folder, "ANDROID_COMBOS")
            gift_folder = os.path.join(output_folder, "GIFT_CARDS_VOUCHERS")
            
            # Save Android Package Combos (package:login:password) - NO HEADERS
            if self.android_package_combos:
                package_file = os.path.join(android_folder, 'android_package_combos.txt')
                with open(package_file, 'w', encoding='utf-8') as f:
                    for combo in sorted(self.android_package_combos.keys()):
                        f.write(f"{combo}\n")
                self.log(f"✅ Saved {len(self.android_package_combos)} Android package combos", "success")
            
            # Save URL credentials (host:login:pass) - NO HEADERS
            if self.unique_url:
                url_file = os.path.join(credentials_folder, 'url_credentials.txt')
                with open(url_file, 'w', encoding='utf-8') as f:
                    for k, v in self.unique_url.items():
                        f.write(f"{k}:{v}\n")
                self.log(f"✅ Saved {len(self.unique_url)} URL credentials", "success")
            
            # Save Android credentials (package:login:pass)
            if self.unique_android:
                android_file = os.path.join(credentials_folder, 'android_credentials.txt')
                with open(android_file, 'w', encoding='utf-8') as f:
                    for k, v in self.unique_android.items():
                        f.write(f"{k}:{v}\n")
                self.log(f"✅ Saved {len(self.unique_android)} Android credentials", "success")
            
            # Save all combos (login:password)
            if self.all_combos:
                combos_file = os.path.join(credentials_folder, 'all_login_pass_combos.txt')
                with open(combos_file, 'w', encoding='utf-8') as f:
                    for k, v in self.all_combos.items():
                        f.write(f"{k}:{v}\n")
                self.log(f"✅ Saved {len(self.all_combos)} login:pass combos", "success")
            
            # Save email credentials
            if self.unique_email:
                email_file = os.path.join(credentials_folder, 'email_credentials.txt')
                with open(email_file, 'w', encoding='utf-8') as f:
                    for k, v in self.unique_email.items():
                        f.write(f"{k}:{v}\n")
                self.log(f"✅ Saved {len(self.unique_email)} email credentials", "success")
            
            # Save phone credentials
            if self.unique_phone:
                phone_file = os.path.join(credentials_folder, 'phone_credentials.txt')
                with open(phone_file, 'w', encoding='utf-8') as f:
                    for k, v in self.unique_phone.items():
                        f.write(f"{k}:{v}\n")
                self.log(f"✅ Saved {len(self.unique_phone)} phone credentials", "success")
            
            # Save Indian phone credentials
            if self.unique_indian_phone:
                indian_file = os.path.join(credentials_folder, 'indian_phone_credentials.txt')
                with open(indian_file, 'w', encoding='utf-8') as f:
                    for k, v in self.unique_indian_phone.items():
                        f.write(f"{k}:{v}\n")
                self.log(f"✅ Saved {len(self.unique_indian_phone)} Indian phone credentials", "success")
            
            # Save JWT tokens
            if self.jwt_tokens:
                jwt_file = os.path.join(sensitive_folder, 'jwt_tokens.txt')
                with open(jwt_file, 'w', encoding='utf-8') as f:
                    for token in self.jwt_tokens:
                        f.write(f"{token}\n")
                self.log(f"✅ Saved {len(self.jwt_tokens)} JWT tokens", "success")
            
            # Save Discord tokens
            if self.discord_tokens:
                discord_file = os.path.join(sensitive_folder, 'discord_tokens.txt')
                with open(discord_file, 'w', encoding='utf-8') as f:
                    for token in self.discord_tokens:
                        f.write(f"{token}\n")
                self.log(f"✅ Saved {len(self.discord_tokens)} Discord tokens", "success")
            
            # Save Telegram tokens
            if self.telegram_tokens:
                telegram_file = os.path.join(sensitive_folder, 'telegram_tokens.txt')
                with open(telegram_file, 'w', encoding='utf-8') as f:
                    for token in self.telegram_tokens:
                        f.write(f"{token}\n")
                self.log(f"✅ Saved {len(self.telegram_tokens)} Telegram tokens", "success")
            
            # Save Credit Cards with details
            if self.credit_cards_detailed:
                cards_file = os.path.join(sensitive_folder, 'credit_cards_detailed.txt')
                with open(cards_file, 'w', encoding='utf-8') as f:
                    for card in self.credit_cards_detailed:
                        line = f"[{card['type'].upper()}] {card['number']}"
                        if card['expiry'] != 'Unknown':
                            line += f" | Exp: {card['expiry']}"
                        if card['cvv'] != 'Unknown':
                            line += f" | CVV: {card['cvv']}"
                        if card['valid']:
                            line += " | ✓ Valid (Luhn)"
                        else:
                            line += " | ✗ Invalid (Luhn)"
                        f.write(line + "\n")
                self.log(f"✅ Saved {len(self.credit_cards_detailed)} credit cards with details", "success")
            
            # Save API Keys
            if self.api_keys:
                api_file = os.path.join(sensitive_folder, 'api_keys.txt')
                with open(api_file, 'w', encoding='utf-8') as f:
                    for key_type, keys in self.api_keys.items():
                        f.write(f"\n=== {key_type.upper()} ===\n")
                        for key in keys:
                            f.write(f"{key}\n")
                self.log(f"✅ Saved {self.api_count} API keys", "success")
            
            # Save Crypto Wallets
            if self.crypto_wallets:
                crypto_file = os.path.join(sensitive_folder, 'crypto_wallets.txt')
                with open(crypto_file, 'w', encoding='utf-8') as f:
                    for wallet_type, addresses in self.crypto_wallets.items():
                        f.write(f"\n=== {wallet_type.upper()} ===\n")
                        for addr in addresses:
                            f.write(f"{addr}\n")
                self.log(f"✅ Saved {self.crypto_count} crypto wallets", "success")
            
            # Save Hashes
            if self.leaked_hashes:
                hashes_file = os.path.join(sensitive_folder, 'hashes.txt')
                with open(hashes_file, 'w', encoding='utf-8') as f:
                    for hash_type, hashes in self.leaked_hashes.items():
                        f.write(f"\n=== {hash_type.upper()} ===\n")
                        for h in hashes:
                            f.write(f"{h}\n")
                self.log(f"✅ Saved {self.hash_count} hashes", "success")
            
            # Save Gift Cards
            if self.gift_cards:
                gift_file = os.path.join(gift_folder, 'gift_cards.txt')
                with open(gift_file, 'w', encoding='utf-8') as f:
                    for brand, cards in self.gift_cards.items():
                        f.write(f"\n=== {brand.upper()} GIFT CARDS ===\n")
                        for card in cards:
                            f.write(f"{card}\n")
                self.log(f"✅ Saved {self.gift_card_count} gift cards", "success")
            
            # Save Promo Codes
            if self.promo_codes:
                promo_file = os.path.join(gift_folder, 'promo_codes.txt')
                with open(promo_file, 'w', encoding='utf-8') as f:
                    for platform, codes in self.promo_codes.items():
                        f.write(f"\n=== {platform.upper()} PROMO CODES ===\n")
                        for code in codes:
                            f.write(f"{code}\n")
                self.log(f"✅ Saved {self.promo_count} promo codes", "success")
            
            # Save Vouchers
            if self.vouchers:
                voucher_file = os.path.join(gift_folder, 'vouchers.txt')
                with open(voucher_file, 'w', encoding='utf-8') as f:
                    for vtype, vouchers in self.vouchers.items():
                        f.write(f"\n=== {vtype.upper()} VOUCHERS ===\n")
                        for voucher in vouchers:
                            f.write(f"{voucher}\n")
                self.log(f"✅ Saved {self.voucher_count} vouchers", "success")
            
            # Save Coupons
            if self.coupons:
                coupon_file = os.path.join(gift_folder, 'coupons.txt')
                with open(coupon_file, 'w', encoding='utf-8') as f:
                    for store, coupons in self.coupons.items():
                        f.write(f"\n=== {store.upper()} COUPONS ===\n")
                        for coupon in coupons:
                            f.write(f"{coupon}\n")
                self.log(f"✅ Saved coupons", "success")
            
            self.log(f"\n📁 All results saved to: {output_folder}", "success")
            
        except Exception as e:
            self.log(f"❌ Error saving results: {str(e)}", "error")
            self.log(traceback.format_exc(), "error")
    
    def display_final_stats(self):
        duration = self.scan_end_time - self.scan_start_time if self.scan_end_time else None
        
        stats = f"""
{'='*70}
✅ SCAN COMPLETED SUCCESSFULLY!
{'='*70}

📁 Files Processed: {self.processed_files:,}
🔑 Valid Credentials: {self.total_credentials:,}
🚫 Filtered: {self.filtered_count:,}
⚠️ Errors: {self.error_count:,}
{'⏱️ Duration: ' + f'{duration.total_seconds():.2f} seconds' if duration else ''}

{'─'*70}
📊 CREDENTIALS CAPTURED:
   📦 Android Package Combos: {len(self.android_package_combos):,}
   📱 Android Credentials: {len(self.unique_android):,}
   🔗 URL Credentials: {len(self.unique_url):,}
   🔑 Login:Pass Combos: {len(self.all_combos):,}
   ✉️ Email Credentials: {len(self.unique_email):,}
   📞 Phone Credentials: {len(self.unique_phone):,}

{'─'*70}
🎁 GIFT CARDS & VOUCHERS:
   🎫 Gift Cards: {self.gift_card_count}
   🏷️ Promo Codes: {self.promo_count}
   🎫 Vouchers: {self.voucher_count}

{'─'*70}
🔐 SENSITIVE DATA:
   🎫 JWT Tokens: {self.jwt_count}
   💬 Discord Tokens: {self.discord_count}
   📨 Telegram Tokens: {self.telegram_count}
   💳 Credit Cards: {self.card_count}
   🔐 API Keys: {self.api_count}
   💰 Crypto Wallets: {self.crypto_count}

{'─'*70}
💾 Output Folder: {self.current_output_folder}

📁 File Structure:
   ├── ANDROID_COMBOS/android_package_combos.txt
   ├── CREDENTIALS/
   │   ├── url_credentials.txt
   │   ├── android_credentials.txt
   │   ├── all_login_pass_combos.txt
   │   ├── email_credentials.txt
   │   └── phone_credentials.txt
   ├── SENSITIVE_DATA/
   │   ├── jwt_tokens.txt
   │   ├── discord_tokens.txt
   │   ├── telegram_tokens.txt
   │   ├── credit_cards_detailed.txt
   │   ├── api_keys.txt
   │   └── crypto_wallets.txt
   └── GIFT_CARDS_VOUCHERS/
       ├── gift_cards.txt
       ├── promo_codes.txt
       └── vouchers.txt

{'='*70}
"""
        self.log(stats, "success")
        messagebox.showinfo("Scan Complete", 
                           f"✅ SCAN COMPLETE!\n\n"
                           f"📦 Android Package Combos: {len(self.android_package_combos)}\n"
                           f"🔑 Total Credentials: {self.total_credentials}\n"
                           f"🎁 Gift Cards: {self.gift_card_count}\n"
                           f"🏷️ Promo Codes: {self.promo_count}\n"
                           f"🎫 JWT Tokens: {self.jwt_count}\n"
                           f"💳 Credit Cards: {self.card_count}\n\n"
                           f"📁 Output: {self.current_output_folder}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CredentialScannerGUI(root)
    root.mainloop()
