"""
Tool tự động Victor Empire (@VictorEmpireBot) chạy 24/7 trên GitHub Actions
- Tự động lấy tgWebAppData qua Telethon session
- Tự động điểm danh hàng ngày (Daily Check-in)
- Tự động hoàn thành Daily Story (+5 VEX)
- Tự động thu hoạch ca đào (Claim Shift Mining khi >= 0.1 VEX)
- Tự động nhận thưởng nhiệm vụ & hoa hồng bạn bè (Crew)
- Vòng lặp 15 phút / lần
"""

import asyncio, os, time, sys, urllib.parse, requests
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import RequestWebViewRequest
from colorama import init, Fore, Style

init(autoreset=True)

API_ID = 39182276
API_HASH = 'f02b155d895a3a3fbf8a1cbe810b5338'

ACCOUNTS = [
    {
        "name": "Acc 1 (hungzai22)",
        "session": os.getenv("TELEGRAM_STRING_SESSION_ACC1") or "1BVtsOHIBuxmpWiBJ9hvwV9pSrzWw5U2I5Fe20Ww8l1LCk9rnsG6T6lLZEJXZE1JJC_qUH_yyWHnRoedRNI5lJYnfjRN4gyGeDrCxquDU12ZflrpCz0VLhMZx2C0LlyUCy2eHRSRE1wUCpEYZaymL0P7Z9eAHwMy4Oogewh5TqyO4x4MF6j0yTq8Zvfpv43O4aQDzErNv3GRqpx8DXBcOJIMP9yVhq-Mby5VH5J9cF-h-bJ5ws3xKjA4GY7YKjHxDt9OI-Zr7mr-V3qZy99UxJooThJj51f2RqOKhODdLh9XZQ0ygSoAd3iFAZDOPMEo8Ch5TrrzLXi2Q3N0HorIL1JfV0xoFQlY="
    },
    {
        "name": "Acc 2 (gaylobucu)",
        "session": os.getenv("TELEGRAM_STRING_SESSION_ACC2") or "1BVtsOHIBuzoeRtBOmpNGh2sdyxpZ5e0nY4MrFe-6KKbmJPaM0YnCJiKRI0L9mEh1C5rwqLQqucj456LRF7vV1YIPjZNqL6JevLM0Ww3FTml1NoKdwsiPINfsy9MbBlBhKOvha7py44L4pK5aEXjwpjpoNj4LaSmtWaPiQPufJuTwPB86f4gYjSeXM3HtxhnFU7MtHR5vbZPBa9N2HQSlt2BMB47q00DbQVtvYA37R3R-TrtV2MtwixL9ozChADFq38NYcw4eRyRwKrkobVLccvz0_hvqgHXiQbrfcFLLRkRGwGlRCB-Ew4YhLLdnCbG1hjGEfxUrp9MRmF0JvS-u20MfAuvlcgQ="
    }
]

BASE_URL = "https://app.victorempire.app/api"

def log(tag, msg, color=Fore.CYAN):
    print(f"{Fore.WHITE}[{time.strftime('%H:%M:%S')}] {color}[{tag}] {Style.RESET_ALL}{msg}", flush=True)

async def get_tg_web_app_data(session_str):
    try:
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return None
        bot = await client.get_input_entity('VictorEmpireBot')
        res = await client(RequestWebViewRequest(
            peer=bot, bot=bot, platform='android', url='https://app.victorempire.app/'
        ))
        await client.disconnect()
        frag = urllib.parse.urlparse(res.url).fragment
        return urllib.parse.parse_qs(frag).get('tgWebAppData', [None])[0]
    except Exception as e:
        log("AUTH_ERR", f"Lỗi lấy session: {e}", Fore.RED)
        return None

def api_call(endpoint, headers, method="GET", json_body=None):
    url = BASE_URL + endpoint
    try:
        if method == "POST":
            r = requests.post(url, headers=headers, json=json_body or {}, timeout=15)
        else:
            r = requests.get(url, headers=headers, timeout=15)
        return r.status_code, r.json() if r.headers.get('content-type', '').startswith('application/json') else r.text
    except Exception as e:
        return 0, str(e)

def claim_with_ad_helper(endpoint, headers, kind, extra_body=None):
    body = dict(extra_body or {})
    body['check'] = True
    code, pre = api_call(endpoint, headers, "POST", body)
    if code != 200:
        return False, pre
    
    ad_token = None
    if isinstance(pre, dict) and pre.get('needAd'):
        _, ad_res = api_call('/claim-ad/start', headers, "POST", {"kind": kind})
        if isinstance(ad_res, dict):
            ad_token = ad_res.get('token')
            
    claim_body = dict(extra_body or {})
    if ad_token:
        claim_body['adToken'] = ad_token
    return api_call(endpoint, headers, "POST", claim_body)

def process_account(acc):
    name = acc['name']
    log("ACC", f"=== Đang xử lý: {name} ===", Fore.MAGENTA)
    
    tg_data = asyncio.run(get_tg_web_app_data(acc['session']))
    if not tg_data:
        log("ERR", f"[{name}] Không lấy được WebAppData!", Fore.RED)
        return

    headers = {
        'content-type': 'application/json',
        'x-init-data': tg_data,
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'origin': 'https://app.victorempire.app',
        'referer': 'https://app.victorempire.app/'
    }

    # 1. Bootstrap
    code, bs = api_call('/bootstrap', headers)
    if code != 200 or not isinstance(bs, dict):
        log("ERR", f"[{name}] Bootstrap thất bại: {bs}", Fore.RED)
        return
        
    user = bs.get('user', {})
    balance = user.get('balance', 0)
    level = user.get('level', 1)
    title = user.get('title', 'Squire')
    wallet = user.get('wallet', {}).get('address') if user.get('wallet') else 'Chưa liên kết'
    log("INFO", f"[{name}] {Fore.GREEN}{user.get('name')} | Level {level} ({title}) | Balance: {Fore.YELLOW}{balance:.4f} VEX | Wallet: {wallet}")

    # 2. Check & Claim Daily Check-in
    code, tasks_data = api_call('/tasks', headers)
    if code == 200 and isinstance(tasks_data, dict):
        ck = tasks_data.get('daily', {}).get('checkin', {})
        if not ck.get('claimed'):
            log("CHECKIN", f"[{name}] 🎁 Đang nhận Daily Check-in Ngày {ck.get('day', 1)}...")
            c_code, c_res = claim_with_ad_helper('/quests/checkin', headers, 'checkin')
            if c_code == 200 and isinstance(c_res, dict):
                log("CHECKIN", f"[{name}] ✅ Nhận thành công +{c_res.get('reward')} VEX!", Fore.GREEN)
            else:
                log("CHECKIN", f"[{name}] ⚠️ Thất bại: {c_res}", Fore.YELLOW)
        else:
            log("CHECKIN", f"[{name}] Đã điểm danh hôm nay rồi.")

        # 3. Check & Claim Story
        st = tasks_data.get('daily', {}).get('story', {})
        if st and not st.get('claimed'):
            log("STORY", f"[{name}] 📱 Bắt đầu nhiệm vụ Daily Story (+{st.get('reward')} VEX)...")
            api_call('/story/start', headers, "POST")
            time.sleep(16)
            s_code, s_res = api_call('/story/claim', headers, "POST")
            if s_code == 200 and isinstance(s_res, dict):
                log("STORY", f"[{name}] ✅ Nhận thành công +{s_res.get('reward')} VEX!", Fore.GREEN)
            else:
                log("STORY", f"[{name}] ⚠️ Không thể claim story: {s_res}", Fore.YELLOW)
        else:
            log("STORY", f"[{name}] Story hôm nay đã hoàn thành.")

    # 4. Check & Claim Shift Mining
    code, mine_data = api_call('/mine', headers)
    if code == 200 and isinstance(mine_data, dict):
        m = mine_data.get('mine', {})
        shift = m.get('shift', {})
        claim_min = m.get('claimMin', 0.1)
        now_s = mine_data.get('serverTime', time.time() * 1000)
        mined = shift.get('mined', 0) + max(0, min(now_s, shift.get('end', 0)) - shift.get('at', 0)) * shift.get('perMs', 0)
        log("MINE", f"[{name}] ⛏️ Mined: {mined:.6f} VEX (Tốc độ: {m.get('speed')} TH/s | Min claim: {claim_min} VEX)")
        
        if mined >= claim_min:
            log("MINE", f"[{name}] ⚡ Đang tiến hành Claim ca đào...")
            c_code, c_res = claim_with_ad_helper('/mine/claim', headers, 'claim')
            if c_code == 200 and isinstance(c_res, dict):
                log("MINE", f"[{name}] ✅ Claim thành công +{c_res.get('reward'):.6f} VEX! Bắt đầu ca đào mới 24h.", Fore.GREEN)
            else:
                log("MINE", f"[{name}] ⚠️ Lỗi claim mine: {c_res}", Fore.YELLOW)

    # 5. Check Referral Crew Bounty
    code, crew = api_call('/crew', headers)
    if code == 200 and isinstance(crew, dict):
        bonus = crew.get('bonus', {})
        pending_bonus = bonus.get('pending', 0)
        log("CREW", f"[{name}] 👥 Bạn bè: {bonus.get('qualified', 0)} người | Thưởng đang chờ: {pending_bonus} VEX")
        if pending_bonus > 0:
            c_code, c_res = api_call('/crew/claim', headers, "POST", {"kind": "bonus"})
            if c_code == 200:
                log("CREW", f"[{name}] ✅ Đã nhận thưởng bạn bè: {c_res}", Fore.GREEN)

def run_once(target_acc=None):
    accs = [a for a in ACCOUNTS if target_acc is None or a['name'].startswith(f'Acc {target_acc}')]
    for acc in accs:
        if acc['session']:
            process_account(acc)
            print("-" * 50, flush=True)

def main():
    print(f"{Fore.GREEN}{'='*50}", flush=True)
    print(f"{Fore.YELLOW}  VICTOR EMPIRE AUTOMATION TOOL - $VEX AUTO MINER 24/7", flush=True)
    print(f"{Fore.GREEN}{'='*50}\n", flush=True)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--once':
        run_once()
        return

    # Loop 24/7
    while True:
        try:
            run_once()
        except Exception as e:
            log("LOOP_ERR", f"Lỗi vòng lặp: {e}", Fore.RED)
        log("SLEEP", "⏳ Nghỉ 15 phút trước chu kỳ kiểm tra tiếp theo...", Fore.BLUE)
        time.sleep(900)

if __name__ == '__main__':
    main()
