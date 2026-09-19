<?php
/**
 * Elite Real Estate — محرّك التقييم (نفس منطق assets/js/valuation.js)
 */

function elite_find($list, $id) {
    foreach ($list as $item) if ($item['id'] === $id) return $item;
    return null;
}

function elite_region($data, $id) { return elite_find($data['regions'], $id); }

function elite_zone($data, $regionId, $zoneId) {
    $r = elite_region($data, $regionId);
    return $r ? elite_find($r['zones'], $zoneId) : null;
}

function elite_area_factor($data, $area) {
    foreach ($data['areaBands'] as $b) if ($area <= $b['max']) return $b['f'];
    return 1.0;
}

/**
 * @param array $in مدخلات المستخدم
 * @return array|null
 */
function elite_estimate($in) {
    $D = elite_dataset();

    $region = elite_region($D, isset($in['region']) ? $in['region'] : '');
    $zone   = elite_zone($D, isset($in['region']) ? $in['region'] : '', isset($in['zone']) ? $in['zone'] : '');
    if (!$region || !$zone) return null;

    $area = isset($in['area']) ? (float)$in['area'] : 0;
    if ($area < 25 || $area > 2000) return null;

    $type   = elite_find($D['types'], isset($in['type']) ? $in['type'] : 'apartment')   ?: $D['types'][0];
    $finish = elite_find($D['finishes'], isset($in['finish']) ? $in['finish'] : 'super-lux') ?: elite_find($D['finishes'], 'super-lux');
    $age    = elite_find($D['ages'], isset($in['age']) ? $in['age'] : '0-5')            ?: elite_find($D['ages'], '0-5');
    $legal  = elite_find($D['legal'], isset($in['legal']) ? $in['legal'] : 'contract')  ?: elite_find($D['legal'], 'contract');
    $pay    = elite_find($D['payment'], isset($in['payment']) ? $in['payment'] : 'cash') ?: elite_find($D['payment'], 'cash');

    $flat  = in_array($type['id'], ['apartment', 'studio', 'duplex', 'penthouse'], true);
    $floor = $flat ? (elite_find($D['floors'], isset($in['floor']) ? $in['floor'] : 'low') ?: elite_find($D['floors'], 'low')) : null;

    $featSum = 0.0; $picked = [];
    $features = isset($in['features']) && is_array($in['features']) ? $in['features'] : [];
    foreach ($features as $fid) {
        $f = elite_find($D['features'], $fid);
        if ($f) { $featSum += $f['p']; $picked[] = $f; }
    }
    $featSum = max(-0.15, min($D['featureCap'], $featSum));

    $aF = elite_area_factor($D, $area);

    $perSqm = $zone['sqm'] * $type['f'] * $finish['f'] * $age['f'] * $legal['f'] * $pay['f'] * $aF * (1 + $featSum);
    if ($floor) $perSqm *= $floor['f'];

    $value = $perSqm * $area;

    $filled = 0;
    foreach (['beds', 'baths', 'legal', 'age', 'finish'] as $k) if (!empty($in[$k])) $filled++;
    $spread = $D['spread'] + ($filled >= 5 ? 0 : 0.03) + (count($features) ? 0 : 0.01);
    $confidence = ($filled >= 5 && count($features)) ? 'high' : ($filled >= 3 ? 'medium' : 'indicative');

    $yield = $region['yield'];

    return [
        'perSqm'       => round($perSqm),
        'marketPerSqm' => $zone['sqm'],
        'value'        => round($value),
        'low'          => round($value * (1 - $spread)),
        'high'         => round($value * (1 + $spread)),
        'rentMonthly'  => round($value * $yield / 12),
        'rentSeason'   => $region['seasonal'] ? round($value * 0.045) : 0,
        'seasonal'     => (bool)$region['seasonal'],
        'yieldPct'     => round($yield * 100, 1),
        'area'         => $area,
        'confidenceKey' => $confidence,
        'zoneLabel'    => $zone['ar'] . ' - ' . $region['ar'],
        'zoneLabelEn'  => $zone['en'] . ' - ' . $region['en'],
        'typeLabel'    => $type['ar'],
        'typeLabelEn'  => $type['en'],
    ];
}
