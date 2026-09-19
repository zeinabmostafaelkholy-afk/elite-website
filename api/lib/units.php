<?php
/**
 * Elite Real Estate — قراءة وحفظ الوحدات (data/properties.json)
 *
 * كل حفظ بيكتب ملفين مع بعض:
 *   data/properties.json   المصدر الأساسي
 *   data/properties.js     نسخة بيقراها الموقع في المتصفح  (window.ELITE_PROPERTIES)
 * والموقع (صفحة الوحدات، صفحات الكمبوندات، الخريطة، الرئيسية) بيقرا النسخة دي مباشرة،
 * فأي تعديل بيظهر من غير ما تشغّلي أي أمر.
 */
require_once __DIR__ . '/bootstrap.php';

function elite_root() {
    return realpath(__DIR__ . '/../..');
}

function elite_data_file($name) {
    return elite_root() . '/data/' . $name;
}

function elite_unit_types() {
    return array('apartment', 'villa', 'chalet', 'townhouse', 'twinhouse', 'duplex', 'penthouse', 'office', 'retail',
                 'medical', 'studio', 'cabin', 'administrative', 'pharmacy', 'loft', 'unit');
}

function elite_cities() {
    return array('alexandria', 'north-coast', 'cairo', 'giza', 'other');
}

function elite_compounds() {
    $raw = @file_get_contents(elite_data_file('compounds.json'));
    $d = $raw === false ? null : json_decode($raw, true);
    return is_array($d) ? $d : array();
}

/* قفل بسيط عشان اتنين مستخدمين ما يكتبوش في نفس اللحظة */
function elite_locked($fn) {
    $lock = @fopen(elite_data_file('.units.lock'), 'c');
    if ($lock) flock($lock, LOCK_EX);
    try {
        $r = $fn();
    } catch (Exception $e) {
        if ($lock) { flock($lock, LOCK_UN); fclose($lock); }
        throw $e;
    }
    if ($lock) { flock($lock, LOCK_UN); fclose($lock); }
    return $r;
}

function elite_units_read() {
    $raw = @file_get_contents(elite_data_file('properties.json'));
    if ($raw === false) elite_fail('ملف الوحدات مش موجود (data/properties.json)', 500);
    $d = json_decode($raw, true);
    if (!is_array($d)) elite_fail('ملف الوحدات تالف', 500);
    return $d;
}

function elite_write_atomic($path, $content) {
    $tmp = $path . '.tmp' . getmypid();
    if (file_put_contents($tmp, $content) === false) return false;
    @chmod($tmp, 0644);
    return rename($tmp, $path);
}

/* نسخة احتياطية واحدة كل يوم (بنحتفظ بآخر 14 يوم) في data/backups */
function elite_backup_units() {
    $src = elite_data_file('properties.json');
    if (!is_file($src)) return;
    $dir = elite_root() . '/data/backups';
    if (!is_dir($dir)) @mkdir($dir, 0755, true);
    $dst = $dir . '/properties-' . date('Ymd') . '.json';
    if (!file_exists($dst)) {
        @copy($src, $dst);
        $all = glob($dir . '/properties-*.json');
        if ($all && count($all) > 14) {
            sort($all);
            foreach (array_slice($all, 0, count($all) - 14) as $old) @unlink($old);
        }
    }
}

function elite_units_write($units) {
    elite_backup_units();
    $units = array_values($units);
    $flags = JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES;
    $ok1 = elite_write_atomic(elite_data_file('properties.json'), json_encode($units, $flags | JSON_PRETTY_PRINT) . "\n");
    $ok2 = elite_write_atomic(elite_data_file('properties.js'), 'window.ELITE_PROPERTIES = ' . json_encode($units, $flags) . ";\n");
    if (!$ok1 || !$ok2) elite_fail('مقدرتش أكتب ملفات البيانات. اتأكد إن فولدر data قابل للكتابة (صلاحيات 755 أو 775).', 500);
}

/* ---------- تنظيف المدخلات ---------- */
function elite_bi($in, $key, $max) {
    $v = (isset($in[$key]) && is_array($in[$key])) ? $in[$key] : array();
    return array('ar' => elite_str($v, 'ar', $max), 'en' => elite_str($v, 'en', $max));
}

function elite_num($v) {
    if (is_string($v)) $v = str_replace(array(',', ' ', '٬'), '', $v);
    if (!is_numeric($v)) return 0;
    $f = (float)$v;
    if ($f < 0) return 0;
    return floor($f) == $f ? (int)$f : round($f, 2);
}

function elite_image_ref($s) {
    $s = trim((string)$s);
    if ($s === '') return '';
    if (preg_match('#^https?://[^\s"\'<>]{4,600}$#i', $s)) return $s;
    $s = ltrim($s, '/');
    if (strpos($s, '..') !== false) return '';
    if (preg_match('#^assets/img/[A-Za-z0-9_./ %()-]+\.(jpe?g|png|webp)$#i', $s)) return $s;
    return '';
}

function elite_next_id($units) {
    $max = 2000;
    foreach ($units as $u) {
        if (preg_match('/^ELT-(\d+)$/', (string)$u['id'], $m) && (int)$m[1] > $max) $max = (int)$m[1];
    }
    return 'ELT-' . ($max + 1);
}

/**
 * يرجّع الوحدة بعد التنظيف. $existing = الوحدة القديمة (أو null لو جديدة).
 * الحقول اللي مش بتتعدّل من اللوحة (sourceUrl, createdAt, ...) بتفضل زي ما هي.
 */
function elite_unit_clean($in, $existing, $units, &$errors) {
    $errors = array();
    $u = $existing ? $existing : array(
        'id' => '', 'featured' => false, 'recommended' => false, 'purpose' => 'sale', 'type' => 'apartment',
        'city' => 'north-coast', 'project' => null, 'compound' => null, 'priceUnit' => 'total', 'floor' => null,
        'createdAt' => date('Y-m-d'), 'features' => array(), 'plans' => array(),
    );

    $u['title'] = elite_bi($in, 'title', 200);
    if ($u['title']['ar'] === '' && $u['title']['en'] === '') $errors[] = 'اكتب عنوان الوحدة (عربي أو إنجليزي)';
    if ($u['title']['ar'] === '') $u['title']['ar'] = $u['title']['en'];
    if ($u['title']['en'] === '') $u['title']['en'] = $u['title']['ar'];

    $u['location'] = elite_bi($in, 'location', 200);
    if ($u['location']['ar'] === '') $u['location']['ar'] = $u['location']['en'];
    if ($u['location']['en'] === '') $u['location']['en'] = $u['location']['ar'];

    $type = isset($in['type']) ? (string)$in['type'] : $u['type'];
    $u['type'] = in_array($type, elite_unit_types(), true) ? $type : 'apartment';
    $purpose = isset($in['purpose']) ? (string)$in['purpose'] : 'sale';
    $u['purpose'] = $purpose === 'rent' ? 'rent' : 'sale';
    $city = isset($in['city']) ? (string)$in['city'] : $u['city'];
    $u['city'] = in_array($city, elite_cities(), true) ? $city : 'other';

    $comps = elite_compounds();
    $slug = isset($in['compound']) ? (string)$in['compound'] : '';
    if ($slug !== '' && !isset($comps[$slug])) { $errors[] = 'الكمبوند ده مش موجود على الخريطة'; $slug = ''; }
    $u['compound'] = $slug === '' ? null : $slug;
    if ($u['compound'] && isset($comps[$slug]['project']) && $comps[$slug]['project'] !== '') $u['project'] = $comps[$slug]['project'];

    $u['priceOnRequest'] = !empty($in['priceOnRequest']);
    $u['price'] = elite_num(isset($in['price']) ? $in['price'] : 0);
    $u['maxPrice'] = elite_num(isset($in['maxPrice']) ? $in['maxPrice'] : 0) ?: null;
    $pu = isset($in['priceUnit']) ? (string)$in['priceUnit'] : 'total';
    $u['priceUnit'] = $pu === 'monthly' ? 'monthly' : 'total';
    if (!$u['priceOnRequest'] && $u['price'] <= 0) $errors[] = 'اكتب السعر أو فعّل "السعر عند الطلب"';

    $u['area'] = elite_num(isset($in['area']) ? $in['area'] : 0);
    $u['areaMax'] = elite_num(isset($in['areaMax']) ? $in['areaMax'] : 0) ?: null;
    $u['beds'] = (int)elite_num(isset($in['beds']) ? $in['beds'] : 0);
    $u['baths'] = (int)elite_num(isset($in['baths']) ? $in['baths'] : 0);
    $floor = elite_str($in, 'floor', 20);
    $u['floor'] = $floor === '' ? null : $floor;
    $u['finishing'] = elite_bi($in, 'finishing', 80);
    $u['delivery'] = elite_bi($in, 'delivery', 80);
    $u['deliveryDate'] = elite_str($in, 'deliveryDate', 20);
    $sale = isset($in['saleType']) ? (string)$in['saleType'] : '';
    $u['saleType'] = in_array($sale, array('developer', 'resale'), true) ? $sale : '';
    $u['phase'] = elite_str($in, 'phase', 80);
    $u['developer'] = elite_str($in, 'developer', 120);
    $u['description'] = elite_bi($in, 'description', 4000);

    $plans = array();
    if (isset($in['plans']) && is_array($in['plans'])) {
        foreach (array_slice($in['plans'], 0, 6) as $p) {
            if (!is_array($p)) continue;
            $inst = elite_num(isset($p['installment']) ? $p['installment'] : 0);
            if ($inst <= 0) continue;
            $fq = isset($p['frequency']) ? (string)$p['frequency'] : 'monthly';
            if (!in_array($fq, array('monthly', 'quarterly', 'semi-annually', 'annually'), true)) $fq = 'monthly';
            $plans[] = array('installment' => $inst, 'frequency' => $fq,
                             'years' => elite_num(isset($p['years']) ? $p['years'] : 0) ?: null,
                             'down' => elite_num(isset($p['down']) ? $p['down'] : 0) ?: null);
        }
    }
    $u['plans'] = $plans;

    $feat = array();
    if (isset($in['features']) && is_array($in['features'])) {
        foreach ($in['features'] as $f) {
            $f = (string)$f;
            if (preg_match('/^[A-Za-z0-9]{2,30}$/', $f) && !in_array($f, $feat, true)) $feat[] = $f;
        }
    }
    $u['features'] = array_slice($feat, 0, 30);

    $u['featured'] = !empty($in['featured']);
    $u['recommended'] = !empty($in['recommended']);
    $ord = isset($in['order']) ? $in['order'] : null;
    $u['order'] = ($ord === null || $ord === '' || !is_numeric($ord)) ? null : (int)$ord;

    $imgs = array();
    if (isset($in['images']) && is_array($in['images'])) {
        foreach ($in['images'] as $im) {
            $r = elite_image_ref($im);
            if ($r !== '' && !in_array($r, $imgs, true)) $imgs[] = $r;
        }
    }
    $imgs = array_slice($imgs, 0, 30);
    if ($imgs) {
        $u['image'] = $imgs[0];
        $u['gallery'] = $imgs;
    } else {
        $u['image'] = $u['compound'] ? 'assets/img/compounds/' . $u['compound'] . '.jpg' : 'assets/img/brand/fallback.jpg';
        $u['gallery'] = array();
    }

    if (!$existing) {
        $id = isset($in['id']) ? trim((string)$in['id']) : '';
        $taken = false;
        foreach ($units as $x) if ($x['id'] === $id) { $taken = true; break; }
        if ($id === '' || !preg_match('/^[A-Za-z0-9._-]{2,40}$/', $id) || $taken) $id = elite_next_id($units);
        $u['id'] = $id;
        $u['createdAt'] = date('Y-m-d');
        $u['sourceReference'] = 'Admin dashboard';
    }
    if (!isset($u['recommended'])) $u['recommended'] = false;
    return $u;
}

/* ---------- رفع الصور ---------- */
function elite_upload_dir() {
    $d = elite_root() . '/assets/img/properties/uploads';
    if (!is_dir($d)) @mkdir($d, 0755, true);
    return $d;
}

/** يرجّع مسار الصورة النسبي (assets/img/...) أو يوقف بخطأ واضح. */
function elite_handle_upload($file) {
    if (!is_array($file) || !isset($file['error'])) elite_fail('مفيش ملف مرفوع');
    if ($file['error'] === UPLOAD_ERR_INI_SIZE || $file['error'] === UPLOAD_ERR_FORM_SIZE) elite_fail('الصورة أكبر من الحد المسموح على السيرفر');
    if ($file['error'] !== UPLOAD_ERR_OK) elite_fail('فشل رفع الصورة (كود ' . (int)$file['error'] . ')');
    if ($file['size'] > 12 * 1024 * 1024) elite_fail('الصورة أكبر من 12 ميجا');
    $info = @getimagesize($file['tmp_name']);
    if (!$info) elite_fail('الملف ده مش صورة');
    $type = $info[2];
    $WEBP = defined('IMAGETYPE_WEBP') ? IMAGETYPE_WEBP : 18;
    $name = 'u-' . date('ymd-His') . '-' . substr(elite_random_hex(4), 0, 6);
    $dir = elite_upload_dir();
    if (!is_dir($dir) || !is_writable($dir)) elite_fail('فولدر الرفع assets/img/properties/uploads مش قابل للكتابة', 500);

    $canGd = function_exists('imagecreatetruecolor');
    if ($canGd && in_array($type, array(IMAGETYPE_JPEG, IMAGETYPE_PNG, $WEBP), true)) {
        $src = null;
        if ($type === IMAGETYPE_JPEG && function_exists('imagecreatefromjpeg')) $src = @imagecreatefromjpeg($file['tmp_name']);
        if ($type === IMAGETYPE_PNG && function_exists('imagecreatefrompng')) $src = @imagecreatefrompng($file['tmp_name']);
        if ($type === $WEBP && function_exists('imagecreatefromwebp')) $src = @imagecreatefromwebp($file['tmp_name']);
        if ($src) {
            if ($type === IMAGETYPE_JPEG && function_exists('exif_read_data')) {
                $exif = @exif_read_data($file['tmp_name']);
                $o = isset($exif['Orientation']) ? (int)$exif['Orientation'] : 1;
                $angle = ($o === 3) ? 180 : (($o === 6) ? -90 : (($o === 8) ? 90 : 0));
                if ($angle && function_exists('imagerotate')) { $r = imagerotate($src, $angle, 0); if ($r) { imagedestroy($src); $src = $r; } }
            }
            $w = imagesx($src); $h = imagesy($src);
            $max = 2000;
            $scale = min(1, $max / max($w, $h));
            $nw = max(1, (int)round($w * $scale)); $nh = max(1, (int)round($h * $scale));
            $dst = imagecreatetruecolor($nw, $nh);
            imagefill($dst, 0, 0, imagecolorallocate($dst, 255, 255, 255));
            imagecopyresampled($dst, $src, 0, 0, 0, 0, $nw, $nh, $w, $h);
            $out = $dir . '/' . $name . '.jpg';
            $ok = imagejpeg($dst, $out, 82);
            imagedestroy($src); imagedestroy($dst);
            if ($ok) { @chmod($out, 0644); return 'assets/img/properties/uploads/' . $name . '.jpg'; }
        }
    }
    /* من غير GD: نحفظ الصورة زي ما هي (jpg / png / webp بس) */
    $ext = ($type === IMAGETYPE_JPEG) ? 'jpg' : (($type === IMAGETYPE_PNG) ? 'png' : (($type === $WEBP) ? 'webp' : ''));
    if ($ext === '') elite_fail('الصيغة دي مش مدعومة. استخدم JPG أو PNG أو WEBP');
    $out = $dir . '/' . $name . '.' . $ext;
    if (!move_uploaded_file($file['tmp_name'], $out)) elite_fail('مقدرتش أحفظ الصورة', 500);
    @chmod($out, 0644);
    return 'assets/img/properties/uploads/' . $name . '.' . $ext;
}
