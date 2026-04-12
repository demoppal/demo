import sys
import time

# engine.so ဖိုင်ရှိမရှိ စစ်ဆေးခြင်း
try:
    import engine
except ImportError:
    print("\033[0;31m[!] Error: engine.so ဖိုင်ကို မတွေ့ပါ။\033[00m")
    print("\033[0;33m[!] engine.py ကို compile အရင်လုပ်ပြီး engine.so လို့ နာမည်ပြောင်းပေးထားပါ။\033[00m")
    sys.exit(1)

def main():
    try:
        # engine.so ထဲမှာပါတဲ့ run_script() function ကို စတင်ခေါ်ယူခြင်း
        # (ID စစ်ဆေးခြင်းနဲ့ Engine bypass logic အားလုံး ဒီထဲမှာ ပါပြီးသားဖြစ်ပါတယ်)
        engine.run_script()
        
    except KeyboardInterrupt:
        # User က Ctrl+C နှိပ်ပြီး ပိတ်လိုက်ရင်
        print("\n\033[0;31m[!] Program ကို အသုံးပြုသူမှ ရပ်ဆိုင်းလိုက်ပါသည်။\033[00m")
        sys.exit(0)
        
    except Exception as e:
        # တခြားမထင်မှတ်ထားတဲ့ Error တက်လာရင် Script ပြုတ်မကျသွားအောင် ၁၀ စက္ကန့်နေရင် ပြန်စတင်မယ်
        print(f"\n\033[0;31m[!] မထင်မှတ်ထားသော Error တက်လာပါသည်: {e}\033[00m")
        print("\033[0;33m[*] ၁၀ စက္ကန့်အကြာတွင် အလိုအလျောက် ပြန်လည်စတင်ပါမည်...\033[00m")
        time.sleep(10)
        main()

if __name__ == "__main__":
    # Script စတင်ချိန်မှာ UI ပိုလှအောင် Screen ရှင်းပေးမယ်
    import os
    os.system('clear' if os.name == 'posix' else 'cls')
    
    main()
  
