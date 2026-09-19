<?php
/**
 * أداة صغيرة: بعد ما تعدّل data/valuation-data.json شغّل الأمر ده
 * من التيرمنال:  php tools/build-js.php
 * عشان يتولّد ملف assets/js/valuation-data.js من جديد.
 */
$json = __DIR__ . '/../data/valuation-data.json';
$out  = __DIR__ . '/../assets/js/valuation-data.js';

$raw = file_get_contents($json);
if ($raw === false) { fwrite(STDERR, "لم يتم العثور على $json\n"); exit(1); }

$data = json_decode($raw, true);
if (!is_array($data)) { fwrite(STDERR, "ملف JSON غير صالح\n"); exit(1); }

$pretty = json_encode($data, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
$js  = "/* Elite Real Estate — بيانات أداة التقييم (مولّدة من data/valuation-data.json)\n";
$js .= "   لتعديل الأسعار: عدّل ملف JSON ثم شغّل tools/build-js.php */\n";
$js .= "window.ELITE_VALUATION_DATA = " . $pretty . ";\n";

file_put_contents($out, $js);
echo "تم توليد assets/js/valuation-data.js بنجاح\n";
