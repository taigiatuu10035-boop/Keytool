from datetime import datetime
import hashlib
from flask import Flask, jsonify, request

app = Flask(__name__)

SECRET_KEY = "TUUDZ_SECRET_2026"
VIP_KEYS = {
    "VIP-TUUDZ-3NGAY": "2026-08-31 23:59:59",
    "VIP-TUUDZ-30NGAY": "2026-09-28 23:59:59",
}


@app.route("/")
def home():
    today = datetime.now().strftime("%Y%m%d")
    free_key = (
        "KEY-"
        + hashlib.md5(f"{today}-{SECRET_KEY}".encode()).hexdigest()[:10].upper()
    )
    return f"""
    <div style="text-align:center;padding:50px;font-family:sans-serif;background:#121212;color:#fff;height:100vh;">
        <h2>🔑 HỆ THỐNG GET KEY</h2>
        <p>Key Ngày {datetime.now().strftime('%d/%m/%Y')} Của Bạn:</p>
        <h1 style="color:#00ff88;">{free_key}</h1>
    </div>
    """


@app.route("/check_key")
def check_key():
    user_key = request.args.get("key", "").strip()
    today = datetime.now().strftime("%Y%m%d")
    free_key = (
        "KEY-"
        + hashlib.md5(f"{today}-{SECRET_KEY}".encode()).hexdigest()[:10].upper()
    )

    if user_key == free_key:
        return jsonify(
            {"status": "success", "type": "FREE 24H", "msg": "Key hợp lệ"}
        )
    if user_key in VIP_KEYS:
        return jsonify({"status": "success", "type": "VIP"})

    return jsonify(
        {"status": "error", "msg": "Key không chính xác hoặc hết hạn!"}
    )
