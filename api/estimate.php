<?php
/**
 * POST /api/estimate.php
 * يستقبل بيانات الوحدة ويرجّع التقييم — من غير ما يحفظ أي بيانات شخصية.
 */
require __DIR__ . '/lib/bootstrap.php';
require __DIR__ . '/lib/estimator.php';

elite_cors();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    elite_fail('استخدم POST', 405);
}

$in = elite_input();
$result = elite_estimate($in);

if (!$result) {
    elite_fail('بيانات ناقصة أو غير صحيحة: تأكد من المنطقة والحي والمساحة');
}

elite_json(['ok' => true, 'result' => $result]);
