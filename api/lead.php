<?php
/**
 * POST /api/lead.php
 * يحفظ بيانات صاحب الطلب مع التقييم، ويبعت إشعار بالبريد لو مفعّل.
 */
require __DIR__ . '/lib/bootstrap.php';
require __DIR__ . '/lib/estimator.php';
require __DIR__ . '/lib/store.php';

elite_cors();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    elite_fail('استخدم POST', 405);
}

$in = elite_input();

$name  = elite_str($in, 'name', 80);
$phone = elite_phone(isset($in['phone']) ? $in['phone'] : '', isset($in['dial']) ? $in['dial'] : '20');
$emailRaw = elite_str($in, 'email', 120);
$email = filter_var($emailRaw, FILTER_VALIDATE_EMAIL);

if ($name === '')  elite_fail('الاسم مطلوب');
if ($phone === false) elite_fail('رقم الموبايل غير صحيح');
if ($emailRaw !== '' && !$email) elite_fail('البريد الإلكتروني غير صحيح');
/* فورم التقييم (نفس فورم عقارماب) البريد فيه إجباري */
if (elite_str($in, 'source', 30) === 'valuation-form' && !$email) elite_fail('البريد الإلكتروني مطلوب');

/* حماية بسيطة من التكرار: نفس الرقم أكتر من 5 مرات في الدقيقة */
$stamp = sys_get_temp_dir() . '/elite_val_' . md5($phone);
if (file_exists($stamp) && (time() - filemtime($stamp)) < 10) {
    elite_fail('تم استلام طلبك بالفعل، استنى شوية قبل المحاولة تاني', 429);
}
@touch($stamp);

$result = elite_estimate($in);

$row = [
    'created_at' => date('Y-m-d H:i:s'),
    'name'   => $name,
    'phone'  => $phone,
    'email'  => $email ?: '',
    'lang'   => elite_str($in, 'lang', 4),
    'intent' => elite_str($in, 'intent', 20),
    'region' => elite_str($in, 'region', 40),
    'zone'   => elite_str($in, 'zone', 40),
    'type'   => elite_str($in, 'type', 20),
    'area'   => (float) (isset($in['area']) ? $in['area'] : 0),
    'beds'   => elite_str($in, 'beds', 3),
    'baths'  => elite_str($in, 'baths', 3),
    'finish' => elite_str($in, 'finish', 20),
    'floor'  => elite_str($in, 'floor', 20),
    'age'    => elite_str($in, 'age', 20),
    'features' => isset($in['features']) && is_array($in['features']) ? implode('|', array_map('strval', $in['features'])) : '',
    'legal'  => elite_str($in, 'legal', 20),
    'payment'=> elite_str($in, 'payment', 20),
    'estimated_value' => $result ? $result['value'] : '',
    'per_sqm'         => $result ? $result['perSqm'] : '',
    'ip'     => isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '',
];

$saved = elite_store_lead($row);
elite_notify($row);

elite_json([
    'ok' => (bool) $saved,
    'saved' => (bool) $saved,
    'result' => $result,
]);
