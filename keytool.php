<?php
header('Access-Control-Allow-Origin: *');

// 1. Chìa khóa bí mật dùng để mã hóa Key Free 24h
$SECRET_KEY = "TUUDZ_SECRET_2026";

// 2. Danh sách Key VIP bán riêng (MÃ_KEY => NĂM-THÁNG-NGÀY GIỜ:PHÚT:GIÂY)
$VIP_KEYS = [
    "VIP-TUUDZ-3NGAY"    => "2026-08-31 23:59:59",
    "VIP-TUUDZ-30NGAY"   => "2026-09-28 23:59:59",
    "VIP-TUUDZ-VINHVIEN"  => "2099-12-31 23:59:59"
];

// 3. Tự động tính Key Free 24h của ngày hôm nay
$today = date("Ymd");
$free_key_today = "KEY-" . strtoupper(substr(md5($today . "-" . $SECRET_KEY), 0, 10));

// --- XỬ LÝ API KHI TOOL PYTHON GỬI YÊU CẦU KIỂM TRA ---
if (isset($_GET['check_key'])) {
    header('Content-Type: application/json');
    $user_key = trim($_GET['check_key']);

    // Check 1: Key Free 24h
    if ($user_key === $free_key_today) {
        echo json_encode(["status" => "success", "type" => "FREE 24H", "msg" => "Key 24h hợp lệ"]);
        exit;
    }

    // Check 2: Key VIP (3 ngày, 30 ngày, vĩnh viễn)
    if (array_key_exists($user_key, $VIP_KEYS)) {
        $expire_time = strtotime($VIP_KEYS[$user_key]);
        if (time() < $expire_time) {
            echo json_encode(["status" => "success", "type" => "VIP", "expire" => $VIP_KEYS[$user_key]]);
            exit;
        } else {
            echo json_encode(["status" => "error", "msg" => "Key VIP này đã hết hạn!"]);
            exit;
        }
    }

    echo json_encode(["status" => "error", "msg" => "Key không chính xác hoặc đã hết hạn!"]);
    exit;
}
?>

<!-- GIAO DIỆN HIỂN THỊ TRÊN TRÌNH DUYỆT KHI KHÁCH VƯỢT LINK XONG -->
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Get Key Tool VIP</title>
    <style>
        body { background: #121212; color: #fff; font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: #1e1e1e; padding: 25px; border-radius: 12px; text-align: center; border: 1px solid #00ff88; box-shadow: 0 0 15px rgba(0,255,136,0.3); width: 300px; }
        .avatar { width: 80px; height: 80px; border-radius: 50%; margin-bottom: 10px; border: 2px solid #00ff88; }
        .key-box { background: #00ff88; color: #000; font-size: 20px; font-weight: bold; padding: 12px; border-radius: 6px; margin-top: 15px; word-break: break-all; }
    </style>
</head>
<body>
    <div class="card">
        <h3>🔑 HỆ THỐNG GET KEY</h3>
        <p style="color: #aaa; margin-top: -10px;">Developer & Admin</p>
        <hr style="border-color: #333;">
        <p>Key Ngày <b><?php echo date("d/m/Y"); ?></b> Của Bạn Là:</p>
        <div class="key-box"><?php echo $free_key_today; ?></div>
        <p style="font-size: 12px; color: #888; margin-top: 15px;">Key tự đổi lúc 00:00 mỗi ngày</p>
    </div>
</body>
</html>
