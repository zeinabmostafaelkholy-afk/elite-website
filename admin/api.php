<?php
/**
 * Elite Real Estate — API لوحة التحكم  (admin/api.php?a=...)
 * الواجهة (admin/assets/admin.js) هي الوحيدة اللي بتكلّمه.
 */
require __DIR__ . '/../api/lib/auth.php';
require __DIR__ . '/../api/lib/units.php';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
header('X-Robots-Tag: noindex');

set_exception_handler(function ($e) {
    elite_json(array('ok' => false, 'error' => 'حصل خطأ غير متوقع في السيرفر'), 500);
});

elite_session();
$a = isset($_GET['a']) ? (string)$_GET['a'] : '';
$isPost = $_SERVER['REQUEST_METHOD'] === 'POST';

/* ---------- بدون تسجيل دخول ---------- */
if ($a === 'session') {
    $u = elite_current_user();
    elite_json(array('ok' => true, 'user' => $u ? elite_public_user($u) : null, 'csrf' => elite_csrf_token()));
}

if (!$isPost) {
    /* ---------- قراءة ---------- */
    $me = elite_require_user();
    if ($a === 'bootstrap') {
        elite_json(array('ok' => true, 'user' => elite_public_user($me), 'units' => elite_units_read(),
                         'compounds' => elite_compounds()));
    }
    if ($a === 'users') {
        elite_require_user('admin');
        $out = array();
        foreach (elite_users_read() as $u) $out[] = elite_public_user($u);
        elite_json(array('ok' => true, 'users' => $out));
    }
    elite_fail('طلب غير معروف', 404);
}

/* ---------- كتابة: كلها محمية بـ CSRF ---------- */
elite_check_csrf();
$in = elite_input();

if ($a === 'login') {
    $u = elite_login(elite_str($in, 'username', 60), isset($in['password']) ? (string)$in['password'] : '');
    if (!$u) elite_fail('اسم المستخدم أو الباسورد غلط', 401);
    elite_json(array('ok' => true, 'user' => elite_public_user($u), 'csrf' => elite_csrf_token()));
}
if ($a === 'logout') {
    $_SESSION = array();
    session_destroy();
    elite_json(array('ok' => true));
}

$me = elite_require_user();

if ($a === 'password') {
    $cur = isset($in['current']) ? (string)$in['current'] : '';
    $next = isset($in['next']) ? (string)$in['next'] : '';
    if (strlen($next) < 8) elite_fail('الباسورد الجديد لازم يكون 8 حروف على الأقل');
    if ($next === ELITE_DEFAULT_PASS) elite_fail('اختار باسورد غير الافتراضي');
    $users = elite_users_read();
    foreach ($users as $i => $u) {
        if (strcasecmp($u['username'], $me['username']) !== 0) continue;
        if (!password_verify($cur, $u['hash'])) elite_fail('الباسورد الحالي غلط');
        $users[$i]['hash'] = password_hash($next, PASSWORD_DEFAULT);
        $users[$i]['mustChange'] = false;
        elite_users_write($users);
        elite_json(array('ok' => true, 'user' => elite_public_user($users[$i])));
    }
    elite_fail('المستخدم مش موجود', 404);
}

/* ---------- المستخدمين (للمدير فقط) ---------- */
if ($a === 'user_save' || $a === 'user_delete') {
    elite_require_user('admin');
    $users = elite_users_read();
    $name = elite_str($in, 'username', 30);

    if ($a === 'user_delete') {
        if (strcasecmp($name, $me['username']) === 0) elite_fail('مينفعش تمسحي حسابك وإنتِ داخلة بيه');
        $found = false;
        foreach ($users as $i => $u) {
            if (strcasecmp($u['username'], $name) !== 0) continue;
            if ($u['role'] === 'admin' && elite_count_admins($users, $name) < 1) elite_fail('لازم يفضل مدير واحد على الأقل');
            unset($users[$i]);
            $found = true;
        }
        if (!$found) elite_fail('المستخدم مش موجود', 404);
        elite_users_write($users);
        elite_json(array('ok' => true));
    }

    $isNew = !empty($in['isNew']);
    $role = (isset($in['role']) && $in['role'] === 'admin') ? 'admin' : 'editor';
    $display = elite_str($in, 'name', 60);
    $pass = isset($in['password']) ? (string)$in['password'] : '';
    if (!elite_valid_username($name)) elite_fail('اسم المستخدم 3-30 حرف إنجليزي أو أرقام (يقبل . _ -)');
    if ($pass !== '' && strlen($pass) < 8) elite_fail('الباسورد لازم يكون 8 حروف على الأقل');

    $idx = null;
    foreach ($users as $i => $u) if (strcasecmp($u['username'], $name) === 0) $idx = $i;

    if ($isNew) {
        if ($idx !== null) elite_fail('اسم المستخدم ده موجود بالفعل');
        if ($pass === '') elite_fail('اكتب باسورد للمستخدم الجديد');
        $users[] = array('username' => $name, 'name' => $display !== '' ? $display : $name, 'role' => $role,
                         'hash' => password_hash($pass, PASSWORD_DEFAULT), 'mustChange' => true,
                         'createdAt' => date('Y-m-d H:i:s'), 'lastLogin' => null);
    } else {
        if ($idx === null) elite_fail('المستخدم مش موجود', 404);
        if ($users[$idx]['role'] === 'admin' && $role !== 'admin' && elite_count_admins($users, $name) < 1) {
            elite_fail('لازم يفضل مدير واحد على الأقل');
        }
        $users[$idx]['name'] = $display !== '' ? $display : $name;
        $users[$idx]['role'] = $role;
        if ($pass !== '') { $users[$idx]['hash'] = password_hash($pass, PASSWORD_DEFAULT); $users[$idx]['mustChange'] = true; }
    }
    if (!elite_users_write($users)) elite_fail('مقدرتش أحفظ المستخدمين. اتأكد إن فولدر api/storage قابل للكتابة', 500);
    $out = array();
    foreach ($users as $u) $out[] = elite_public_user($u);
    elite_json(array('ok' => true, 'users' => $out));
}

/* ---------- الوحدات ---------- */
if ($a === 'unit_save') {
    $raw = isset($in['unit']) && is_array($in['unit']) ? $in['unit'] : array();
    $result = elite_locked(function () use ($raw) {
        $units = elite_units_read();
        $idx = null;
        $id = isset($raw['id']) ? (string)$raw['id'] : '';
        if (!empty($raw['_existing']) && $id !== '') {
            foreach ($units as $i => $x) if ((string)$x['id'] === $id) $idx = $i;
            if ($idx === null) elite_fail('الوحدة دي اتمسحت', 404);
        }
        $errors = array();
        $u = elite_unit_clean($raw, $idx === null ? null : $units[$idx], $units, $errors);
        if ($errors) elite_json(array('ok' => false, 'error' => implode(' — ', $errors), 'errors' => $errors), 422);
        if ($idx === null) $units[] = $u; else $units[$idx] = $u;
        elite_units_write($units);
        return $u;
    });
    elite_json(array('ok' => true, 'unit' => $result));
}

if ($a === 'unit_delete') {
    $id = isset($in['id']) ? (string)$in['id'] : '';
    elite_locked(function () use ($id) {
        $units = elite_units_read();
        $keep = array();
        foreach ($units as $x) if ((string)$x['id'] !== $id) $keep[] = $x;
        if (count($keep) === count($units)) elite_fail('الوحدة مش موجودة', 404);
        elite_units_write($keep);
    });
    elite_json(array('ok' => true));
}

if ($a === 'unit_patch') {
    /* تعديل سريع من الجدول: مميزة / ترتيب / مقترحة */
    $id = isset($in['id']) ? (string)$in['id'] : '';
    $patch = isset($in['patch']) && is_array($in['patch']) ? $in['patch'] : array();
    $result = elite_locked(function () use ($id, $patch) {
        $units = elite_units_read();
        foreach ($units as $i => $x) {
            if ((string)$x['id'] !== $id) continue;
            if (array_key_exists('featured', $patch)) $units[$i]['featured'] = !empty($patch['featured']);
            if (array_key_exists('recommended', $patch)) $units[$i]['recommended'] = !empty($patch['recommended']);
            if (array_key_exists('order', $patch)) {
                $o = $patch['order'];
                $units[$i]['order'] = ($o === null || $o === '' || !is_numeric($o)) ? null : (int)$o;
            }
            elite_units_write($units);
            return $units[$i];
        }
        elite_fail('الوحدة مش موجودة', 404);
    });
    elite_json(array('ok' => true, 'unit' => $result));
}

if ($a === 'upload') {
    if (!isset($_FILES['file'])) elite_fail('مفيش ملف مرفوع');
    elite_json(array('ok' => true, 'url' => elite_handle_upload($_FILES['file'])));
}

elite_fail('طلب غير معروف', 404);
