from datetime import datetime
import hashlib
import os
import sys

# Khóa bí mật (Khớp với khóa trong file HTML)
SECRET_KEY = "TUUDZ_SECRET_8888"

# DÁN LINK RÚT GỌN TẠI BƯỚC 3 VÀO ĐÂY
LINK_VUOT_KEY = "https://site2s.com/FJSCnLv"


def get_hwid():
    raw_info = (
        os.uname().nodename
        + os.uname().machine
        + os.environ.get("USER", "default")
    )
    return hashlib.md5(raw_info.encode()).hexdigest()[:8].upper()


def generate_valid_key(hwid):
    today_str = datetime.now().strftime("%Y%m%d")
    mix_data = f"{hwid}-{today_str}-{SECRET_KEY}"
    valid_hash = hashlib.md5(mix_data.encode()).hexdigest()[:10].upper()
    return f"KEY-{valid_hash}"


def check_user_key():
    hwid = get_hwid()
    correct_key = generate_valid_key(hwid)

    print("\033[1;36m┌── 🔑 HỆ THỐNG XÁC THỰC KEY TOOL\033[0m")
    print(f"\033[1;33m├── 📲 HWID Máy bạn: \033[1;32m{hwid}\033[0m")
    print(
        f"\033[1;35m├── 🌐 Truy cập link để lấy Key: {LINK_VUOT_KEY}\033[0m"
    )
    print("\033[1;36m├───\033[0m")

    user_input_key = input(
        "\033[1;33m└──👉 Nhập Key kích hoạt: \033[0m"
    ).strip()

    if user_input_key == correct_key:
        print(
            "\033[1;32m\n✅ XÁC THỰC THÀNH CÔNG! ĐANG MỞ TOOL...\033[0m\n"
        )
        return True
    else:
        print(
            "\033[1;31m\n❌ KEY SAI HOẶC KHÔNG PHẢI CỦA MÁY NÀY!\033[0m"
        )
        sys.exit()


# Chạy hàm kiểm tra ngay khi mở tool
check_user_key()

