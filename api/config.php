<?php
/**
 * Elite Real Estate — إعدادات أداة التقييم
 * غيّر القيم هنا فقط.
 */

return [

    /* الشركة */
    'company_name'  => 'Elite Real Estate',
    'company_name_ar' => 'إيليت للتسويق العقاري',
    'site_url'      => 'https://www.eliterealestateco.com',

    /* استقبال طلبات التقييم */
    'notify_email'  => 'info@eliterealestateco.com',
    'send_email'    => false,   // خليها true لو السيرفر بيدعم دالة mail()
    'whatsapp'      => '201111788812',

    /* تخزين الطلبات: 'csv' (بدون قاعدة بيانات) أو 'mysql' */
    'storage'       => 'csv',
    'csv_file'      => __DIR__ . '/storage/leads.csv',

    /* بيانات MySQL — تُستخدم فقط لو storage = mysql */
    'db' => [
        'host' => 'localhost',
        'name' => 'elite_valuation',
        'user' => 'root',
        'pass' => '',
        'table' => 'valuation_leads',
    ],

    /* لوحة التحكم /admin — القيم دي بتتستخدم مرة واحدة بس لعمل أول مستخدم، وبعدها المستخدمين بيتدارو من اللوحة نفسها */
    'admin_user'    => 'elite',
    'admin_pass'    => 'ChangeMe2026!',   // غيّرها فوراً بعد الرفع

    /* النطاقات المسموح لها بمناداة الـ API (اتركها فارغة للسماح للجميع) */
    'allowed_origins' => [
        'https://www.eliterealestateco.com',
        'https://eliterealestateco.com',
    ],
];
