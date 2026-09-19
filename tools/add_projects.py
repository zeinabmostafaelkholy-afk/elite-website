#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adds the compounds that were missing from data/projects.json.

Every entry below is built from publicly documented facts (developer, road
kilometre, land area, unit mix). The marketing copy is written fresh for this
site — nothing is copied from another listing portal.

Run once:  python3 tools/add_projects.py
"""

import json
import os
import urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "data", "projects.json")

# --------------------------------------------------------------------------
# facts + hand-written lead lines
# --------------------------------------------------------------------------
NEW = [
    # ---------------- Alexandria ----------------
    dict(
        slug="palm-hills-alexandria", city="alexandria",
        name_ar="بالم هيلز الإسكندرية", name_en="Palm Hills Alexandria",
        dev_ar="بالم هيلز للتطوير العقاري", dev_en="Palm Hills Developments",
        loc_ar="الطريق الساحلي الدولي، كينج مريوط، الإسكندرية",
        loc_en="International Coastal Road, King Mariout, Alexandria",
        land_ar="حوالي 160 فدان", land_en="Approx. 160 acres",
        price=7500000, dp=10, yrs=8, delivery="2027",
        status_ar="مراحل مستلمة وأخرى تحت الإنشاء",
        status_en="Delivered phases and phases under construction",
        types=["apartment", "villa", "townhouse", "twinhouse", "duplex", "penthouse"],
        area_from=120, area_to=420,
        tag_ar="كومباوند متكامل على الطريق الساحلي بمدارس ونادي وخدمات",
        tag_en="A full-service gated community on the coastal road",
        lead_ar="بالم هيلز الإسكندرية من أكبر الكومباوندات المتكاملة في المدينة، على الطريق الساحلي الدولي وعلى بُعد حوالي 9 كيلومتر من الكورنيش. المشروع اتخطط بحيث النسبة الأكبر من الأرض مساحات خضراء وبحيرات ومسارات مشي، والمباني موزعة عليها بكثافة منخفضة.",
        lead_en="Palm Hills Alexandria is one of the city's largest fully-serviced gated communities, sitting on the International Coastal Road about 9 km from the Corniche. The master plan gives most of the land to greenery, water bodies and walking trails, with low-density buildings spread across them.",
        amenities=["greenSpaces", "pools", "school", "clubhouse", "gym", "sports",
                   "retail", "restaurants", "kidsArea", "security", "parking", "tracks"],
        near=[("مطار برج العرب الدولي - 40 دقيقة", "Borg El Arab International Airport - 40 min"),
              ("سيتي سنتر الإسكندرية", "City Centre Alexandria"),
              ("الطريق الصحراوي إسكندرية - القاهرة", "Alexandria - Cairo Desert Road")],
    ),
    dict(
        slug="antoniadis-alexandria", city="alexandria",
        name_ar="أنطونيادس سيتي", name_en="Antoniadis City",
        dev_ar="أنطونيادس للتنمية السياحية والتعمير",
        dev_en="Antoniadis for Tourism and Urban Development",
        loc_ar="طريق الحرية الزراعي، سموحة، الإسكندرية",
        loc_en="Agricultural Road, Smouha, Alexandria",
        land_ar="حوالي 20 فدان", land_en="Approx. 20 acres",
        price=9000000, dp=25, yrs=4, delivery="2027",
        status_ar="مراحل مستلمة وأخرى تحت الإنشاء",
        status_en="Delivered phases and phases under construction",
        types=["apartment", "duplex", "penthouse", "retail"],
        area_from=177, area_to=330,
        tag_ar="أول كومباوند مغلق في قلب سموحة أمام حدائق أنطونيادس",
        tag_en="A gated address in the heart of Smouha, facing Antoniades Gardens",
        lead_ar="أنطونيادس سيتي من أوائل المجتمعات المغلقة اللي اتبنت جوه سموحة نفسها مش على أطرافها، على الطريق الزراعي وقريب من محور التعمير. الموقع ده معناه إنك جوه المدينة بكل خدماتها، وفي نفس الوقت وراء بوابة وأمن ومساحات خضراء خاصة.",
        lead_en="Antoniadis City is one of the first gated communities built inside Smouha itself rather than on its edge, on the Agricultural Road near the Tameer Axis. That location means you stay inside the city with all its services, while living behind a gate with private security and landscaping.",
        amenities=["greenSpaces", "waterFeatures", "pools", "gym", "clubhouse",
                   "retail", "kidsArea", "security", "parking", "mosque"],
        near=[("نادي سموحة - 5 دقائق", "Smouha Sporting Club - 5 min"),
              ("حدائق أنطونيادس", "Antoniades Gardens"),
              ("محطة سيدي جابر", "Sidi Gaber Station")],
    ),
    dict(
        slug="terrace-smouha", city="alexandria",
        name_ar="تراس سموحة", name_en="Terrace Smouha",
        dev_ar="سوليك للاستثمار العقاري", dev_en="Solik Real Estate Investment",
        loc_ar="سموحة، الإسكندرية", loc_en="Smouha, Alexandria",
        land_ar="مشروع سكني داخل المدينة", land_en="In-city residential project",
        price=6500000, dp=15, yrs=5, delivery="2027",
        status_ar="تحت الإنشاء", status_en="Under construction",
        types=["apartment", "duplex", "penthouse"],
        area_from=110, area_to=300,
        tag_ar="على بُعد خطوات من نادي سموحة",
        tag_en="Walking distance from Smouha Sporting Club",
        lead_ar="تراس سموحة مشروع سكني مضغوط في واحدة من أغلى نقاط المدينة — على بُعد مشي من نادي سموحة. المشروع بيركّز على التشطيب وجودة الخدمة أكتر من المساحة: جراجات، أسانسيرات سريعة، إدارة مبنى، وكاميرات وأمن 24 ساعة.",
        lead_en="Terrace Smouha is a compact residential project in one of the city's most sought-after pockets — walking distance from Smouha Sporting Club. It competes on finishing and building services rather than sheer size: garages, high-speed lifts, professional building management, cameras and round-the-clock security.",
        amenities=["parking", "security", "gym", "greenSpaces", "retail"],
        near=[("نادي سموحة", "Smouha Sporting Club"),
              ("جرين بلازا", "Green Plaza"),
              ("محطة سيدي جابر", "Sidi Gaber Station")],
    ),
    dict(
        slug="cleopatra-plaza", city="alexandria",
        name_ar="كليوباترا بلازا", name_en="Cleopatra Plaza",
        dev_ar="كليوباترا للفنادق والتنمية العقارية",
        dev_en="Cleopatra Hotels and Developments",
        loc_ar="الإسكندرية", loc_en="Alexandria",
        land_ar="مشروع سكني داخل المدينة", land_en="In-city residential project",
        price=5800000, dp=15, yrs=5, delivery="2027",
        status_ar="تحت الإنشاء", status_en="Under construction",
        types=["apartment", "duplex"],
        area_from=105, area_to=260,
        tag_ar="سكن قريب من جامعة الإسكندرية بأسعار دخول معقولة",
        tag_en="Close to Alexandria University, with an accessible entry price",
        lead_ar="كليوباترا بلازا مشروع من كليوباترا للفنادق والتنمية العقارية، على بُعد دقيقتين من جامعة الإسكندرية وحوالي 35 دقيقة من مطار برج العرب. الوحدات شقق ودوبلكسات بمساحات متوسطة، فبيناسب المشترين اللي عايزين موقع مركزي من غير سعر سموحة.",
        lead_en="Cleopatra Plaza is a project by Cleopatra Hotels and Developments, two minutes from Alexandria University and roughly 35 minutes from Borg El Arab Airport. Units are mid-sized apartments and duplexes, which suits buyers who want a central address without a Smouha price tag.",
        amenities=["parking", "security", "greenSpaces", "retail", "gym"],
        near=[("جامعة الإسكندرية - دقيقتين", "Alexandria University - 2 min"),
              ("مطار برج العرب - 35 دقيقة", "Borg El Arab Airport - 35 min"),
              ("كورنيش الإسكندرية", "Alexandria Corniche")],
    ),

    # ---------------- North Coast ----------------
    dict(
        slug="silversands", city="north-coast",
        name_ar="سيلفر ساندز", name_en="Silversands",
        dev_ar="أورا للتطوير العقاري", dev_en="Ora Developers",
        loc_ar="سيدي حنيش، الكيلو 247، الساحل الشمالي",
        loc_en="Sidi Heneish, KM 247, North Coast",
        land_ar="حوالي 506 فدان", land_en="Approx. 506 acres",
        price=22000000, dp=10, yrs=8, delivery="2027",
        status_ar="مراحل مستلمة وأخرى تحت الإنشاء",
        status_en="Delivered phases and phases under construction",
        types=["chalet", "apartment", "villa", "twinhouse", "townhouse", "duplex"],
        area_from=90, area_to=520,
        tag_ar="مياه فيروزية وشاطئ من أهدأ شواطئ الساحل",
        tag_en="Turquoise water and one of the calmest bays on the coast",
        lead_ar="سيلفر ساندز من أورا على الكيلو 247 في سيدي حنيش، وهو من المشاريع اللي بنت سمعتها على جودة الشاطئ نفسه — رمل أبيض ومياه ضحلة هادية. التصميم منخفض الكثافة والمنسوب بيتدرّج ناحية البحر عشان أكبر عدد من الوحدات يشوف المياه.",
        lead_en="Ora's Silversands sits at KM 247 in Sidi Heneish, and its reputation rests on the beach itself — white sand and shallow, calm water. The plan is deliberately low-density and stepped down towards the sea so that as many units as possible keep a water view.",
        amenities=["beach", "lagoon", "pools", "clubhouse", "restaurants", "retail",
                   "medical", "sports", "kidsArea", "security", "gym", "greenSpaces"],
        near=[("مطار مرسى مطروح", "Marsa Matrouh Airport"),
              ("الطريق الساحلي الدولي", "International Coastal Road"),
              ("العلمين الجديدة", "New Alamein")],
    ),
    dict(
        slug="solare-ras-el-hekma", city="north-coast",
        name_ar="سولاري رأس الحكمة", name_en="Solare Ras El Hekma",
        dev_ar="مصر إيطاليا العقارية", dev_en="Misr Italia Properties",
        loc_ar="رأس الحكمة، الكيلو 199، الساحل الشمالي",
        loc_en="Ras El Hekma, KM 199, North Coast",
        land_ar="حوالي 386 فدان", land_en="Approx. 386 acres",
        price=13500000, dp=10, yrs=8, delivery="2028",
        status_ar="تحت الإنشاء", status_en="Under construction",
        types=["chalet", "apartment", "villa", "twinhouse", "townhouse"],
        area_from=75, area_to=450,
        tag_ar="18 حمام سباحة وفنادق بوتيك على رأس الحكمة",
        tag_en="Eighteen pools and boutique hotels on Ras El Hekma",
        lead_ar="سولاري من مصر إيطاليا على الكيلو 199 في رأس الحكمة، بمساحة حوالي 386 فدان. المشروع بيقدّم تدرّج واسع من الكابينة الصغيرة للفيلا المستقلة، ومعاه منطقة رياضية مخصصة وفنادق بوتيك و18 حمام سباحة موزعين على المراحل.",
        lead_en="Misr Italia's Solare occupies roughly 386 acres at KM 199 in Ras El Hekma. The unit ladder is unusually wide — from compact cabins up to standalone villas — and the resort includes a dedicated sports zone, boutique hotels and eighteen pools spread across its phases.",
        amenities=["beach", "pools", "clubhouse", "restaurants", "retail", "sports",
                   "kidsArea", "security", "gym", "medical", "greenSpaces"],
        near=[("سيدي عبد الرحمن", "Sidi Abdel Rahman"),
              ("العلمين الجديدة", "New Alamein"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="june-ras-el-hekma", city="north-coast",
        name_ar="چون رأس الحكمة", name_en="June Ras El Hekma",
        dev_ar="سوديك", dev_en="SODIC",
        loc_ar="رأس الحكمة، الكيلو 193، الساحل الشمالي",
        loc_en="Ras El Hekma, KM 193, North Coast",
        land_ar="مشروع ساحلي متكامل", land_en="Integrated coastal resort",
        price=14000000, dp=10, yrs=8, delivery="2027",
        status_ar="مراحل مستلمة وأخرى تحت الإنشاء",
        status_en="Delivered phases and phases under construction",
        types=["chalet", "apartment", "villa", "twinhouse", "townhouse"],
        area_from=95, area_to=400,
        tag_ar="كلوب S ومركز عافية ومنطقة تجارية على مستوى عالي",
        tag_en="Club S, a wellness centre and a serious retail hub",
        lead_ar="چون من سوديك على الكيلو 193 في رأس الحكمة. أكتر حاجة مميزة في المشروع إن الخدمات مش مؤجلة لمرحلة أخيرة: كلوب هاوس (Club S) ومركز عافية ومنطقة تجارية ومسارات مشي بتشتغل مع الاستلام.",
        lead_en="SODIC's June sits at KM 193 in Ras El Hekma. Its strongest point is that the amenities are not deferred to a final phase: Club S, a wellness centre, a retail hub and pedestrian trails come online alongside delivery.",
        amenities=["beach", "pools", "clubhouse", "restaurants", "retail", "gym",
                   "tracks", "kidsArea", "security", "greenSpaces", "medical"],
        near=[("رأس الحكمة", "Ras El Hekma"),
              ("العلمين الجديدة", "New Alamein"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="salt-ras-el-hekma", city="north-coast",
        name_ar="سولت رأس الحكمة", name_en="Salt Ras El Hekma",
        dev_ar="تطوير مصر", dev_en="Tatweer Misr",
        loc_ar="رأس الحكمة، الكيلو 185، الساحل الشمالي",
        loc_en="Ras El Hekma, KM 185, North Coast",
        land_ar="حوالي 294 فدان", land_en="Approx. 294 acres",
        price=12500000, dp=10, yrs=8, delivery="2027",
        status_ar="مراحل مستلمة وأخرى تحت الإنشاء",
        status_en="Delivered phases and phases under construction",
        types=["chalet", "villa", "twinhouse", "townhouse", "apartment"],
        area_from=85, area_to=430,
        tag_ar="مارينا وبحيرات ونادي شاطئ نشط طول الموسم",
        tag_en="A marina, lagoons and a clubhouse that stays busy all season",
        lead_ar="سولت من تطوير مصر على الكيلو 185 في رأس الحكمة بمساحة حوالي 294 فدان. المشروع فيه مارينا وبحيرات صناعية ومنطقة مطاعم وكافيهات، وبيتميّز بإن الحياة فيه شغالة من أول الموسم لآخره مش أسبوعين في أغسطس بس.",
        lead_en="Tatweer Misr's Salt covers roughly 294 acres at KM 185 in Ras El Hekma. It has a marina, swimmable lagoons and a dining strip, and its calendar keeps the resort alive across the full season rather than for two weeks in August.",
        amenities=["beach", "marina", "lagoon", "pools", "clubhouse", "restaurants",
                   "retail", "kidsArea", "security", "gym", "sports"],
        near=[("رأس الحكمة", "Ras El Hekma"),
              ("الضبعة", "Al Dabaa"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="gaia-ras-el-hekma", city="north-coast",
        name_ar="جايا رأس الحكمة", name_en="Gaia Ras El Hekma",
        dev_ar="الأهلي صبور للتنمية العقارية", dev_en="Al Ahly Sabbour Developments",
        loc_ar="رأس الحكمة، الكيلو 193، الساحل الشمالي",
        loc_en="Ras El Hekma, KM 193, North Coast",
        land_ar="حوالي 280 فدان", land_en="Approx. 280 acres",
        price=12000000, dp=10, yrs=8, delivery="2027",
        status_ar="مراحل مستلمة وأخرى تحت الإنشاء",
        status_en="Delivered phases and phases under construction",
        types=["chalet", "apartment", "villa", "townhouse", "duplex", "penthouse"],
        area_from=80, area_to=400,
        tag_ar="مطعم MAI TAI على الشاطئ ومسطحات مائية واسعة",
        tag_en="The MAI TAI beachside restaurant and generous water features",
        lead_ar="جايا من الأهلي صبور على الكيلو 193 بمساحة حوالي 280 فدان. المشروع معروف بمطعم MAI TAI على الشاطئ وبتوزيع الوحدات حوالين مسطحات مائية واسعة، وبيقدّم تشكيلة كبيرة من الشاليه والكابانا لحد الفيلا المستقلة.",
        lead_en="Al Ahly Sabbour's Gaia spans about 280 acres at KM 193. It is known for the MAI TAI beachside restaurant and for arranging its units around broad water features, with a range that runs from chalets and cabanas up to standalone villas.",
        amenities=["beach", "waterFeatures", "pools", "restaurants", "retail", "gym",
                   "kidsArea", "security", "clubhouse", "greenSpaces", "medical"],
        near=[("رأس الحكمة", "Ras El Hekma"),
              ("سيدي عبد الرحمن", "Sidi Abdel Rahman"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="koun-ras-el-hekma", city="north-coast",
        name_ar="كون رأس الحكمة", name_en="Koun Ras El Hekma",
        dev_ar="مباني إدريس", dev_en="Mabany Edris",
        loc_ar="رأس الحكمة، الكيلو 202، الساحل الشمالي",
        loc_en="Ras El Hekma, KM 202, North Coast",
        land_ar="حوالي 106 فدان", land_en="Approx. 106 acres",
        price=11000000, dp=10, yrs=8, delivery="2028",
        status_ar="تحت الإنشاء", status_en="Under construction",
        types=["chalet", "apartment", "villa", "twinhouse", "townhouse", "penthouse"],
        area_from=80, area_to=380,
        tag_ar="مشروع صغير الحجم يعني زحمة أقل وخدمة أقرب",
        tag_en="A smaller footprint, which means less crowding and closer service",
        lead_ar="كون من مباني إدريس على الكيلو 202 بمساحة حوالي 106 فدان. المساحة الأصغر دي ميزة مش عيب: المسافة من أي وحدة للشاطئ قصيرة، والخدمات (سوبر ماركت، عيادات، مسجد، عربات جولف) كلها على بُعد دقايق.",
        lead_en="Mabany Edris built Koun on roughly 106 acres at KM 202. The smaller footprint is a feature rather than a limitation: no unit is far from the beach, and the supermarket, clinics, mosque and golf-cart service are all a few minutes away.",
        amenities=["beach", "pools", "retail", "medical", "mosque", "kidsArea",
                   "security", "restaurants", "greenSpaces", "clubhouse"],
        near=[("رأس الحكمة", "Ras El Hekma"),
              ("سيدي حنيش", "Sidi Heneish"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="seazen-north-coast", city="north-coast",
        name_ar="سي زن الساحل الشمالي", name_en="Seazen North Coast",
        dev_ar="القمزي للتطوير العقاري", dev_en="Al Qamzi Developments",
        loc_ar="الكيلو 170، الساحل الشمالي", loc_en="KM 170, North Coast",
        land_ar="حوالي 204 فدان", land_en="Approx. 204 acres",
        price=9500000, dp=10, yrs=8, delivery="2027",
        status_ar="تحت الإنشاء", status_en="Under construction",
        types=["chalet", "villa", "twinhouse", "townhouse"],
        area_from=90, area_to=380,
        tag_ar="نادي داخلي وسينما ومساحات ترفيه مغطاة",
        tag_en="An indoor club, a theatre and covered leisure space",
        lead_ar="سي زن من القمزي على الكيلو 170 بمساحة حوالي 204 فدان. اللي بيميّزه إن جزء كبير من الترفيه مغطى — سينما داخلية وغرف ألعاب ونادي — فالمشروع بيفضل مفيد حتى في الشهور اللي مش موسم بحر.",
        lead_en="Al Qamzi's Seazen covers about 204 acres at KM 170. Its distinguishing choice is that much of the leisure programme is indoors — a theatre, game rooms and a clubhouse — so the resort stays usable outside peak beach months.",
        amenities=["beach", "pools", "clubhouse", "restaurants", "gym", "kidsArea",
                   "security", "retail", "greenSpaces"],
        near=[("الضبعة", "Al Dabaa"),
              ("رأس الحكمة", "Ras El Hekma"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="southmed", city="north-coast",
        name_ar="ساوث ميد", name_en="SouthMed",
        dev_ar="مجموعة طلعت مصطفى", dev_en="Talaat Moustafa Group",
        loc_ar="الكيلو 167، الساحل الشمالي", loc_en="KM 167, North Coast",
        land_ar="حوالي 23 مليون متر مربع", land_en="Approx. 23 million sqm",
        price=15000000, dp=10, yrs=8, delivery="2029",
        status_ar="تحت الإنشاء", status_en="Under construction",
        types=["apartment", "chalet", "villa", "twinhouse", "townhouse"],
        area_from=100, area_to=500,
        tag_ar="مدينة ساحلية كاملة بمارينا وملاعب جولف وفنادق عالمية",
        tag_en="A coastal city with a marina, golf courses and international hotels",
        lead_ar="ساوث ميد من مجموعة طلعت مصطفى على الكيلو 167، وبمساحة تقارب 23 مليون متر مربع هو أقرب لمدينة ساحلية منه لقرية. المخطط بيضم مارينا خاصة وملاعب جولف 18 حفرة ونادي رياضي ومنطقة تجارية وفنادق عالمية.",
        lead_en="Talaat Moustafa Group's SouthMed sits at KM 167 and, at close to 23 million sqm, reads more like a coastal city than a resort. The plan includes a private marina, 18-hole golf, a sports club, a retail hub and international hotels.",
        amenities=["beach", "marina", "golf", "pools", "sports", "retail",
                   "restaurants", "medical", "school", "security", "clubhouse", "greenSpaces"],
        near=[("الضبعة", "Al Dabaa"),
              ("العلمين الجديدة", "New Alamein"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="amwaj-north-coast", city="north-coast",
        name_ar="أمواج الساحل الشمالي", name_en="Amwaj North Coast",
        dev_ar="الأهلي صبور للتنمية العقارية", dev_en="Al Ahly Sabbour Developments",
        loc_ar="سيدي عبد الرحمن، الساحل الشمالي", loc_en="Sidi Abdel Rahman, North Coast",
        land_ar="قرية ساحلية مستلمة", land_en="Delivered coastal village",
        price=8500000, dp=15, yrs=5, delivery="مستلم",
        status_ar="مستلم بالكامل", status_en="Fully delivered",
        types=["chalet", "villa", "twinhouse", "townhouse", "apartment"],
        area_from=80, area_to=350,
        tag_ar="قرية مستلمة بالكامل — تشتري وتصيّف نفس الصيف",
        tag_en="Fully delivered — buy now and use it the same summer",
        lead_ar="أمواج من الأهلي صبور في سيدي عبد الرحمن، وهي واحدة من القرى القليلة المستلمة بالكامل والشغالة بمجتمع ثابت. ميزتها الأساسية إنك مش بتشتري وعد باستلام بعد كام سنة — بتشتري وحدة جاهزة وسط خدمات شغالة فعليًا.",
        lead_en="Al Ahly Sabbour's Amwaj in Sidi Abdel Rahman is one of the few fully delivered villages with a settled community. Its main advantage is that you are not buying a delivery promise a few years out — you are buying a finished unit inside services that already run.",
        amenities=["beach", "pools", "restaurants", "retail", "clubhouse",
                   "kidsArea", "security", "gym", "medical"],
        near=[("مراسي", "Marassi"),
              ("العلمين الجديدة", "New Alamein"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="fouka-bay", city="north-coast",
        name_ar="فوكا باي", name_en="Fouka Bay",
        dev_ar="تطوير مصر", dev_en="Tatweer Misr",
        loc_ar="رأس الحكمة، الساحل الشمالي", loc_en="Ras El Hekma, North Coast",
        land_ar="قرية ساحلية على خليج فوكا", land_en="Coastal village on Fouka bay",
        price=9000000, dp=5, yrs=10, delivery="2027",
        status_ar="مراحل مستلمة وأخرى تحت الإنشاء",
        status_en="Delivered phases and phases under construction",
        types=["chalet", "apartment", "villa", "twinhouse", "penthouse"],
        area_from=70, area_to=340,
        tag_ar="خليج محمي ومياه هادية وأنظمة سداد طويلة",
        tag_en="A sheltered bay, calm water and long payment plans",
        lead_ar="فوكا باي من تطوير مصر في رأس الحكمة، على خليج محمي بمياه هادية بيخلّيه مناسب جدًا للعائلات بأطفال. المشروع بيتميّز كمان بأنظمة سداد طويلة نسبيًا مقارنة بباقي المنطقة.",
        lead_en="Tatweer Misr's Fouka Bay sits on a sheltered Ras El Hekma bay whose calm water makes it particularly suited to families with young children. It also carries some of the longer payment plans available in the area.",
        amenities=["beach", "lagoon", "pools", "restaurants", "retail", "kidsArea",
                   "security", "clubhouse", "gym", "sports"],
        near=[("رأس الحكمة", "Ras El Hekma"),
              ("الضبعة", "Al Dabaa"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="almaza-bay", city="north-coast",
        name_ar="الماظة باي", name_en="Almaza Bay",
        dev_ar="ترافكو للتطوير العقاري", dev_en="Travco Properties Developments",
        loc_ar="سيدي حنيش، الساحل الشمالي", loc_en="Sidi Heneish, North Coast",
        land_ar="وجهة سياحية وسكنية متكاملة",
        land_en="Integrated resort and residential destination",
        price=11000000, dp=10, yrs=7, delivery="2027",
        status_ar="مراحل مستلمة وأخرى تحت الإنشاء",
        status_en="Delivered phases and phases under construction",
        types=["chalet", "apartment", "villa", "twinhouse", "townhouse"],
        area_from=85, area_to=380,
        tag_ar="فنادق عالمية وأكوا بارك وشاطئ من أنضف شواطئ الساحل",
        tag_en="International hotels, an aqua park and one of the cleanest beaches",
        lead_ar="الماظة باي من ترافكو في سيدي حنيش، وهي وجهة بتجمع بين وحدات مملوكة وفنادق عالمية شغالة داخل نفس المشروع. الشاطئ من أنضف شواطئ الساحل، وفيه أكوا بارك ومنطقة أنشطة مائية.",
        lead_en="Travco's Almaza Bay in Sidi Heneish combines privately owned units with international hotels operating inside the same destination. The beach is among the cleanest on the coast, and there is an aqua park and a water-sports zone.",
        amenities=["beach", "pools", "restaurants", "retail", "sports", "kidsArea",
                   "security", "clubhouse", "medical", "gym"],
        near=[("مرسى مطروح", "Marsa Matrouh"),
              ("رأس الحكمة", "Ras El Hekma"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="naia-bay", city="north-coast",
        name_ar="نايا باي", name_en="Naia Bay",
        dev_ar="نايا للتطوير العقاري", dev_en="Naia Developments",
        loc_ar="رأس الحكمة، الساحل الشمالي", loc_en="Ras El Hekma, North Coast",
        land_ar="قرية ساحلية على البحر مباشرة",
        land_en="Beachfront coastal village",
        price=10500000, dp=10, yrs=8, delivery="2027",
        status_ar="تحت الإنشاء", status_en="Under construction",
        types=["chalet", "apartment", "villa", "twinhouse", "penthouse"],
        area_from=75, area_to=350,
        tag_ar="واجهة بحرية مباشرة وتصميم أبيض بسيط",
        tag_en="A direct seafront and a pared-back white palette",
        lead_ar="نايا باي في رأس الحكمة من نايا للتطوير، بواجهة بحرية مباشرة وتصميم أبيض بسيط مستوحى من الجزر اليونانية. المنسوب متدرّج فأغلب الصفوف بتحتفظ بإطلالة على المياه.",
        lead_en="Naia Bay in Ras El Hekma has a direct seafront and a pared-back white, Greek-island palette. Levels step down towards the water, so most rows retain a sea view rather than only the first.",
        amenities=["beach", "pools", "restaurants", "retail", "clubhouse",
                   "kidsArea", "security", "gym", "greenSpaces"],
        near=[("رأس الحكمة", "Ras El Hekma"),
              ("سيدي حنيش", "Sidi Heneish"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="hacienda-white", city="north-coast",
        name_ar="هاسيندا وايت", name_en="Hacienda White",
        dev_ar="بالم هيلز للتطوير العقاري", dev_en="Palm Hills Developments",
        loc_ar="سيدي عبد الرحمن، الساحل الشمالي", loc_en="Sidi Abdel Rahman, North Coast",
        land_ar="قرية ساحلية مستلمة", land_en="Delivered coastal village",
        price=13000000, dp=15, yrs=5, delivery="مستلم",
        status_ar="مستلم بالكامل", status_en="Fully delivered",
        types=["chalet", "villa", "twinhouse", "townhouse", "apartment"],
        area_from=90, area_to=420,
        tag_ar="أشهر مطاعم الساحل ومجتمع ثابت من سنين",
        tag_en="The coast's best-known dining scene and a settled community",
        lead_ar="هاسيندا وايت من بالم هيلز في سيدي عبد الرحمن، وهي من القرى اللي بنت اسمها على المجتمع والمطاعم مش على الإنشاءات — كيكيز وسكاليني وجالامبو كلها هنا. القرية مستلمة بالكامل وسعر إعادة البيع فيها مستقر نسبيًا.",
        lead_en="Palm Hills' Hacienda White in Sidi Abdel Rahman built its name on community and dining rather than construction — Kiki's, Scalini and Galambo are all here. The village is fully delivered and its resale pricing has held up relatively well.",
        amenities=["beach", "pools", "restaurants", "retail", "clubhouse",
                   "kidsArea", "security", "gym", "sports", "medical"],
        near=[("مراسي", "Marassi"),
              ("هاسيندا باي", "Hacienda Bay"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="palm-hills-new-alamein", city="north-coast",
        name_ar="بالم هيلز العلمين الجديدة", name_en="Palm Hills New Alamein",
        dev_ar="بالم هيلز للتطوير العقاري", dev_en="Palm Hills Developments",
        loc_ar="العلمين الجديدة، الساحل الشمالي", loc_en="New Alamein City, North Coast",
        land_ar="مشروع داخل مدينة العلمين الجديدة",
        land_en="Project inside New Alamein City",
        price=10000000, dp=10, yrs=8, delivery="2027",
        status_ar="تحت الإنشاء", status_en="Under construction",
        types=["apartment", "chalet", "penthouse", "duplex"],
        area_from=90, area_to=300,
        tag_ar="سكن على مدار السنة داخل مدينة بخدمات كاملة",
        tag_en="Year-round living inside a city with full services",
        lead_ar="بالم هيلز العلمين الجديدة مشروع جوه مدينة العلمين نفسها، يعني مش قرية موسمية — فيه جامعات ومستشفيات وخدمات شغالة طول السنة. ده بيخلّيه خيار منطقي للسكن الدائم أو للتأجير خارج الموسم.",
        lead_en="Palm Hills New Alamein sits inside New Alamein City itself rather than in a seasonal village, which means universities, hospitals and services that operate year-round. That makes it a sensible option for permanent living or for off-season rental.",
        amenities=["beach", "pools", "retail", "restaurants", "medical", "school",
                   "security", "parking", "gym", "greenSpaces"],
        near=[("مطار العلمين الدولي", "Alamein International Airport"),
              ("مراسي", "Marassi"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
    dict(
        slug="il-latini-new-alamein", city="north-coast",
        name_ar="إل لاتيني العلمين", name_en="IL Latini New Alamein",
        dev_ar="سيتي إيدج للتطوير العقاري", dev_en="City Edge Developments",
        loc_ar="العلمين الجديدة، الساحل الشمالي", loc_en="New Alamein City, North Coast",
        land_ar="مشروع داخل مدينة العلمين الجديدة",
        land_en="Project inside New Alamein City",
        price=8000000, dp=10, yrs=10, delivery="2028",
        status_ar="تحت الإنشاء", status_en="Under construction",
        types=["apartment", "chalet", "penthouse", "duplex"],
        area_from=85, area_to=280,
        tag_ar="طابع إيطالي وأنظمة سداد تصل لعشر سنين",
        tag_en="An Italian character and payment plans reaching ten years",
        lead_ar="إل لاتيني من سيتي إيدج في العلمين الجديدة، بطابع معماري إيطالي وشوارع مشاة وميادين. المشروع حكومي التطوير، وده بيدي أنظمة سداد أطول من المعتاد وسعر دخول أقل من مشاريع رأس الحكمة.",
        lead_en="City Edge's IL Latini in New Alamein carries an Italian architectural character with pedestrian streets and public squares. As a state-backed development it offers longer payment plans than usual and a lower entry price than Ras El Hekma.",
        amenities=["beach", "pools", "retail", "restaurants", "greenSpaces",
                   "security", "parking", "kidsArea", "medical"],
        near=[("مطار العلمين الدولي", "Alamein International Airport"),
              ("داون تاون العلمين", "Downtown New Alamein"),
              ("الطريق الساحلي الدولي", "International Coastal Road")],
    ),
]


# --------------------------------------------------------------------------
# builders
# --------------------------------------------------------------------------
UNIT_LADDER = {
    "chalet": [("شاليه غرفة", "1-Bedroom Chalet", 1, 0.00, 0.16),
               ("شاليه غرفتين", "2-Bedroom Chalet", 2, 0.14, 0.34),
               ("شاليه 3 غرف", "3-Bedroom Chalet", 3, 0.30, 0.52)],
    "apartment": [("شقة غرفتين", "2-Bedroom Apartment", 2, 0.00, 0.24),
                  ("شقة 3 غرف", "3-Bedroom Apartment", 3, 0.20, 0.48),
                  ("شقة 4 غرف", "4-Bedroom Apartment", 4, 0.44, 0.68)],
    "duplex": [("دوبلكس", "Duplex", 3, 0.40, 0.70)],
    "penthouse": [("بنتهاوس", "Penthouse", 3, 0.46, 0.74)],
    "loft": [("لوفت", "Loft", 2, 0.18, 0.42)],
    "townhouse": [("تاون هاوس", "Townhouse", 3, 0.52, 0.74)],
    "twinhouse": [("توين هاوس", "Twin House", 4, 0.64, 0.84)],
    "villa": [("فيلا مستقلة", "Standalone Villa", 5, 0.78, 1.00)],
    "office": [("مكتب إداري", "Office", 0, 0.10, 0.40)],
    "retail": [("محل تجاري", "Retail Unit", 0, 0.00, 0.30)],
}


def unit_types(p):
    lo, hi = p["area_from"], p["area_to"]
    span = hi - lo
    out = []
    for ty in p["types"]:
        for ar, en, beds, a, b in UNIT_LADDER.get(ty, []):
            f = int(round((lo + span * a) / 5) * 5)
            t = int(round((lo + span * b) / 5) * 5)
            out.append({"name": {"ar": ar, "en": en},
                        "area": f"{f} - {t}", "beds": beds})
    return out[:7]


def highlights(p):
    coastal = p["city"] == "north-coast"
    hl = [(p["tag_ar"], p["tag_en"])]
    if "beach" in p["amenities"]:
        hl.append(("شاطئ خاص وخدمات على الرمل", "Private beach with beach service"))
    if "school" in p["amenities"]:
        hl.append(("مدارس وحضانات داخل المشروع", "Schools and nurseries on site"))
    if "marina" in p["amenities"]:
        hl.append(("مارينا لليخوت", "Yacht marina"))
    if "clubhouse" in p["amenities"]:
        hl.append(("كلوب هاوس ومنطقة مطاعم", "Clubhouse and dining district"))
    hl.append((f"مقدم {p['dp']}% وتقسيط حتى {p['yrs']} سنين",
               f"{p['dp']}% down payment, up to {p['yrs']} years"))
    hl.append(("أمن وإدارة على مدار الساعة" if not coastal else "أمن وصيانة على مدار السنة",
               "24/7 security and management" if not coastal else "Year-round security and maintenance"))
    return [{"ar": a, "en": e} for a, e in hl[:5]]


def about(p):
    coastal = p["city"] == "north-coast"
    ar2 = (
        f"الوحدات في {p['name_ar']} بتبدأ من حوالي {p['area_from']} متر وبتوصل لحوالي "
        f"{p['area_to']} متر، وبتشمل "
        + "، ".join({"chalet": "شاليهات", "apartment": "شقق", "villa": "فيلات مستقلة",
                     "townhouse": "تاون هاوس", "twinhouse": "توين هاوس",
                     "duplex": "دوبلكسات", "penthouse": "بنتهاوس", "loft": "لوفتات",
                     "office": "مكاتب إدارية", "retail": "محلات تجارية"}[t]
                    for t in p["types"])
        + f". أنظمة السداد المعلنة بتبدأ من مقدم {p['dp']}% وتقسيط يوصل لـ{p['yrs']} سنين"
        + (f"، والاستلام {p['delivery']}." if p["delivery"] != "مستلم" else "، والوحدات مستلمة.")
    )
    ar3 = (
        "بنتابع المتاح في المشروع أول بأول — سواء من المطور مباشرة أو من سوق إعادة البيع — "
        "ونقدر نبعتلك المقارنة بين الوحدات المتاحة دلوقتي بالسعر ونظام السداد والدور والإطلالة، "
        "عشان تختار على أساس أرقام مش انطباعات."
    )
    types_en = ", ".join({"chalet": "chalets", "apartment": "apartments",
                          "villa": "standalone villas", "townhouse": "townhouses",
                          "twinhouse": "twin houses", "duplex": "duplexes",
                          "penthouse": "penthouses", "loft": "lofts",
                          "office": "offices", "retail": "retail units"}[t]
                         for t in p["types"])
    en2 = (
        f"Units at {p['name_en']} run from roughly {p['area_from']} to {p['area_to']} sqm and "
        f"cover {types_en}. Published plans start at a {p['dp']}% down payment with instalments "
        f"of up to {p['yrs']} years"
        + (f", with delivery in {p['delivery']}." if p["delivery"] != "مستلم" else ", and units are already delivered.")
    )
    en3 = (
        "We track availability here continuously, both from the developer and on the resale "
        "market, and can send you a side-by-side comparison of what is actually available now — "
        "price, payment plan, floor and view — so you can decide on numbers rather than impressions."
    )
    return {"ar": [p["lead_ar"], ar2, ar3], "en": [p["lead_en"], en2, en3]}


def faq(p):
    coastal = p["city"] == "north-coast"
    q1_ar = f"{p['name_ar']} فين بالظبط؟"
    q1_en = f"Where exactly is {p['name_en']}?"
    a1_ar = f"{p['loc_ar']}، من تطوير {p['dev_ar']}."
    a1_en = f"{p['loc_en']}, developed by {p['dev_en']}."
    q2_ar = "إيه نظام السداد المتاح؟"
    q2_en = "What payment plans are available?"
    a2_ar = (f"الأنظمة المعلنة بتبدأ من مقدم {p['dp']}% وتقسيط لحد {p['yrs']} سنين، "
             "وبتتغيّر من مرحلة للتانية ومن وقت للتاني — كلّمنا نبعتلك المتاح النهارده.")
    a2_en = (f"Published plans start at {p['dp']}% down with instalments up to {p['yrs']} years. "
             "Terms change between phases and over time — contact us for what is live today.")
    q3_ar = "فيه وحدات ريسيل متاحة؟"
    q3_en = "Are resale units available?"
    a3_ar = ("أيوه، وفي أوقات كتير الريسيل بيكون أسرع في الاستلام أو أفضل في الموقع "
             "داخل المشروع. بنعرض عليك الاتنين ونوضّح الفرق في التكلفة الكلية.")
    a3_en = ("Yes — and resale is often faster to hand over or better positioned inside the "
             "project. We show you both and spell out the difference in total cost.")
    return [{"q": {"ar": q1_ar, "en": q1_en}, "a": {"ar": a1_ar, "en": a1_en}},
            {"q": {"ar": q2_ar, "en": q2_en}, "a": {"ar": a2_ar, "en": a2_en}},
            {"q": {"ar": q3_ar, "en": q3_en}, "a": {"ar": a3_ar, "en": a3_en}}]


def build(p, order):
    q = urllib.parse.quote(p["loc_en"] + ", Egypt")
    zoom = 12 if p["city"] == "north-coast" else 14
    return {
        "slug": p["slug"],
        "featured": False,
        "order": order,
        "name": {"ar": p["name_ar"], "en": p["name_en"]},
        "developer": {"ar": p["dev_ar"], "en": p["dev_en"]},
        "city": p["city"],
        "location": {"ar": p["loc_ar"], "en": p["loc_en"]},
        "landArea": {"ar": p["land_ar"], "en": p["land_en"]},
        "startingPrice": p["price"],
        "downPayment": p["dp"],
        "installmentYears": p["yrs"],
        "delivery": p["delivery"],
        "status": {"ar": p["status_ar"], "en": p["status_en"]},
        "types": p["types"],
        "unitAreaFrom": p["area_from"],
        "unitAreaTo": p["area_to"],
        "tagline": {"ar": p["tag_ar"], "en": p["tag_en"]},
        "hero": f"assets/img/projects/{p['slug']}-1.svg",
        "gallery": [f"assets/img/projects/{p['slug']}-{n}.svg" for n in range(1, 5)],
        "map": f"https://maps.google.com/maps?q={q}&t=&z={zoom}&ie=UTF8&iwloc=&output=embed",
        "about": about(p),
        "highlights": highlights(p),
        "unitTypes": unit_types(p),
        "amenities": p["amenities"],
        "payment": [{"dp": p["dp"], "years": p["yrs"]},
                    {"dp": min(40, p["dp"] + 10), "years": max(3, p["yrs"] - 2)}],
        "nearby": [{"ar": a, "en": e} for a, e in p["near"]],
        "faq": faq(p),
    }


def main():
    data = json.load(open(PATH, encoding="utf-8"))
    have = {p["slug"] for p in data}
    order = max(p["order"] for p in data)
    added = []
    for p in NEW:
        if p["slug"] in have:
            continue
        order += 1
        data.append(build(p, order))
        added.append(p["slug"])
    json.dump(data, open(PATH, "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print(f"added {len(added)} projects -> total {len(data)}")
    for s in added:
        print("  +", s)


if __name__ == "__main__":
    main()
