<?php
/**
 * Elite Real Estate — دوال مشتركة لكل ملفات الـ API
 */

function elite_config() {
    static $c = null;
    if ($c === null) $c = require __DIR__ . '/../config.php';
    return $c;
}

function elite_dataset() {
    static $d = null;
    if ($d === null) {
        $path = __DIR__ . '/../../data/valuation-data.json';
        $raw = @file_get_contents($path);
        if ($raw === false) elite_fail('لم يتم العثور على ملف البيانات valuation-data.json', 500);
        $d = json_decode($raw, true);
        if (!is_array($d)) elite_fail('ملف البيانات غير صالح', 500);
    }
    return $d;
}

function elite_cors() {
    $cfg = elite_config();
    $origin = isset($_SERVER['HTTP_ORIGIN']) ? $_SERVER['HTTP_ORIGIN'] : '';
    if (empty($cfg['allowed_origins'])) {
        header('Access-Control-Allow-Origin: *');
    } elseif ($origin && in_array($origin, $cfg['allowed_origins'], true)) {
        header('Access-Control-Allow-Origin: ' . $origin);
    }
    header('Access-Control-Allow-Headers: Content-Type');
    header('Access-Control-Allow-Methods: POST, OPTIONS');
    header('Content-Type: application/json; charset=utf-8');
    if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(204); exit; }
}

function elite_input() {
    $raw = file_get_contents('php://input');
    $data = json_decode($raw, true);
    if (!is_array($data)) $data = $_POST;
    return is_array($data) ? $data : [];
}

function elite_json($payload, $code = 200) {
    http_response_code($code);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE);
    exit;
}

function elite_fail($message, $code = 400) {
    elite_json(['ok' => false, 'error' => $message], $code);
}

function elite_str($arr, $key, $max = 120) {
    $v = isset($arr[$key]) ? trim((string)$arr[$key]) : '';
    $v = strip_tags($v);
    return mb_substr($v, 0, $max);
}

/**
 * تنظيف رقم الموبايل.
 * مصر (كود 20): يرجّع 01xxxxxxxxx — أي دولة تانية: يرجّع +<كود الدولة><الرقم>
 * يرجّع false لو الرقم مش صحيح.
 */
function elite_phone($value, $dial = '20') {
    $dial = preg_replace('/[^0-9]/', '', (string)$dial);
    if ($dial === '') $dial = '20';
    $p = preg_replace('/[^0-9]/', '', (string)$value);
    if (strpos($p, '00' . $dial) === 0) $p = substr($p, 2 + strlen($dial));

    if ($dial === '20') {
        if (strpos($p, '20') === 0 && strlen($p) > 11) $p = '0' . substr($p, 2);
        if (strlen($p) === 10 && $p[0] === '1') $p = '0' . $p;
        return preg_match('/^01[0125][0-9]{8}$/', $p) ? $p : false;
    }

    if (strpos($p, $dial) === 0 && strlen($p) > 9) $p = substr($p, strlen($dial));
    $p = ltrim($p, '0');
    return preg_match('/^[0-9]{6,14}$/', $p) ? '+' . $dial . $p : false;
}
