<?php
/**
 * Elite Real Estate — طلبات التقييم
 * ادخل على: https://yoursite.com/admin/leads.php  (بنفس مستخدم لوحة التحكم)
 */
require __DIR__ . '/../api/lib/auth.php';
require __DIR__ . '/../api/lib/store.php';

$cfg = elite_config();
$me = elite_current_user();
if (!$me) { header('Location: index.php'); exit; }
$authed = true;

/* ---------- قراءة الطلبات ---------- */
function elite_read_leads() {
    $cfg = elite_config();
    $rows = [];
    if ($cfg['storage'] === 'mysql') {
        try {
            $pdo = elite_pdo();
            $rows = $pdo->query('SELECT * FROM `' . $cfg['db']['table'] . '` ORDER BY id DESC LIMIT 1000')->fetchAll();
            return $rows;
        } catch (Exception $e) { /* نكمل على CSV */ }
    }
    $file = $cfg['csv_file'];
    if (!file_exists($file)) return [];
    $fh = fopen($file, 'r');
    $head = fgetcsv($fh);
    if ($head && isset($head[0])) $head[0] = preg_replace('/^\xEF\xBB\xBF/', '', $head[0]);
    while (($line = fgetcsv($fh)) !== false) {
        if (count($line) === count($head)) $rows[] = array_combine($head, $line);
    }
    fclose($fh);
    return array_reverse($rows);
}

/* ---------- تصدير CSV ---------- */
if ($authed && isset($_GET['export'])) {
    $rows = elite_read_leads();
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="elite-valuation-leads-' . date('Y-m-d') . '.csv"');
    $out = fopen('php://output', 'w');
    fwrite($out, "\xEF\xBB\xBF");
    fputcsv($out, elite_lead_columns());
    foreach ($rows as $r) {
        $line = [];
        foreach (elite_lead_columns() as $c) $line[] = isset($r[$c]) ? $r[$c] : '';
        fputcsv($out, $line);
    }
    exit;
}

$rows = $authed ? elite_read_leads() : [];
$q = isset($_GET['q']) ? trim($_GET['q']) : '';
if ($q !== '') {
    $rows = array_values(array_filter($rows, function ($r) use ($q) {
        return mb_stripos(implode(' ', array_map('strval', $r)), $q) !== false;
    }));
}
$D = elite_dataset();
function elite_label($list, $id) {
    foreach ($list as $i) if ($i['id'] === $id) return $i['ar'];
    return $id;
}
function elite_zone_label($D, $regionId, $zoneId) {
    foreach ($D['regions'] as $r) {
        if ($r['id'] !== $regionId) continue;
        foreach ($r['zones'] as $z) if ($z['id'] === $zoneId) return $z['ar'] . ' - ' . $r['ar'];
        return $r['ar'];
    }
    return $zoneId;
}
$e = function ($v) { return htmlspecialchars((string)$v, ENT_QUOTES, 'UTF-8'); };
?>
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>طلبات التقييم | <?= $e($cfg['company_name_ar']) ?></title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=El+Messiri:wght@400;600&family=Tajawal:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  :root { --navy:#08192a; --brass:#b0894f; --cream:#f4f2ed; --line:#e0dbd2; --muted:#6d7b87; }
  * { box-sizing: border-box; }
  body { margin:0; font-family:"Tajawal",Arial,sans-serif; background:var(--cream); color:#16232e; font-size:15px; }
  header { background:var(--navy); color:#fff; padding:18px 24px; display:flex; justify-content:space-between; align-items:center; gap:16px; flex-wrap:wrap; }
  header h1 { font-family:"El Messiri",serif; font-size:20px; margin:0; font-weight:600; }
  header a { color:rgba(255,255,255,.75); text-decoration:none; font-size:14px; }
  header a:hover { color:#fff; }
  .wrap { max-width:1240px; margin:0 auto; padding:26px 24px 60px; }
  .bar { display:flex; gap:12px; flex-wrap:wrap; align-items:center; margin-bottom:18px; }
  .bar input { padding:11px 14px; border:1px solid var(--line); background:#fff; font-family:inherit; min-width:240px; }
  .btn { display:inline-block; padding:11px 18px; background:var(--navy); color:#fff; text-decoration:none; border:0; font-family:inherit; cursor:pointer; font-size:14px; }
  .btn--brass { background:var(--brass); }
  .count { color:var(--muted); font-size:14px; }
  table { width:100%; border-collapse:collapse; background:#fff; border:1px solid var(--line); font-size:14px; }
  th, td { padding:11px 12px; text-align:right; border-bottom:1px solid var(--line); white-space:nowrap; }
  th { background:#fbfaf7; font-weight:500; color:var(--muted); font-size:13px; }
  tr:hover td { background:#fbfaf7; }
  td.money { font-weight:500; color:var(--navy); }
  .tag { display:inline-block; padding:3px 9px; border-radius:999px; background:rgba(176,137,79,.14); color:#7a5c30; font-size:12px; }
  .scroll { overflow-x:auto; }
  .login { max-width:360px; margin:12vh auto; background:#fff; border:1px solid var(--line); padding:32px; }
  .login h2 { font-family:"El Messiri",serif; margin:0 0 18px; font-weight:600; }
  .login input { width:100%; padding:12px 14px; border:1px solid var(--line); margin-bottom:12px; font-family:inherit; }
  .err { color:#b3261e; font-size:14px; margin-bottom:12px; }
  .empty { background:#fff; border:1px solid var(--line); padding:40px; text-align:center; color:var(--muted); }
</style>
</head>
<body>


  <header>
    <h1><?= $e($cfg['company_name_ar']) ?> — طلبات التقييم</h1>
    <span><a href="index.php">لوحة الوحدات</a> &nbsp;·&nbsp; <?= $e($me['name']) ?></span>
  </header>

  <div class="wrap">
    <form class="bar" method="get">
      <input name="q" value="<?= $e($q) ?>" placeholder="ابحث بالاسم أو الرقم أو المنطقة">
      <button class="btn">بحث</button>
      <a class="btn btn--brass" href="?export=1">تحميل CSV</a>
      <span class="count"><?= count($rows) ?> طلب</span>
    </form>

    <?php if (!$rows): ?>
      <div class="empty">لا توجد طلبات حتى الآن.</div>
    <?php else: ?>
      <div class="scroll">
      <table>
        <thead><tr>
          <th>التاريخ</th><th>الاسم</th><th>الموبايل</th><th>البريد</th>
          <th>الهدف</th><th>المنطقة</th><th>النوع</th><th>المساحة</th>
          <th>التشطيب</th><th>التقييم</th><th>سعر المتر</th>
        </tr></thead>
        <tbody>
        <?php foreach ($rows as $r): ?>
          <tr>
            <td><?= $e(substr((string)($r['created_at'] ?? ''), 0, 16)) ?></td>
            <td><?= $e($r['name'] ?? '') ?></td>
            <?php $ph = (string)($r['phone'] ?? ''); $intl = $ph === '' ? '' : ($ph[0] === '+' ? substr($ph, 1) : '20' . ltrim($ph, '0')); ?>
            <td dir="ltr"><a href="https://wa.me/<?= $e($intl) ?>" target="_blank" rel="noopener"><?= $e($ph) ?></a></td>
            <td dir="ltr"><?= $e($r['email'] ?? '') ?></td>
            <td><span class="tag"><?= $e(elite_label($D['intents'], $r['intent'] ?? '')) ?></span></td>
            <td><?= $e(elite_zone_label($D, $r['region'] ?? '', $r['zone'] ?? '')) ?></td>
            <td><?= $e(elite_label($D['types'], $r['type'] ?? '')) ?></td>
            <td><?= $e($r['area'] ?? '') ?> م²</td>
            <td><?= $e(elite_label($D['finishes'], $r['finish'] ?? '')) ?></td>
            <td class="money"><?= $r['estimated_value'] !== '' ? number_format((float)$r['estimated_value']) : '—' ?></td>
            <td><?= $r['per_sqm'] !== '' ? number_format((float)$r['per_sqm']) : '—' ?></td>
          </tr>
        <?php endforeach; ?>
        </tbody>
      </table>
      </div>
    <?php endif; ?>
  </div>

</body>
</html>
