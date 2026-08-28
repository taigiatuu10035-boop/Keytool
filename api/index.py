from http.server import BaseHTTPRequestHandler
import json
import secrets
import hashlib
from datetime import datetime, timedelta, timezone


class handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        self.wfile.write(body)

    def do_GET(self):

        try:
            # Tạo mã ngẫu nhiên
            raw_key = secrets.token_hex(16).upper()

            key = "TUUDZ-" + raw_key

            # Thời gian tạo
            now = datetime.now(timezone.utc)

            # Key có hiệu lực 24 giờ
            expires = now + timedelta(hours=24)

            self.send_json({
                "success": True,
                "key": key,
                "created_at": now.isoformat(),
                "expires_at": expires.isoformat(),
                "message": "Tạo key thành công"
            })

        except Exception as e:

            self.send_json({
                "success": False,
                "message": str(e)
            }, 500)
