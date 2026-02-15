<?php
// Твой токен и ID уже здесь
$botToken = "8478893095:AAGwYkX40jhE6P1EoFJnaD4p0ruQKM4c8aU";
$adminChatId = "5962134875"; 

if (isset($_GET['action']) && $_GET['action'] == 'send_order') {
    $userName = $_POST['name'] ?? 'Не указано';
    $userPhone = $_POST['phone'] ?? 'Не указано';
    $orderData = $_POST['order'] ?? 'Пусто';

    $text = "НОВЫЙ ЗАКАЗ AUTO67\n";
    $text .= "━━━━━━━━━━━━━━━\n";
    $text .= "Клиент: " . $userName . "\n";
    $text .= "Тел: " . $userPhone . "\n";
    $text .= "━━━━━━━━━━━━━━━\n";
    $text .= "Заказ:\n" . $orderData;

    $url = "https://api.telegram.org/bot$botToken/sendMessage";
    
    $postData = [
        'chat_id' => $adminChatId,
        'text' => $text
    ];

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($postData));
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $result = curl_exec($ch);
    curl_close($ch);

    header('Content-Type: application/json');
    echo json_encode(["status" => "success"]);
    exit;
}
?>