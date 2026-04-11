import engine
import sys
import os

def main():
    try:
        # engine.so ထဲက Static ID ကို လှမ်းယူမယ်
        my_id = engine.get_static_id()
        
        # GitHub ကနေ ID ရှိမရှိ အရင်စစ်မယ်
        if engine.is_still_approved(my_id):
            # ID ရှိရင် Script ကို စတင်ပွင့်စေမယ်
            engine.start_process(my_id)
        else:
            # ID မရှိရင် Access Denied ပြမယ်
            os.system('clear' if os.name == 'posix' else 'cls')
            print("\033[1;31m" + "═"*40)
            print("        ACCESS DENIED - NOT APPROVED")
            print("═"*40 + "\033[00m")
            print(f"\n\033[0;36m[!] YOUR ID: \033[0;37m{my_id}\033[00m")
            print("\033[0;33m[*] Please register your ID first.\033[00m\n")
            
    except AttributeError:
        print("Error: engine.so file is corrupted or incompatible.")
    except KeyboardInterrupt:
        print("\n\033[0;31mStopped.\033[00m")

if __name__ == "__main__":
    main()
    
