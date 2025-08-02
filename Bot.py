import requests
import time
import ta
import pandas as pd

# 🔑 توکن و chat_id خودت رو اینجا بذار
BOT_TOKEN = "توکن_ربات_تلگرام"
CHAT_ID = "چت_آیدی_خودت"

# تنظیمات
SYMBOLS = ["XRPUSDT", "DOGEUSDT", "ADAUSDT"]
INTERVAL = "1m"
LIMIT = 50  # تعداد کندل برای محاسبات
CHECK_INTERVAL = 60  # هر چند ثانیه یکبار بررسی کند

last_signal = {}

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, json=payload)

def get_klines(symbol):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={INTERVAL}&limit={LIMIT}"
    r = requests.get(url).json()
    df = pd.DataFrame(r, columns=["time","o","h","l","c","v","close_time","q","n","tbb","tbq","ignore"])
    df["c"] = df["c"].astype(float)
    return df

def generate_signal(df):
    df["rsi"] = ta.momentum.RSIIndicator(df["c"], window=14).rsi()
    df["ema_fast"] = ta.trend.EMAIndicator(df["c"], window=9).ema_indicator()
    df["ema_slow"] = ta.trend.EMAIndicator(df["c"], window=21).ema_indicator()

    rsi = df["rsi"].iloc[-1]
    ema_fast = df["ema_fast"].iloc[-1]
    ema_slow = df["ema_slow"].iloc[-1]
    price = df["c"].iloc[-1]

    if rsi < 30 and ema_fast > ema_slow:
        return f"🟢 سیگنال خرید! قیمت: {price:.4f} | RSI={rsi:.1f}"
    elif rsi > 70 and ema_fast < ema_slow:
        return f"🔴 سیگنال فروش! قیمت: {price:.4f} | RSI={rsi:.1f}"
    else:
        return None

while True:
    try:
        for sym in SYMBOLS:
            df = get_klines(sym)
            signal = generate_signal(df)

            if signal and last_signal.get(sym) != signal:
                send_telegram_message(f"📊 [{sym}] {signal}")
                last_signal[sym] = signal

        time.sleep(CHECK_INTERVAL)

    except Exception as e:
        print("⚠️ Error:", e)
        time.sleep(10)
