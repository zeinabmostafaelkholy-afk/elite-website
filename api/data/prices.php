<?php
/**
 * GET /api/data/prices.php
 * يرجّع جدول الأسعار والمعاملات كـ JSON (نفس ملف data/valuation-data.json).
 * مفيد لو حبيت تربط الأداة بتطبيق أو صفحة تانية.
 */
require __DIR__ . '/../lib/bootstrap.php';
elite_cors();
elite_json(['ok' => true, 'data' => elite_dataset()]);
