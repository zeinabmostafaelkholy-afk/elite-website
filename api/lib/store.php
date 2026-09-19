<?php
/**
 * Elite Real Estate — تخزين طلبات التقييم
 * CSV افتراضياً، وMySQL لو حبيت.
 */

function elite_lead_columns() {
    return ['created_at','name','phone','email','lang','intent','region','zone','type',
            'area','beds','baths','finish','floor','age','features','legal','payment',
            'estimated_value','per_sqm','ip'];
}

function elite_store_lead(array $row) {
    $cfg = elite_config();
    return $cfg['storage'] === 'mysql' ? elite_store_mysql($row, $cfg) : elite_store_csv($row, $cfg);
}

/* ---------- CSV ---------- */
function elite_store_csv(array $row, array $cfg) {
    $file = $cfg['csv_file'];
    $dir  = dirname($file);
    if (!is_dir($dir)) @mkdir($dir, 0755, true);

    $new = !file_exists($file);
    $fh = @fopen($file, 'a');
    if (!$fh) return false;

    if (flock($fh, LOCK_EX)) {
        if ($new) {
            fwrite($fh, "\xEF\xBB\xBF");           // BOM ليفتح عربي صح في Excel
            fputcsv($fh, elite_lead_columns());
        }
        $ordered = [];
        foreach (elite_lead_columns() as $c) $ordered[] = isset($row[$c]) ? $row[$c] : '';
        fputcsv($fh, $ordered);
        flock($fh, LOCK_UN);
    }
    fclose($fh);
    return true;
}

/* ---------- MySQL ---------- */
function elite_pdo() {
    static $pdo = null;
    if ($pdo === null) {
        $db = elite_config()['db'];
        $dsn = "mysql:host={$db['host']};dbname={$db['name']};charset=utf8mb4";
        $pdo = new PDO($dsn, $db['user'], $db['pass'], [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        ]);
    }
    return $pdo;
}

function elite_store_mysql(array $row, array $cfg) {
    try {
        $pdo = elite_pdo();
        $table = $cfg['db']['table'];
        $cols = elite_lead_columns();
        $sql = 'INSERT INTO `' . $table . '` (`' . implode('`,`', $cols) . '`) VALUES (:' . implode(',:', $cols) . ')';
        $st = $pdo->prepare($sql);
        foreach ($cols as $c) $st->bindValue(':' . $c, isset($row[$c]) ? $row[$c] : null);
        $st->execute();
        return true;
    } catch (Exception $e) {
        // fallback على CSV عشان ما نضيّعش أي طلب
        return elite_store_csv($row, $cfg);
    }
}

/* ---------- إشعار بالبريد ---------- */
function elite_notify(array $row) {
    $cfg = elite_config();
    if (empty($cfg['send_email'])) return false;

    $to = $cfg['notify_email'];
    $subject = '=?UTF-8?B?' . base64_encode('طلب تقييم عقاري جديد — ' . $row['name']) . '?=';

    $lines = [];
    foreach (elite_lead_columns() as $c) {
        if ($c === 'ip') continue;
        $lines[] = $c . ': ' . (isset($row[$c]) ? $row[$c] : '');
    }
    $body = implode("\n", $lines);

    $headers  = "MIME-Version: 1.0\r\n";
    $headers .= "Content-Type: text/plain; charset=UTF-8\r\n";
    $headers .= 'From: ' . $cfg['notify_email'] . "\r\n";
    if (!empty($row['email'])) $headers .= 'Reply-To: ' . $row['email'] . "\r\n";

    return @mail($to, $subject, $body, $headers);
}
