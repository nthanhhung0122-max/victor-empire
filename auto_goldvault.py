"""
Tool tự động Gold Vault (@goldvaults_bot) chạy 24/7 trên GitHub Actions
- Tự động lấy tgWebAppData qua Telethon session
- Tự động điểm danh hàng ngày (Daily Reward +10 Gold)
- Tự động bán Vàng (Sell Gold -> Coins & Cash)
- Tự động tái đầu tư mua Wooden Pickaxe khi >= 500 Cash
- Hỗ trợ đa tài khoản
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

BASE_URL = "https://gold-vault.tanphucc414.workers.dev/api"

def log(tag, msg, color=Fore.CYAN):
    print(f"{Fore.WHITE}[{time.strftime('%H:%M:%S')}] {color}[{tag}] {Style.RESET_ALL}{msg}", flush=True)

async def get_tg_web_app_data(session_str):
    try:
        client = TelegramClient(StringSession(session_str), API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return None
        bot = await client.get_input_entity('goldvaults_bot')
        res = await client(RequestWebViewRequest(
            peer=bot, bot=bot, platform='android', url='https://gold-dxm.pages.dev/'
        ))
        await client.disconnect()
        frag = urllib.parse.urlparse(res.url).fragment
        return urllib.parse.parse_qs(frag).get('tgWebAppData', [None])[0]
    except Exception as e:
        log("AUTH_ERR", f"Lỗi lấy session: {e}", Fore.RED)
        return None

def api_call(endpoint, tg_data, body=None):
    url = BASE_URL + endpoint
    headers = {
        'Content-Type': 'application/json',
        'X-Init-Data': tg_data,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'Origin': 'https://gold-dxm.pages.dev',
        'Referer': 'https://gold-dxm.pages.dev/'
    }
    try:
        r = requests.post(url, headers=headers, json=body or {}, timeout=15)
        return r.status_code, r.json() if r.headers.get('content-type', '').startswith('application/json') else r.text
    except Exception as e:
        return 0, str(e)

def process_account(acc):
    name = acc['name']
    log("ACC", f"=== Đang xử lý: {name} ===", Fore.MAGENTA)
    
    tg_data = asyncio.run(get_tg_web_app_data(acc['session']))
    if not tg_data:
        log("ERR", f"[{name}] Không lấy được WebAppData!", Fore.RED)
        return

    # 1. Get Me
    code, me_data = api_call('/me', tg_data)
    if code != 200 or not isinstance(me_data, dict):
        log("ERR", f"[{name}] Không lấy được thông tin: {me_data}", Fore.RED)
        return
        
    u = me_data.get('u', {})
    coins = u.get('coins', 0)
    cash = u.get('cash', 0)
    gold = u.get('gold', 0)
    wallet = u.get('wallet') or 'Chưa liên kết'
    own = u.get('own', {})
    log("INFO", f"[{name}] Coins: {Fore.YELLOW}{coins} | Cash: {Fore.GREEN}{cash} | Gold: {Fore.YELLOW}{gold:.2f} | Cuốc: {own} | Ví: {wallet}")

    # 2. Check Daily
    last_daily = u.get('daily', 0)
    now = me_data.get('now', time.time() * 1000)
    if now - last_daily >= 86400000:
        log("DAILY", f"[{name}] 🎁 Đang nhận thưởng Daily...")
        c_code, c_res = api_call('/act', tg_data, {"a": "daily", "wp": 0})
        if c_code == 200 and isinstance(c_res, dict) and c_res.get('ok'):
            log("DAILY", f"[{name}] ✅ Nhận Daily thành công! (+10 Gold)", Fore.GREEN)
        else:
            log("DAILY", f"[{name}] ⚠️ Lỗi nhận daily: {c_res}", Fore.YELLOW)
    else:
        left_h = (86400000 - (now - last_daily)) / 3600000
        log("DAILY", f"[{name}] Đã điểm danh hôm nay. Còn {left_h:.1f}h nữa.")

    # 3. Sell Gold (nếu có >= 20 gold)
    if gold >= 20:
        log("SELL", f"[{name}] 💰 Bán {int(gold)} Vàng thành Coins & Cash...")
        c_code, c_res = api_call('/act', tg_data, {"a": "sell", "wp": 0})
        if c_code == 200 and isinstance(c_res, dict) and c_res.get('ok'):
            u_new = c_res.get('u', {})
            coins = u_new.get('coins', coins)
            cash = u_new.get('cash', cash)
            log("SELL", f"[{name}] ✅ Đã bán xong! Coins mới: {coins}, Cash mới: {cash}", Fore.GREEN)
        else:
            log("SELL", f"[{name}] ⚠️ Lỗi bán vàng: {c_res}", Fore.YELLOW)
    else:
        log("SELL", f"[{name}] Vàng hiện tại ({gold:.2f}) chưa đủ 20 để bán.")

    # 4. Auto Buy Pickaxe (nếu đủ 500 cash)
    if cash >= 500:
        log("SHOP", f"[{name}] 🔨 Đủ {cash} Cash -> Tiến hành mua thêm Wooden Pickaxe (500 Cash)...")
        b_code, b_res = api_call('/act', tg_data, {"a": "buy", "id": "wood", "wp": 0})
        if b_code == 200 and isinstance(b_res, dict) and b_res.get('ok'):
            log("SHOP", f"[{name}] ✅ Mua cuốc thành công! Tăng tốc độ đào.", Fore.GREEN)

def run_once(target_acc=None):
    accs = [a for a in ACCOUNTS if target_acc is None or a['name'].startswith(f'Acc {target_acc}')]
    for acc in accs:
        if acc['session']:
            process_account(acc)
            print("-" * 50, flush=True)

def main():
    print(f"{Fore.YELLOW}{'='*50}", flush=True)
    print(f"{Fore.CYAN}    GOLD VAULT AUTOMATION TOOL (@goldvaults_bot) 24/7", flush=True)
    print(f"{Fore.YELLOW}{'='*50}\n", flush=True)
    
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
