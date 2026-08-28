from datetime import datetime
import hashlib
from flask import Flask, jsonify, request

app = Flask(__name__)

SECRET_KEY = "TUUDZ_SECRET_2026"
VIP_KEYS = {
    "VIP-TUUDZ-3NGAY": "2026-08-31 23:59:59",
    "VIP-TUUDZ-30NGAY": "2026-09-28 23:59:59",
    "VIP-TUUDZ-VINHVIEN": "2099-12-31 23:59:59",
}


@app.route("/")
def home():
    today = datetime.now().strftime("%Y%m%d")
    free_key = (
        "KEY-"
        + hashlib.md5(f"{today}-{SECRET_KEY}".encode()).hexdigest()[:10].upper()
    )
    today_show = datetime.now().strftime("%d/%m/%Y")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Get Key Tool</title>
        <style>
            body {{ background: #121212; color: #fff; font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ background: #1e1e1e; padding: 25px; border-radius: 12px; text-align: center; border: 1px solid #00ff88; width: 300px; }}
            .key-box {{ background: #00ff88; color: #000; font-size: 20px; font-weight: bold; padding: 12px; border-radius: 6px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h3>🔑 HỆ THỐNG GET KEY</h3>
            <p>Developer & Admin</p><hr style="border-color:#333">
            <p>Key Ngày <b>{today_show}</b> Của Bạn Là:</p>
            <div class="key-box">{free_key}</div>
            <p style="font-size: 12px; color: #888; margin-top: 15px;">Key tự đổi lúc 00:00 mỗi ngày</p>
        </div>
    </body>
    </html>
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
        expire_time = datetime.strptime(
            VIP_KEYS[user_key], "%Y-%m-%d %H:%M:%S"
        )
        if datetime.now() < expire_time:
            return jsonify(
                {
                    "status": "success",
                    "type": "VIP",
                    "expire": VIP_KEYS[user_key],
                }
            )
        else:
            return jsonify(
                {"status": "error", "msg": "Key VIP này đã hết hạn!"}
            )

    return jsonify(
        {"status": "error", "msg": "Key không chính xác hoặc hết hạn!"}
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
