"""
Tool gộp Auto Victor Empire ($VEX) & Gold Vault (@goldvaults_bot) 24/7 trên 1 Runner duy nhất
- Tự động chạy cả 2 tài khoản (Acc 1 & Acc 2)
- Tự động Claim ca đào 24h & Daily Quests của Victor Empire
- Tự động Điểm danh Daily, Bán Vàng & Tái đầu tư mua cuốc của Gold Vault
- Vòng lặp 15 phút / lần
"""

import auto_victor
import auto_goldvault
import time, sys
from colorama import Fore

def run_both_once():
    print(f"\n{Fore.GREEN}{'='*60}", flush=True)
    print(f"{Fore.GREEN}>>> 1. CHẠY VICTOR EMPIRE ($VEX MINING) - ACC 1 & ACC 2 <<<", flush=True)
    print(f"{Fore.GREEN}{'='*60}", flush=True)
    try:
        auto_victor.run_once()
    except Exception as e:
        auto_victor.log("ERR_VICTOR", f"Lỗi Victor Empire: {e}", Fore.RED)

    print(f"\n{Fore.YELLOW}{'='*60}", flush=True)
    print(f"{Fore.YELLOW}>>> 2. CHẠY GOLD VAULT (@goldvaults_bot) - ACC 1 & ACC 2 <<<", flush=True)
    print(f"{Fore.YELLOW}{'='*60}", flush=True)
    try:
        auto_goldvault.run_once()
    except Exception as e:
        auto_goldvault.log("ERR_GOLD", f"Lỗi Gold Vault: {e}", Fore.RED)

def main():
    print(f"{Fore.CYAN}{'='*60}", flush=True)
    print(f"{Fore.CYAN}  COMBO RUNNER 24/7: VICTOR EMPIRE + GOLD VAULT (MULTI-ACC)", flush=True)
    print(f"{Fore.CYAN}{'='*60}\n", flush=True)

    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        run_both_once()
        return

    while True:
        try:
            run_both_once()
        except Exception as e:
            print(f"{Fore.RED}[COMBO_LOOP_ERR] Lỗi vòng lặp combo: {e}", flush=True)
        print(f"\n{Fore.BLUE}[SLEEP] ⏳ Hoàn tất chu kỳ cho cả 2 game. Nghỉ 15 phút trước lần chạy tiếp theo...\n", flush=True)
        time.sleep(900)

if __name__ == '__main__':
    main()
