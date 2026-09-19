<?php
/**
 * فحص جاهزية السيرفر للوحة التحكم — افتحيه بعد رفع الموقع:  /admin/check.php
 * (بيطلب تسجيل دخول لوحة التحكم)
 */
require __DIR__ . '/../api/lib/auth.php';
require __DIR__ . '/../api/lib/units.php';
header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: no-store');
header('X-Robots-Tag: noindex, nofollow');
$me = elite_current_user();
if (!$me || $me['role'] !== 'admin') { http_response_code(403); echo '<meta charset="utf-8"><p dir="rtl">سجّلي دخول كمدير من <a href="index.php">لوحة التحكم</a> الأول.</p>'; exit; }

$root = elite_root();
$rows = array();
function chk(&$rows, $label, $ok, $hint) { $rows[] = array($label, $ok, $hint); }

chk($rows, 'إصدار PHP ' . PHP_VERSION, version_compare(PHP_VERSION, '7.0.0', '>='), 'محتاج PHP 7.0 أو أحدث');
chk($rows, 'إضافة mbstring', function_exists('mb_substr'), 'فعّليها من إعدادات الاستضافة');
chk($rows, 'إضافة json', function_exists('json_encode'), 'مطلوبة');
chk($rows, 'إضافة GD (تصغير الصور المرفوعة)', function_exists('imagecreatetruecolor'), 'اختيارية: من غيرها الصور بتتحفظ بحجمها الأصلي');
chk($rows, 'data/properties.json موجود', is_file($root . '/data/properties.json'), 'ارفعي فولدر data كامل');
chk($rows, 'data/properties.json قابل للكتابة', is_writable($root . '/data/properties.json'), 'اجعلي الصلاحية 664 أو 666');
chk($rows, 'data/properties.js قابل للكتابة', is_writable($root . '/data/properties.js'), 'اجعلي الصلاحية 664 أو 666');
chk($rows, 'فولدر data قابل للكتابة', is_writable($root . '/data'), 'اجعلي الصلاحية 775 (بيتكتب فيه ملف مؤقت وقت الحفظ)');
chk($rows, 'data/compounds.json موجود', is_file($root . '/data/compounds.json'), 'اتولّد من python3 build.py');
chk($rows, 'فولدر رفع الصور قابل للكتابة', is_writable(elite_upload_dir()), 'assets/img/properties/uploads لازم يكون 775');
chk($rows, 'فولدر api/storage قابل للكتابة (المستخدمين)', is_writable(elite_storage_dir()), 'api/storage لازم يكون 775');
$mb = function ($v) { $n = (int)$v; $u = strtoupper(substr(trim($v), -1)); return $u === 'G' ? $n * 1024 : ($u === 'M' ? $n : ($u === 'K' ? $n / 1024 : $n / 1048576)); };
chk($rows, 'حد رفع الصورة upload_max_filesize = ' . ini_get('upload_max_filesize'), $mb(ini_get('upload_max_filesize')) >= 8, 'يفضل 8M أو أكتر');
chk($rows, 'post_max_size = ' . ini_get('post_max_size'), $mb(ini_get('post_max_size')) >= 8, 'يفضل 8M أو أكتر');
?>
<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="robots" content="noindex">
<title>فحص السيرفر</title>
<style>body{font:15px/1.6 Tahoma,Arial,sans-serif;background:#f4f2ed;color:#16232e;max-width:760px;margin:30px auto;padding:0 16px}
table{width:100%;border-collapse:collapse;background:#fff;border:1px solid #e0dbd2}td{padding:10px 12px;border-bottom:1px solid #e0dbd2}
.ok{color:#1f7a4d;font-weight:700}.no{color:#b3261e;font-weight:700}small{color:#6d7b87}</style></head><body>
<h1>فحص جاهزية لوحة التحكم</h1>
<table>
<?php foreach ($rows as $r): ?>
<tr><td><?= htmlspecialchars($r[0]) ?></td><td class="<?= $r[1] ? 'ok' : 'no' ?>"><?= $r[1] ? '✓ تمام' : '✗ محتاج تعديل' ?></td><td><small><?= $r[1] ? '' : htmlspecialchars($r[2]) ?></small></td></tr>
<?php endforeach; ?>
</table>
<p><a href="index.php">← لوحة التحكم</a></p>
</body></html>
