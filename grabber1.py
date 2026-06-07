import os
import re
from pathlib import Path
from datetime import datetime
import sys

def process_files(folder_path):
    unique_android = {}
    unique_phone = {}
    unique_email = {}
    unique_url = {}
    all_combos = {}
    
    android_results = []
    phone_results = []
    email_results = []
    url_results = []
    combo_results = []
    
    total_files = 0
    total_lines = 0
    processed_files = 0
    
    script_location = os.path.dirname(os.path.abspath(__file__))
    output_folder = script_location if script_location else os.getcwd()
    
    output_android_path = os.path.join(output_folder, 'package_android.txt')
    output_phone_path = os.path.join(output_folder, 'loginnumberpass.txt')
    output_email_path = os.path.join(output_folder, 'emailuserpass.txt')
    output_url_path = os.path.join(output_folder, 'urlcombouserpass.txt')
    output_other_path = os.path.join(output_folder, 'other_usernames_passwords.txt')
    output_master_path = os.path.join(output_folder, 'ALL_CREDENTIALS_MASTER.txt')
    
    existing_android = set()
    existing_phone = set()
    existing_email = set()
    existing_url = set()
    existing_other = set()
    
    if os.path.exists(output_android_path):
        with open(output_android_path, 'r', encoding='utf-8', errors='ignore') as f:
            existing_android.update(line.strip() for line in f if line.strip())
    if os.path.exists(output_phone_path):
        with open(output_phone_path, 'r', encoding='utf-8', errors='ignore') as f:
            existing_phone.update(line.strip() for line in f if line.strip())
    if os.path.exists(output_email_path):
        with open(output_email_path, 'r', encoding='utf-8', errors='ignore') as f:
            existing_email.update(line.strip() for line in f if line.strip())
    if os.path.exists(output_url_path):
        with open(output_url_path, 'r', encoding='utf-8', errors='ignore') as f:
            existing_url.update(line.strip() for line in f if line.strip())
    if os.path.exists(output_other_path):
        with open(output_other_path, 'r', encoding='utf-8', errors='ignore') as f:
            existing_other.update(line.strip() for line in f if line.strip())
    
    print("=" * 100)
    print(f"STARTING SCAN AT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"TARGET FOLDER: {folder_path}")
    print(f"OUTPUT FOLDER: {output_folder}")
    print("=" * 100)
    print()
    
    all_items = list(Path(folder_path).rglob('*'))
    all_folders = [x for x in all_items if x.is_dir()]
    total_files_to_process = [x for x in all_items if x.is_file()]
    total_folders = len(all_folders)
    total_files_count = len(total_files_to_process)
    
    print(f"📊 TOTAL ITEMS FOUND:")
    print(f"   📁 Folders: {total_folders}")
    print(f"   📄 Files: {total_files_count}")
    print(f"   🔄 Existing entries loaded:")
    print(f"      Android: {len(existing_android)} | Phone: {len(existing_phone)} | Email: {len(existing_email)} | URL: {len(existing_url)} | Other: {len(existing_other)}")
    print()
    
    folder_num = 0
    
    for root, dirs, files in os.walk(folder_path):
        folder_num += 1
        current_folder = os.path.basename(root) if os.path.basename(root) else root
        relative_path = os.path.relpath(root, folder_path) if root != folder_path else "."
        
        sys.stdout.write(f"\r{' ' * 100}\r")
        print(f"\n{'=' * 100}")
        print(f"📁 [{folder_num}/{total_folders}] PROCESSING FOLDER: {current_folder}")
        print(f"   Location: {relative_path}")
        print(f"   Subfolders: {len(dirs)} | Files in this folder: {len(files)}")
        print(f"{'=' * 100}")
        
        folder_files_processed = 0
        
        for file in files:
            file_path = os.path.join(root, file)
            processed_files += 1
            folder_files_processed += 1
            
            percent = (processed_files / total_files_count) * 100
            bar_length = 40
            filled = int(bar_length * processed_files // total_files_count)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            sys.stdout.write(f"\r   📄 [{processed_files}/{total_files_count}] {bar} {percent:.1f}% - Current: {file}")
            sys.stdout.flush()
            
            try:
                file_size = os.path.getsize(file_path)
                
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.splitlines()
                    file_lines = len(lines)
                    total_lines += file_lines
                    
                    found_in_file = 0
                    current_host = ""
                    current_login = ""
                    current_password = ""
                    
                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        line_lower = line.lower()
                        
                        if 'host:' in line_lower:
                            host_match = re.search(r'host:\s*(.+)', line, re.IGNORECASE)
                            if host_match:
                                current_host = host_match.group(1).strip()
                        
                        elif 'login:' in line_lower or 'username:' in line_lower or 'user:' in line_lower or 'email:' in line_lower:
                            login_match = re.search(r'(?:login|username|user|email):\s*(.+)', line, re.IGNORECASE)
                            if login_match:
                                current_login = login_match.group(1).strip()
                                if len(current_login) > 40:
                                    current_login = ""
                        
                        elif 'password:' in line_lower or 'pass:' in line_lower or 'pwd:' in line_lower:
                            pass_match = re.search(r'(?:password|pass|pwd):\s*(.+)', line, re.IGNORECASE)
                            if pass_match:
                                current_password = pass_match.group(1).strip()
                                if len(current_password) > 40:
                                    current_password = ""
                                
                                if current_host and current_login and current_password and current_login != 'login' and current_password != 'password':
                                    if current_host.startswith('http'):
                                        entry = f"{current_host}:{current_login}:{current_password}"
                                        key = f"{current_host}:{current_login}"
                                        if key not in unique_url and entry not in existing_url:
                                            if len(current_login) <= 40 and len(current_password) <= 40:
                                                unique_url[key] = current_password
                                                found_in_file += 1
                                    else:
                                        if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', current_login):
                                            entry = f"{current_login}:{current_password}"
                                            key = current_login
                                            if key not in unique_email and entry not in existing_email:
                                                if len(current_login) <= 40 and len(current_password) <= 40:
                                                    unique_email[key] = current_password
                                                    found_in_file += 1
                                        elif re.match(r'^\+?[\d\s\-\(\)]{8,}$', current_login):
                                            clean_num = re.sub(r'[^\d+]', '', current_login)
                                            entry = f"{clean_num}:{current_password}"
                                            key = clean_num
                                            if key not in unique_phone and entry not in existing_phone:
                                                if len(clean_num) <= 40 and len(current_password) <= 40:
                                                    unique_phone[key] = current_password
                                                    found_in_file += 1
                                        else:
                                            entry = f"{current_login}:{current_password}"
                                            key = current_login
                                            if key not in all_combos and entry not in existing_other:
                                                if len(current_login) <= 40 and len(current_password) <= 40:
                                                    all_combos[key] = current_password
                                                    found_in_file += 1
                                    
                                    current_host = ""
                                    current_login = ""
                                    current_password = ""
                        
                        if ':' in line and not any(x in line_lower for x in ['host:', 'login:', 'password:', 'username:', 'user:', 'email:', 'pass:', 'pwd:', 'soft:', 'https://', 'http://']):
                            if 'android://' in line:
                                android_match = re.search(r'android://[^@]+@([^:]+):([^:]+):(.+)$', line)
                                if android_match:
                                    package = android_match.group(1)
                                    username = android_match.group(2)
                                    password = android_match.group(3)
                                    if username and password and len(password) >= 3:
                                        if len(username) <= 40 and len(password) <= 40:
                                            entry = f"{package}:{username}:{password}"
                                            key = f"{package}:{username}"
                                            if key not in unique_android and entry not in existing_android:
                                                unique_android[key] = password
                                                found_in_file += 1
                                else:
                                    parts = line.split(':', 2)
                                    if len(parts) >= 3 and 'android://' in parts[0]:
                                        if len(parts) == 3:
                                            pkg_user = parts[1]
                                            pwd = parts[2]
                                            if pkg_user and pwd and len(pwd) >= 3:
                                                if '://' not in pkg_user and '@' not in pkg_user:
                                                    if len(pkg_user) <= 40 and len(pwd) <= 40:
                                                        entry = f"android:{pkg_user}:{pwd}"
                                                        key = f"android:{pkg_user}"
                                                        if key not in unique_phone and entry not in existing_phone:
                                                            unique_phone[key] = pwd
                                                            found_in_file += 1
                            
                            elif '://' in line and 'android://' not in line:
                                url_pattern = r'(https?://[^:/\s]+)'
                                url_match = re.search(url_pattern, line)
                                if url_match:
                                    url_base = url_match.group(1)
                                    remaining = line[line.find(url_base) + len(url_base):]
                                    if remaining.startswith(':'):
                                        after_colon = remaining[1:]
                                        if ':' in after_colon:
                                            cred_parts = after_colon.split(':', 1)
                                            if len(cred_parts) == 2:
                                                username, password = cred_parts[0].strip(), cred_parts[1].strip()
                                                if username and password and len(password) >= 3:
                                                    if len(username) <= 40 and len(password) <= 40:
                                                        entry = f"{url_base}:{username}:{password}"
                                                        key = f"{url_base}:{username}"
                                                        if key not in unique_url and entry not in existing_url:
                                                            unique_url[key] = password
                                                            found_in_file += 1
                            
                            else:
                                if line.count(':') == 1:
                                    username, password = line.split(':', 1)
                                    username = username.strip()
                                    password = password.strip()
                                    
                                    if username and password and len(password) >= 3:
                                        if len(username) <= 40 and len(password) <= 40:
                                            if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', username):
                                                entry = f"{username}:{password}"
                                                key = username
                                                if key not in unique_email and entry not in existing_email:
                                                    unique_email[key] = password
                                                    found_in_file += 1
                                            elif re.match(r'^\+?[\d\s\-\(\)]{8,}$', username):
                                                clean_num = re.sub(r'[^\d+]', '', username)
                                                entry = f"{clean_num}:{password}"
                                                key = clean_num
                                                if key not in unique_phone and entry not in existing_phone:
                                                    unique_phone[key] = password
                                                    found_in_file += 1
                                            elif username.isdigit() or (username.startswith('+') and username[1:].isdigit()):
                                                entry = f"{username}:{password}"
                                                key = username
                                                if key not in unique_phone and entry not in existing_phone:
                                                    unique_phone[key] = password
                                                    found_in_file += 1
                                            elif len(username) >= 3 and len(password) >= 3:
                                                entry = f"{username}:{password}"
                                                key = username
                                                if key not in all_combos and entry not in existing_other:
                                                    all_combos[key] = password
                                                    found_in_file += 1
                                
                                elif line.count(':') > 1:
                                    parts = line.split(':')
                                    if len(parts) >= 3:
                                        username = parts[-2].strip()
                                        password = parts[-1].strip()
                                        if username and password and len(password) >= 3:
                                            if len(username) <= 40 and len(password) <= 40:
                                                if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', username):
                                                    entry = f"{username}:{password}"
                                                    key = username
                                                    if key not in unique_email and entry not in existing_email:
                                                        unique_email[key] = password
                                                        found_in_file += 1
                                                elif username.isdigit() or (username.startswith('+') and username[1:].isdigit()):
                                                    entry = f"{username}:{password}"
                                                    key = username
                                                    if key not in unique_phone and entry not in existing_phone:
                                                        unique_phone[key] = password
                                                        found_in_file += 1
                                                elif len(username) >= 3:
                                                    entry = f"{username}:{password}"
                                                    key = username
                                                    if key not in all_combos and entry not in existing_other:
                                                        all_combos[key] = password
                                                        found_in_file += 1
                    
                    if found_in_file > 0:
                        sys.stdout.write(f" ✅ (+{found_in_file})")
                        sys.stdout.flush()
                    
            except Exception as e:
                sys.stdout.write(f" ⚠️ Error")
                sys.stdout.flush()
                continue
        
        print(f"\n   📊 Folder summary: +{len([x for x in unique_android.keys() if x not in existing_android])} Android | +{len([x for x in unique_phone.keys() if x not in existing_phone])} Phone | +{len([x for x in unique_email.keys() if x not in existing_email])} Email | +{len([x for x in unique_url.keys() if x not in existing_url])} URL | +{len([x for x in all_combos.keys() if x not in existing_other])} Other")
    
    print("\n" + "=" * 100)
    print("WRITING OUTPUT FILES (APPENDING NEW ENTRIES)...")
    print("=" * 100)
    
    new_android = []
    for key, pwd in unique_android.items():
        entry = f"{key}:{pwd}"
        if entry not in existing_android:
            new_android.append(entry)
            existing_android.add(entry)
    
    new_phone = []
    for key, pwd in unique_phone.items():
        entry = f"{key}:{pwd}"
        if entry not in existing_phone:
            new_phone.append(entry)
            existing_phone.add(entry)
    
    new_email = []
    for key, pwd in unique_email.items():
        entry = f"{key}:{pwd}"
        if entry not in existing_email:
            new_email.append(entry)
            existing_email.add(entry)
    
    new_url = []
    for key, pwd in unique_url.items():
        entry = f"{key}:{pwd}"
        if entry not in existing_url:
            new_url.append(entry)
            existing_url.add(entry)
    
    new_other = []
    for key, pwd in all_combos.items():
        entry = f"{key}:{pwd}"
        if entry not in existing_other and entry not in existing_phone and entry not in existing_email:
            new_other.append(entry)
            existing_other.add(entry)
    
    new_android.sort()
    new_phone.sort()
    new_email.sort()
    new_url.sort()
    new_other.sort()
    
    if new_android:
        print(f"\n💾 Appending {len(new_android)} new entries to: {output_android_path}")
        with open(output_android_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(new_android) + '\n')
    
    if new_phone:
        print(f"💾 Appending {len(new_phone)} new entries to: {output_phone_path}")
        with open(output_phone_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(new_phone) + '\n')
    
    if new_email:
        print(f"💾 Appending {len(new_email)} new entries to: {output_email_path}")
        with open(output_email_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(new_email) + '\n')
    
    if new_url:
        print(f"💾 Appending {len(new_url)} new entries to: {output_url_path}")
        with open(output_url_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(new_url) + '\n')
    
    if new_other:
        print(f"💾 Appending {len(new_other)} new entries to: {output_other_path}")
        with open(output_other_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(new_other) + '\n')
    
    all_master_new = []
    if new_android:
        all_master_new.extend([f"[ANDROID] {x}" for x in new_android])
    if new_phone:
        all_master_new.extend([f"[PHONE] {x}" for x in new_phone])
    if new_email:
        all_master_new.extend([f"[EMAIL] {x}" for x in new_email])
    if new_url:
        all_master_new.extend([f"[URL] {x}" for x in new_url])
    if new_other:
        all_master_new.extend([f"[OTHER] {x}" for x in new_other])
    
    if all_master_new:
        print(f"💾 Appending {len(all_master_new)} new entries to: {output_master_path}")
        with open(output_master_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(all_master_new) + '\n')
    
    print("\n" + "=" * 100)
    print(f"✅ SCAN COMPLETE AT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print(f"📊 FINAL STATISTICS")
    print("=" * 100)
    print(f"Total folders scanned: {total_folders}")
    print(f"Total files processed: {processed_files}")
    print(f"Total lines analyzed: {total_lines:,}")
    print("-" * 100)
    print(f"📱 Android package combos (new): {len(new_android)} (total: {len(existing_android)})")
    print(f"📞 Phone number combos (new): {len(new_phone)} (total: {len(existing_phone)})")
    print(f"✉️  Email combos (new): {len(new_email)} (total: {len(existing_email)})")
    print(f"🔗 URL combos (new): {len(new_url)} (total: {len(existing_url)})")
    print(f"🔑 Other username combos (new): {len(new_other)} (total: {len(existing_other)})")
    print("-" * 100)
    print(f"🎯 TOTAL NEW CREDENTIALS ADDED: {len(new_android) + len(new_phone) + len(new_email) + len(new_url) + len(new_other)}")
    print(f"🎯 TOTAL UNIQUE CREDENTIALS OVERALL: {len(existing_android) + len(existing_phone) + len(existing_email) + len(existing_url) + len(existing_other)}")
    print("=" * 100)
    print(f"📁 OUTPUT FILES LOCATION: {output_folder}")
    print("=" * 100)
    print(f"  📄 package_android.txt")
    print(f"  📄 loginnumberpass.txt")
    print(f"  📄 emailuserpass.txt")
    print(f"  📄 urlcombouserpass.txt")
    print(f"  📄 other_usernames_passwords.txt")
    print(f"  📄 ALL_CREDENTIALS_MASTER.txt")
    print("=" * 100)

if __name__ == "__main__":
    folder_path = input("Enter folder path: ").strip()
    if os.path.exists(folder_path):
        process_files(folder_path)
    else:
        print("Invalid folder path")
