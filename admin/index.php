<?php
/**
 * Elite Real Estate — لوحة التحكم
 * ادخل على: https://yoursite.com/admin/
 * الصفحة نفسها ثابتة؛ كل الشغل بيتم من admin/assets/admin.js عن طريق admin/api.php
 */
header('Content-Type: text/html; charset=utf-8');
header('Cache-Control: no-store');
header('X-Robots-Tag: noindex, nofollow');
header('X-Frame-Options: SAMEORIGIN');
header('X-Content-Type-Options: nosniff');
header('Referrer-Policy: same-origin');
readfile(__DIR__ . '/app.html');
