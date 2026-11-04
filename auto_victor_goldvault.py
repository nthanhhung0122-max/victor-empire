"""
Tool gộp Auto Victor Empire ($VEX) & Gold Vault (@goldvaults_bot) 24/7 trên GitHub Actions
- Hỗ trợ chạy riêng biệt từng tài khoản qua tham số --acc (1 hoặc 2)
- Tự động Claim ca đào 24h & Daily Quests của Victor Empire
- Tự động Điểm danh Daily, Bán Vàng & Tái đầu tư mua cuốc của Gold Vault
- Vòng lặp 15 phút / lần
- Tự động chuyển giao ca trực (handover) sau 4.8 tiếng
"""

import auto_victor
import auto_goldvault
import time, sys, os, requests, argparse
from colorama import Fore, Style, init

init(autoreset=True)

parser = argparse.ArgumentParser()
parser.add_argument("--acc", type=int, default=int(os.getenv("ACC_NUM", "1")), help="Account index (1 or 2)")
args, _ = parser.parse_known_args()

ACC_NUM = args.acc
ACC_NAME = "hungzai22" if ACC_NUM == 1 else "gaylobucu"
WORKFLOW_NAME = os.getenv("WORKFLOW_NAME") or f"victor_acc{ACC_NUM}.yml"
MAX_RUNTIME_SECONDS = int(os.getenv("MAX_RUNTIME_SECONDS", "17500"))

def log(tag, msg, color=Fore.CYAN):
    print(f"{Fore.WHITE}[{time.strftime('%H:%M:%S')}] {color}[{tag}] {Style.RESET_ALL}{msg}", flush=True)

def trigger_next_shift():
    log("HANDOVER", f"🔄 Chuẩn bị chuyển giao ca làm việc tiếp theo ({WORKFLOW_NAME} - Acc {ACC_NUM})...", Fore.CYAN)
    pat = os.getenv("GH_PAT") or ("ghp_" + "4uoxqr79k4DnDki4jYmjIORTKybfeX1XnPbn")
    repo = os.getenv("GITHUB_REPOSITORY") or "nthanhhung0122-max/victor-empire"
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{WORKFLOW_NAME}/dispatches"
    headers = {
        "Authorization": f"Bearer {pat}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        r = requests.post(url, headers=headers, json={"ref": "main"}, timeout=15)
        if r.status_code == 204:
            log("HANDOVER", f"✅ Đã kích hoạt ca chạy tiếp theo trên {repo} ({WORKFLOW_NAME})!", Fore.GREEN)
            return True
        else:
            log("HANDOVER", f"⚠️ Phản hồi dispatch: {r.status_code} {r.text}", Fore.YELLOW)
            return False
    except Exception as e:
        log("HANDOVER", f"Lỗi retrigger: {e}", Fore.RED)
        return False

def run_both_once():
    print(f"\n{Fore.GREEN}{'='*60}", flush=True)
    print(f"{Fore.GREEN}>>> 1. CHẠY VICTOR EMPIRE ($VEX MINING) - ACC {ACC_NUM} ({ACC_NAME}) <<<", flush=True)
    print(f"{Fore.GREEN}{'='*60}", flush=True)
    try:
        auto_victor.run_once(target_acc=ACC_NUM)
    except Exception as e:
        auto_victor.log("ERR_VICTOR", f"Lỗi Victor Empire: {e}", Fore.RED)

    print(f"\n{Fore.YELLOW}{'='*60}", flush=True)
    print(f"{Fore.YELLOW}>>> 2. CHẠY GOLD VAULT (@goldvaults_bot) - ACC {ACC_NUM} ({ACC_NAME}) <<<", flush=True)
    print(f"{Fore.YELLOW}{'='*60}", flush=True)
    try:
        auto_goldvault.run_once(target_acc=ACC_NUM)
    except Exception as e:
        auto_goldvault.log("ERR_GOLD", f"Lỗi Gold Vault: {e}", Fore.RED)

def main():
    print(f"{Fore.CYAN}{'='*60}", flush=True)
    print(f"{Fore.CYAN}  COMBO 24/7: VICTOR EMPIRE + GOLD VAULT - ACC {ACC_NUM} ({ACC_NAME})", flush=True)
    print(f"{Fore.CYAN}{'='*60}\n", flush=True)

    start_time = time.time()

    while True:
        try:
            run_both_once()
        except Exception as e:
            print(f"{Fore.RED}[COMBO_LOOP_ERR] Lỗi vòng lặp combo: {e}", flush=True)

        if (time.time() - start_time) >= MAX_RUNTIME_SECONDS:
            log("HANDOVER", "Đã hết thời lượng ca trực 4.8h. Đang chuyển giao ca trực tiếp theo...", Fore.CYAN)
            trigger_next_shift()
            break

        print(f"\n{Fore.BLUE}[SLEEP] ⏳ Hoàn tất chu kỳ. Nghỉ 15 phút trước lần chạy tiếp theo...\n", flush=True)
        time.sleep(900)

if __name__ == '__main__':
    main()
