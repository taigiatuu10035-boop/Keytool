from http.server import BaseHTTPRequestHandler
import json
import secrets
import os
import requests

from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse, parse_qs

from supabase import create_client


# =========================================================
# CONFIG
# =========================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
LINK4M_API = os.environ.get("LINK4M_API")

BASE_URL = "https://keytool-tuudz.vercel.app"


# =========================================================
# SUPABASE
# =========================================================

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Thiếu SUPABASE_URL hoặc SUPABASE_KEY"
    )

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# HANDLER
# =========================================================

class handler(BaseHTTPRequestHandler):

    # -----------------------------------------------------
    # SEND JSON
    # -----------------------------------------------------

    def send_json(self, data, status=200):

        body = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(body)


    # -----------------------------------------------------
    # SEND HTML
    # -----------------------------------------------------

    def send_html(self, html, status=200):

        body = html.encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(body)


    # =====================================================
    # GET
    # =====================================================

    def do_GET(self):

        try:

            parsed = urlparse(self.path)

            path = parsed.path

            params = parse_qs(parsed.query)


            # =================================================
            # /api
            # =================================================

            if path in ["/api", "/api/"]:

                self.api_start()

                return


            # =================================================
            # /verify
            # =================================================

            if path == "/verify":

                session_id = params.get(
                    "session",
                    [""]
                )[0]

                self.verify_session(session_id)

                return


            # =================================================
            # /check_key
            # =================================================

            if path == "/check_key":

                key = params.get(
                    "key",
                    [""]
                )[0]

                device_id = params.get(
                    "device_id",
                    [""]
                )[0]

                self.check_key(
                    key,
                    device_id
                )

                return


            # =================================================
            # HOME
            # =================================================

            self.home()


        except Exception as e:

            self.send_json(
                {
                    "success": False,
                    "message": str(e)
                },
                500
            )


    # =====================================================
    # HOME
    # =====================================================

    def home(self):

        html = """
<!DOCTYPE html>

<html lang="vi">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1"
>

<title>TUUDZ GET KEY</title>

<style>

body{
    margin:0;
    min-height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#101010;
    color:white;
    font-family:Arial,sans-serif;
}

.card{
    width:88%;
    max-width:400px;
    background:#1c1c1c;
    padding:30px;
    border-radius:20px;
    text-align:center;
    box-shadow:0 0 30px rgba(0,255,120,.15);
}

h1{
    color:#00ff88;
}

button{
    width:100%;
    padding:15px;
    border:0;
    border-radius:10px;
    background:#00ff88;
    color:#000;
    font-size:17px;
    font-weight:bold;
}

.info{
    color:#aaa;
    line-height:1.6;
}

</style>

</head>

<body>

<div class="card">

<h1>🔑 TUUDZ GET KEY</h1>

<p class="info">
Mỗi thiết bị sẽ có một KEY riêng.
<br>
KEY có hiệu lực 24 giờ.
</p>

<button onclick="getKey()">
🚀 GET KEY
</button>

<p id="msg"></p>

</div>


<script>

async function getKey(){

    const msg =
        document.getElementById("msg");

    msg.innerText =
        "⏳ Đang tạo link...";

    try{

        const response =
            await fetch("/api");

        const data =
            await response.json();

        if(!data.success){

            msg.innerText =
                "❌ " + data.message;

            return;
        }

        window.location.href =
            data.url;

    }catch(error){

        msg.innerText =
            "❌ Không thể kết nối server.";

    }

}

</script>

</body>

</html>
"""

        self.send_html(html)


    # =====================================================
    # API START
    # =====================================================

    def api_start(self):

        if not LINK4M_API:

            self.send_json(
                {
                    "success": False,
                    "message":
                    "Thiếu LINK4M_API trên Vercel"
                },
                500
            )

            return


        # -----------------------------------------------
        # Tạo session
        # -----------------------------------------------

        session_id = secrets.token_urlsafe(32)


        # -----------------------------------------------
        # Device ID
        # -----------------------------------------------

        device_id = (
            self.headers.get("X-Forwarded-For")
            or self.client_address[0]
            or "unknown"
        )

        device_id = device_id.split(",")[0].strip()


        # -----------------------------------------------
        # Session hết hạn sau 30 phút
        # -----------------------------------------------

        now = datetime.now(timezone.utc)

        expires = now + timedelta(
            minutes=30
        )


        # -----------------------------------------------
        # Lưu session
        # -----------------------------------------------

        supabase.table(
            "key_sessions"
        ).insert(
            {
                "session_id": session_id,
                "device_id": device_id,
                "expires_at": expires.isoformat()
            }
        ).execute()


        # -----------------------------------------------
        # URL quay lại
        # -----------------------------------------------

        destination = (
            f"{BASE_URL}/verify"
            f"?session={session_id}"
        )


        # -----------------------------------------------
        # Gọi Link4m
        # -----------------------------------------------

        response = requests.get(
            "https://link4m.co/api-shorten/v2",
            params={
                "api": LINK4M_API,
                "url": destination
            },
            timeout=10
        )


        data = response.json()


        if data.get("status") != "success":

            self.send_json(
                {
                    "success": False,
                    "message":
                    data.get(
                        "message",
                        "Link4m lỗi"
                    )
                },
                500
            )

            return


        shortened_url = data.get(
            "shortenedUrl"
        )


        if not shortened_url:

            self.send_json(
                {
                    "success": False,
                    "message":
                    "Link4m không trả về shortenedUrl"
                },
                500
            )

            return


        # -----------------------------------------------
        # Trả link Link4m
        # -----------------------------------------------

        self.send_json(
            {
                "success": True,
                "url": shortened_url,
                "message":
                "Đã tạo link vượt"
            }
        )


    # =====================================================
    # VERIFY
    # =====================================================

    def verify_session(self, session_id):

        if not session_id:

            self.send_html(
                "<h2>❌ Session không hợp lệ.</h2>",
                400
            )

            return


        result = (
            supabase
            .table("key_sessions")
            .select("*")
            .eq("session_id", session_id)
            .limit(1)
            .execute()
        )


        if not result.data:

            self.send_html(
                "<h2>❌ Session không tồn tại.</h2>",
                400
            )

            return


        session = result.data[0]


        expires = datetime.fromisoformat(
            session["expires_at"]
            .replace("Z", "+00:00")
        )


        if datetime.now(timezone.utc) > expires:

            self.send_html(
                "<h2>❌ Phiên đã hết hạn.</h2>",
                400
            )

            return


        device_id = session["device_id"]


        # -----------------------------------------------
        # Tạo KEY
        # -----------------------------------------------

        key = (
            "TUUDZ-"
            + secrets.token_hex(16).upper()
        )


        now = datetime.now(timezone.utc)

        key_expires = (
            now + timedelta(hours=24)
        )


        # -----------------------------------------------
        # Lưu KEY vào Supabase
        # -----------------------------------------------

        supabase.table(
            "keys"
        ).insert(
            {
                "key_code": key,
                "device_id": device_id,
                "key_date": now.date().isoformat(),
                "created_at": now.isoformat(),
                "expires_at":
                    key_expires.isoformat(),
                "used": False
            }
        ).execute()


        # -----------------------------------------------
        # Xóa session đã dùng
        # -----------------------------------------------

        supabase.table(
            "key_sessions"
        ).delete().eq(
            "session_id",
            session_id
        ).execute()


        # -----------------------------------------------
        # Hiển thị KEY
        # -----------------------------------------------

        html = f"""
<!DOCTYPE html>

<html lang="vi">

<head>

<meta charset="UTF-8">

<meta
name="viewport"
content="width=device-width,initial-scale=1"
>

<title>KEY TUUDZ</title>

<style>

body{{
    margin:0;
    min-height:100vh;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#101010;
    color:white;
    font-family:Arial;
}}

.card{{
    width:88%;
    max-width:450px;
    background:#1c1c1c;
    padding:30px;
    border-radius:20px;
    text-align:center;
}}

.key{{
    background:#00ff88;
    color:#000;
    padding:18px;
    border-radius:10px;
    font-weight:bold;
    word-break:break-all;
    font-size:18px;
}}

</style>

</head>

<body>

<div class="card">

<h2>✅ GET KEY THÀNH CÔNG</h2>

<p>KEY của bạn:</p>

<div class="key">
{key}
</div>

<p>
⏰ Hiệu lực: 24 giờ
</p>

</div>

</body>

</html>
"""

        self.send_html(html)


    # =====================================================
    # CHECK KEY
    # =====================================================

    def check_key(
        self,
        key,
        device_id
    ):

        if not key:

            self.send_json(
                {
                    "success": False,
                    "message":
                    "Thiếu KEY"
                },
                400
            )

            return


        result = (
            supabase
            .table("keys")
            .select("*")
            .eq("key_code", key)
            .limit(1)
            .execute()
        )


        if not result.data:

            self.send_json(
                {
                    "success": False,
                    "message":
                    "KEY không tồn tại"
                }
            )

            return


        info = result.data[0]


        # -----------------------------------------------
        # Kiểm tra hạn
        # -----------------------------------------------

        expires = datetime.fromisoformat(
            info["expires_at"]
            .replace("Z", "+00:00")
        )


        if datetime.now(timezone.utc) > expires:

            self.send_json(
                {
                    "success": False,
                    "message":
                    "KEY đã hết hạn"
                }
            )

            return


        # -----------------------------------------------
        # Kiểm tra thiết bị
        # -----------------------------------------------

        if (
            device_id
            and info["device_id"] != device_id
        ):

            self.send_json(
                {
                    "success": False,
                    "message":
                    "KEY không thuộc thiết bị này"
                }
            )

            return


        self.send_json(
            {
                "success": True,
                "message":
                "KEY hợp lệ",
                "expires_at":
                info["expires_at"]
            }
        )
