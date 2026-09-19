<?php
/**
 * Elite Real Estate — لوحة التحكم: المستخدمين والجلسات وحماية CSRF
 *
 * المستخدمين متخزّنين في api/storage/users.php (الباسوردات مشفّرة بـ password_hash).
 * أول مرة بتتفتح فيها اللوحة بيتعمل مستخدم واحد من admin_user / admin_pass في api/config.php
 * وبيتطلب منه يغيّر الباسورد.
 */
require_once __DIR__ . '/bootstrap.php';

define('ELITE_USERS_GUARD', "<?php http_response_code(404); exit; ?>\n");
define('ELITE_DEFAULT_PASS', 'ChangeMe2026!');

function elite_storage_dir() {
    $d = __DIR__ . '/../storage';
    if (!is_dir($d)) @mkdir($d, 0755, true);
    return $d;
}

function elite_users_file() {
    return elite_storage_dir() . '/users.php';
}

function elite_users_write($users) {
    $f = elite_users_file();
    $json = json_encode(array_values($users), JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    $tmp = $f . '.tmp' . getmypid();
    if (file_put_contents($tmp, ELITE_USERS_GUARD . $json, LOCK_EX) === false) return false;
    @chmod($tmp, 0640);
    return @rename($tmp, $f);
}

function elite_users_seed() {
    $cfg = elite_config();
    $pass = isset($cfg['admin_pass']) ? (string)$cfg['admin_pass'] : ELITE_DEFAULT_PASS;
    $users = array(array(
        'username'   => isset($cfg['admin_user']) ? (string)$cfg['admin_user'] : 'elite',
        'name'       => 'المدير',
        'role'       => 'admin',
        'hash'       => password_hash($pass, PASSWORD_DEFAULT),
        'mustChange' => ($pass === ELITE_DEFAULT_PASS),
        'createdAt'  => date('Y-m-d H:i:s'),
        'lastLogin'  => null,
    ));
    elite_users_write($users);
    return $users;
}

function elite_users_read() {
    $f = elite_users_file();
    if (!file_exists($f)) return elite_users_seed();
    $raw = @file_get_contents($f);
    if ($raw === false) return array();
    $d = json_decode(substr($raw, strlen(ELITE_USERS_GUARD)), true);
    return is_array($d) ? $d : array();
}

function elite_public_user($u) {
    return array(
        'username'   => $u['username'],
        'name'       => isset($u['name']) ? $u['name'] : $u['username'],
        'role'       => isset($u['role']) ? $u['role'] : 'editor',
        'mustChange' => !empty($u['mustChange']),
        'createdAt'  => isset($u['createdAt']) ? $u['createdAt'] : '',
        'lastLogin'  => isset($u['lastLogin']) ? $u['lastLogin'] : null,
    );
}

/* ---------- الجلسة ---------- */
function elite_session() {
    if (session_status() === PHP_SESSION_ACTIVE) return;
    $secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
    @ini_set('session.cookie_httponly', '1');
    @ini_set('session.cookie_samesite', 'Lax');
    @ini_set('session.use_strict_mode', '1');
    if ($secure) @ini_set('session.cookie_secure', '1');
    session_name('elite_admin');
    session_start();
    if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = elite_random_hex(16);
}

function elite_random_hex($bytes) {
    if (function_exists('random_bytes')) return bin2hex(random_bytes($bytes));
    if (function_exists('openssl_random_pseudo_bytes')) return bin2hex(openssl_random_pseudo_bytes($bytes));
    return md5(uniqid((string)mt_rand(), true));
}

function elite_csrf_token() {
    elite_session();
    return $_SESSION['csrf'];
}

function elite_check_csrf() {
    elite_session();
    $sent = isset($_SERVER['HTTP_X_CSRF_TOKEN']) ? (string)$_SERVER['HTTP_X_CSRF_TOKEN'] : '';
    if ($sent === '' || !hash_equals((string)$_SESSION['csrf'], $sent)) {
        elite_fail('انتهت الجلسة، حدّث الصفحة وحاول تاني', 419);
    }
}

function elite_current_user() {
    elite_session();
    if (empty($_SESSION['user'])) return null;
    foreach (elite_users_read() as $u) {
        if (strcasecmp($u['username'], $_SESSION['user']) === 0) return $u;
    }
    unset($_SESSION['user']);
    return null;
}

function elite_require_user($role = null) {
    $u = elite_current_user();
    if (!$u) elite_fail('لازم تسجّل دخول', 401);
    if ($role === 'admin' && (!isset($u['role']) || $u['role'] !== 'admin')) elite_fail('الصلاحية دي للمدير فقط', 403);
    return $u;
}

/* ---------- الدخول (مع حد لمحاولات الباسورد الغلط) ---------- */
function elite_throttle_file() {
    $ip = isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : 'x';
    return sys_get_temp_dir() . '/elite_login_' . md5($ip);
}

function elite_throttle_blocked() {
    $f = elite_throttle_file();
    if (!file_exists($f)) return false;
    $d = json_decode((string)@file_get_contents($f), true);
    if (!is_array($d)) return false;
    $recent = array();
    foreach ($d as $t) if ($t > time() - 900) $recent[] = $t;
    return count($recent) >= 8;
}

function elite_throttle_hit() {
    $f = elite_throttle_file();
    $d = file_exists($f) ? json_decode((string)@file_get_contents($f), true) : array();
    if (!is_array($d)) $d = array();
    $d[] = time();
    @file_put_contents($f, json_encode(array_slice($d, -20)), LOCK_EX);
}

function elite_login($username, $password) {
    elite_session();
    if (elite_throttle_blocked()) elite_fail('محاولات كتير غلط، جرّب بعد 15 دقيقة', 429);
    $users = elite_users_read();
    foreach ($users as $i => $u) {
        if (strcasecmp($u['username'], $username) === 0 && password_verify($password, $u['hash'])) {
            session_regenerate_id(true);
            $_SESSION['user'] = $u['username'];
            if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = elite_random_hex(16);
            $users[$i]['lastLogin'] = date('Y-m-d H:i:s');
            elite_users_write($users);
            @unlink(elite_throttle_file());
            return $users[$i];
        }
    }
    elite_throttle_hit();
    usleep(400000);
    return null;
}

/* ---------- إدارة المستخدمين ---------- */
function elite_valid_username($s) {
    return (bool)preg_match('/^[A-Za-z0-9._-]{3,30}$/', $s);
}

function elite_count_admins($users, $except = null) {
    $n = 0;
    foreach ($users as $u) {
        if ($except !== null && strcasecmp($u['username'], $except) === 0) continue;
        if (isset($u['role']) && $u['role'] === 'admin') $n++;
    }
    return $n;
}
