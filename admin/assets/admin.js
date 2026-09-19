/* Elite Real Estate — لوحة التحكم
   وحدات (إضافة / تعديل / حذف / ترتيب / مميزة / صور / معاينة الكارت) + مستخدمين.
   بتكلّم admin/api.php، وكل حفظ بيظهر على الموقع فورًا. */
(function () {
  "use strict";
  var C = window.EliteCards;
  var app = document.getElementById("app");
  var PER = 25;
  var S = { csrf: "", user: null, units: [], comps: {}, users: [], view: "units", q: "", fcomp: "", ftype: "", fflag: "", page: 1 };
  var E = null; /* الوحدة المفتوحة في المحرر */

  var TYPES = [["apartment", "شقة"], ["villa", "فيلا"], ["chalet", "شاليه"], ["townhouse", "تاون هاوس"], ["twinhouse", "توين هاوس"],
    ["duplex", "دوبلكس"], ["penthouse", "بنتهاوس"], ["studio", "ستوديو"], ["cabin", "كابينة"], ["loft", "لوفت"], ["office", "مكتب إداري"],
    ["administrative", "إداري"], ["retail", "تجاري"], ["medical", "طبي"], ["pharmacy", "صيدلية"], ["unit", "وحدة (نوع غير محدد)"]];
  var CITIES = [["north-coast", "الساحل الشمالي"], ["alexandria", "الإسكندرية"], ["cairo", "القاهرة"], ["giza", "الجيزة"], ["other", "مناطق أخرى في مصر"]];
  var FEATURES = [["seaView", "إطلالة بحر"], ["lagoonView", "إطلالة لاجون"], ["privatePool", "حمام سباحة خاص"], ["pool", "حمام سباحة"],
    ["pools", "حمامات سباحة مشتركة"], ["garden", "حديقة"], ["roof", "روف"], ["roofTerrace", "تراس علوي"], ["balcony", "بلكونة"],
    ["parking", "جراج"], ["security", "أمن 24 ساعة"], ["elevator", "أسانسير"], ["furnished", "مفروش"], ["maidRoom", "غرفة خادمة"],
    ["driver", "غرفة سواق"], ["nanny", "غرفة مربية"], ["beachAccess", "وصول للشاطئ"], ["clubhouse", "كلوب هاوس"], ["school", "مدرسة"],
    ["compound", "داخل كمبوند"], ["gym", "جيم"], ["kidsArea", "منطقة أطفال"], ["kitchen", "مطبخ مجهز"], ["ac", "تكييفات"],
    ["spa", "سبا"], ["row5", "الصف الخامس"], ["commercial", "منطقة تجارية"]];
  var FREQ = [["monthly", "شهري"], ["quarterly", "ربع سنوي"], ["semi-annually", "نصف سنوي"], ["annually", "سنوي"]];
  var typeName = {}; TYPES.forEach(function (t) { typeName[t[0]] = t[1]; });

  function esc(s) { return C.esc(s); }
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function opts(list, cur) {
    return list.map(function (o) { return '<option value="' + esc(o[0]) + '"' + (o[0] === cur ? " selected" : "") + ">" + esc(o[1]) + "</option>"; }).join("");
  }
  function money(n) { return C.money(n); }
  function comp(u) { return S.comps[u.compound]; }
  function compName(u) { var c = comp(u); return c ? c.name.ar : ""; }

  /* ---------- toast ---------- */
  function toast(msg, kind) {
    var t = document.createElement("div");
    t.className = "toast" + (kind ? " toast--" + kind : "");
    t.textContent = msg;
    $("#toasts").appendChild(t);
    setTimeout(function () { t.remove(); }, kind === "err" ? 6000 : 3200);
  }

  /* ---------- API ---------- */
  function api(action, body, retried) {
    var o = { credentials: "same-origin", headers: { "X-CSRF-Token": S.csrf } };
    if (body !== undefined) { o.method = "POST"; o.headers["Content-Type"] = "application/json"; o.body = JSON.stringify(body); }
    return fetch("api.php?a=" + action, o).then(function (r) {
      return r.json().then(function (j) { return { r: r, j: j }; }, function () { return { r: r, j: { ok: false, error: "رد غير صالح من السيرفر (اتأكد إن PHP شغال)" } }; });
    }, function () { throw new Error("مقدرتش أكلم السيرفر. اتأكد إن الموقع شغال."); }).then(function (x) {
      if (x.r.status === 419 && !retried) return loadSession().then(function () { return api(action, body, true); });
      if (x.r.status === 401 && action !== "login" && action !== "session") { S.user = null; renderLogin(); throw new Error(x.j.error || "انتهت الجلسة"); }
      if (!x.j.ok) { var e = new Error(x.j.error || "حصل خطأ"); e.data = x.j; throw e; }
      return x.j;
    });
  }
  function upload(file) {
    var fd = new FormData(); fd.append("file", file);
    return fetch("api.php?a=upload", { method: "POST", credentials: "same-origin", headers: { "X-CSRF-Token": S.csrf }, body: fd })
      .then(function (r) { return r.json(); }).then(function (j) { if (!j.ok) throw new Error(j.error || "فشل الرفع"); return j.url; });
  }

  function loadSession() {
    return api("session").then(function (j) { S.csrf = j.csrf; S.user = j.user; });
  }
  function loadAll() {
    return api("bootstrap").then(function (j) {
      S.user = j.user; S.units = j.units; S.comps = j.compounds || {};
      renderShell();
      if (S.user.mustChange) openPassword(true);
    });
  }

  /* ---------- login ---------- */
  function renderLogin() {
    closeModal(true);
    app.innerHTML = '<form class="login" id="loginf"><h1>لوحة تحكم إيليت</h1><p class="sub">سجّلي الدخول لإدارة الوحدات</p>' +
      '<label class="fld"><span>اسم المستخدم</span><input name="username" class="ltr" autocomplete="username" required autofocus></label>' +
      '<label class="fld"><span>الباسورد</span><input name="password" type="password" class="ltr" autocomplete="current-password" required></label>' +
      '<p class="err" id="lerr" hidden></p><button class="btn btn--brass">دخول</button></form>';
    $("#loginf").addEventListener("submit", function (e) {
      e.preventDefault();
      var f = e.target, b = $(".btn", f); b.disabled = true;
      api("login", { username: f.username.value, password: f.password.value }).then(function (j) {
        S.csrf = j.csrf; S.user = j.user; S.view = "units"; S.q = S.fcomp = S.ftype = S.fflag = ""; S.page = 1; return loadAll();
      }).catch(function (er) {
        var p = $("#lerr"); p.hidden = false; p.textContent = er.message; b.disabled = false;
      });
    });
  }

  /* ---------- shell ---------- */
  function renderShell() {
    var admin = S.user.role === "admin";
    app.innerHTML = '<header class="top"><span class="top__brand">إيليت — لوحة التحكم</span><nav>' +
      '<button data-view="units" class="' + (S.view === "units" ? "on" : "") + '">الوحدات</button>' +
      (admin ? '<button data-view="users" class="' + (S.view === "users" ? "on" : "") + '">المستخدمين</button>' : "") +
      '<a href="leads.php">طلبات التقييم</a><a href="../ar/index.html" target="_blank" rel="noopener">شوف الموقع</a></nav>' +
      '<div class="top__user"><span>' + esc(S.user.name) + '</span><button data-pass>تغيير الباسورد</button><button data-logout>خروج</button></div></header>' +
      '<main class="wrap" id="view"></main>';
    renderView();
  }
  function renderView() {
    $$(".top nav [data-view]").forEach(function (b) { b.classList.toggle("on", b.dataset.view === S.view); });
    if (S.view === "users" && S.user.role !== "admin") S.view = "units";
    if (S.view === "users") return usersView();
    unitsView();
  }

  /* ---------- الوحدات: القائمة ---------- */
  function unitsView() {
    var comps = Object.keys(S.comps).map(function (k) { return S.comps[k]; }).sort(function (a, b) { return b.km - a.km; });
    var compOpts = '<option value="">كل الكمبوندات</option><option value="__none"' + (S.fcomp === "__none" ? " selected" : "") + ">بدون كمبوند</option>" +
      comps.map(function (c) { return '<option value="' + esc(c.slug) + '"' + (S.fcomp === c.slug ? " selected" : "") + ">" + esc(c.name.ar + " — كم " + c.km) + "</option>"; }).join("");
    $("#view").innerHTML = '<div class="bar"><input class="field-inline search grow" id="q" type="search" placeholder="ابحث بالاسم أو الكود أو الكمبوند…" value="' + esc(S.q) + '">' +
      '<select class="field-inline" id="fcomp">' + compOpts + "</select>" +
      '<select class="field-inline" id="ftype"><option value="">كل الأنواع</option>' + opts(TYPES, S.ftype) + "</select>" +
      '<select class="field-inline" id="fflag">' + opts([["", "كل الوحدات"], ["featured", "المميزة فقط"], ["ask", "السعر عند الطلب"]], S.fflag) + "</select>" +
      '<button class="btn btn--brass" data-new>+ وحدة جديدة</button></div><p class="count" id="cnt"></p><div id="list"></div>';
    $("#q").addEventListener("input", function (e) { S.q = e.target.value; S.page = 1; renderList(); });
    $("#fcomp").addEventListener("change", function (e) { S.fcomp = e.target.value; S.page = 1; renderList(); });
    $("#ftype").addEventListener("change", function (e) { S.ftype = e.target.value; S.page = 1; renderList(); });
    $("#fflag").addEventListener("change", function (e) { S.fflag = e.target.value; S.page = 1; renderList(); });
    renderList();
  }
  function filtered() {
    var q = S.q.trim().toLowerCase();
    var a = S.units.filter(function (u) {
      if (S.fcomp === "__none") { if (u.compound) return false; } else if (S.fcomp && u.compound !== S.fcomp) return false;
      if (S.ftype && u.type !== S.ftype) return false;
      if (S.fflag === "featured" && !u.featured) return false;
      if (S.fflag === "ask" && !C.isAsk(u)) return false;
      if (q) {
        var c = comp(u);
        var hay = [u.id, u.title.ar, u.title.en, u.location.ar, u.location.en, c ? c.name.ar + " " + c.name.en : ""].join(" ").toLowerCase();
        if (hay.indexOf(q) < 0) return false;
      }
      return true;
    });
    a.sort(S.fcomp && S.fcomp !== "__none" ? C.byCompound : C.byDefault);
    return a;
  }
  function renderList() {
    var all = filtered(), pages = Math.max(1, Math.ceil(all.length / PER));
    if (S.page > pages) S.page = pages;
    var rows = all.slice((S.page - 1) * PER, S.page * PER);
    $("#cnt").textContent = all.length + " وحدة" + (all.length !== S.units.length ? " (من " + S.units.length + ")" : "") + " — الترتيب هنا هو نفس ترتيب الظهور على الموقع";
    if (!rows.length) { $("#list").innerHTML = '<div class="tbl-wrap"><p class="empty">مفيش وحدات مطابقة.</p></div>'; return; }
    var html = '<div class="tbl-wrap"><table><thead><tr><th></th><th>الوحدة</th><th>الكمبوند</th><th>النوع</th><th>السعر</th><th>الترتيب</th><th>مميزة</th><th></th></tr></thead><tbody>';
    rows.forEach(function (u) {
      var ask = C.isAsk(u);
      html += '<tr data-id="' + esc(u.id) + '"><td><img class="thumb" loading="lazy" referrerpolicy="no-referrer" src="' + esc(C.imgSrc("../", u.image)) + '" alt=""></td>' +
        '<td><div class="t1">' + esc(u.title.ar) + '</div><div class="t2">' + esc(u.id) + (u.purpose === "rent" ? " · إيجار" : "") + "</div></td>" +
        "<td>" + (compName(u) ? esc(compName(u)) : '<span class="t2">—</span>') + "</td><td>" + esc(typeName[u.type] || u.type) + "</td>" +
        "<td>" + (ask ? '<span class="tag tag--ask">عند الطلب</span>' : esc(money(u.price)) + (u.priceUnit === "monthly" ? " / شهر" : "")) + "</td>" +
        '<td><input class="ord ltr" type="number" data-ord="' + esc(u.id) + '" value="' + (u.order === null || u.order === undefined ? "" : esc(u.order)) + '" placeholder="تلقائي" title="رقم أصغر = يظهر أول"></td>' +
        '<td><button class="iconbtn star' + (u.featured ? " on" : "") + '" data-star="' + esc(u.id) + '" title="مميزة" aria-pressed="' + (u.featured ? "true" : "false") + '">★</button></td>' +
        '<td class="act"><button class="btn btn--ghost btn--sm" data-edit="' + esc(u.id) + '">تعديل</button> <button class="btn btn--ghost btn--sm" data-dup="' + esc(u.id) + '">نسخ</button> ' +
        '<button class="btn btn--danger btn--sm" data-del="' + esc(u.id) + '">حذف</button></td></tr>';
    });
    html += "</tbody></table></div>";
    if (pages > 1) {
      html += '<div class="pager">';
      for (var p = 1; p <= pages; p++) {
        if (pages > 12 && Math.abs(p - S.page) > 3 && p !== 1 && p !== pages) { if (p === 2 || p === pages - 1) html += "<span>…</span>"; continue; }
        html += '<button data-page="' + p + '" class="' + (p === S.page ? "on" : "") + '">' + p + "</button>";
      }
      html += "</div>";
    }
    $("#list").innerHTML = html;
    if (window.EliteImgFix) window.EliteImgFix.sweep();
  }
  function byId(id) { for (var i = 0; i < S.units.length; i++) if (String(S.units[i].id) === String(id)) return S.units[i]; return null; }
  function replaceUnit(u) {
    for (var i = 0; i < S.units.length; i++) if (String(S.units[i].id) === String(u.id)) { S.units[i] = u; return; }
    S.units.push(u);
  }
  function patch(id, p) {
    return api("unit_patch", { id: id, patch: p }).then(function (j) { replaceUnit(j.unit); renderList(); toast("اتحفظ — ظهر على الموقع", "ok"); })
      .catch(function (e) { toast(e.message, "err"); renderList(); });
  }

  /* ---------- المحرر ---------- */
  function modalRoot() {
    var r = $("#modal");
    if (!r) { r = document.createElement("div"); r.id = "modal"; document.body.appendChild(r); }
    return r;
  }
  function closeModal(force) {
    if (!force && E && E.dirty && !confirm("فيه تعديلات ما اتحفظتش. تقفلي من غير حفظ؟")) return;
    var r = $("#modal"); if (r) r.innerHTML = "";
    E = null; document.body.style.overflow = "";
  }

  function blankUnit(compSlug) {
    var c = S.comps[compSlug];
    return { id: "", title: { ar: "", en: "" }, location: { ar: c ? c.name.ar + "، " + c.area.ar + "، الساحل الشمالي" : "", en: c ? c.name.en + ", " + c.area.en + ", North Coast" : "" },
      type: "apartment", purpose: "sale", city: c ? "north-coast" : "alexandria", compound: compSlug || null, price: 0, priceOnRequest: false,
      priceUnit: "total", area: 0, beds: 0, baths: 0, finishing: { ar: "", en: "" }, delivery: { ar: "", en: "" }, description: { ar: "", en: "" },
      features: [], plans: [], featured: false, recommended: false, order: null, image: "", gallery: [], saleType: "", phase: "", developer: "" };
  }

  function openEditor(u, isNew) {
    var src = JSON.parse(JSON.stringify(u));
    var imgs = [];
    [src.image].concat(src.gallery || []).forEach(function (x) { if (x && imgs.indexOf(x) < 0 && !/assets\/img\/(compounds\/|brand\/fallback)/.test(x)) imgs.push(x); });
    pvReady = false;
    E = { isNew: isNew, id: isNew ? "" : src.id, u: src, imgs: imgs, plans: (src.plans && src.plans.length ? src.plans : legacyPlans(src)).map(function (p) { return Object.assign({}, p); }), dirty: false, lang: "ar", busy: false };
    var root = modalRoot();
    document.body.style.overflow = "hidden";
    root.innerHTML = '<div class="veil"><div class="editor" role="dialog" aria-modal="true">' +
      '<div class="editor__head"><h2>' + (isNew ? "وحدة جديدة" : "تعديل: " + esc(src.title.ar)) + '</h2>' +
      (!isNew ? '<a class="btn btn--ghost btn--sm" target="_blank" rel="noopener" href="../ar/property.html?id=' + encodeURIComponent(src.id) + '">شوفها على الموقع</a>' : "") +
      '<button class="btn btn--ghost" data-ed-close>إلغاء</button><button class="btn btn--brass" data-ed-save>حفظ</button></div>' +
      '<div class="editor__body"><div id="edform">' + formHTML(src) + '</div>' +
      '<aside class="preview"><div class="preview__bar"><b style="flex:1">معاينة الكارت</b><button class="btn btn--ghost on" data-plang="ar">عربي</button><button class="btn btn--ghost" data-plang="en">English</button></div>' +
      '<iframe id="pv" title="معاينة" src="preview.html"></iframe><p class="hint">المعاينة بتتحدّث وإنتِ بتكتبي، وبتستخدم نفس كود الموقع فالكارت هيطلع بنفس الشكل.</p></aside></div>' +
      '<p class="err" id="ederr" hidden style="padding:0 22px 16px"></p></div></div>';
    renderImgs(); renderPlans(); syncPriceUI();
    E.dirty = false;
  }
  function legacyPlans(u) {
    var pp = u.paymentPlan || {};
    if (pp.minInstallment && !pp.isCash) return [{ installment: pp.minInstallment, frequency: pp.frequency || "monthly", years: pp.years || null, down: pp.minDownPayment || null }];
    return [];
  }

  function fld(label, inner, cls) { return '<label class="fld' + (cls ? " " + cls : "") + '"><span>' + label + "</span>" + inner + "</label>"; }
  function inp(name, val, extra) { return '<input name="' + name + '" value="' + esc(val === null || val === undefined ? "" : val) + '" ' + (extra || "") + ">"; }
  function num(name, val) { return '<input name="' + name + '" class="ltr" inputmode="decimal" value="' + (val ? esc(val) : "") + '">'; }

  function formHTML(u) {
    var compList = Object.keys(S.comps).map(function (k) { return S.comps[k]; }).sort(function (a, b) { return b.km - a.km; })
      .map(function (c) { return [c.slug, c.name.ar + " — كم " + c.km]; });
    return '<div class="sec"><h3>الأساسيات</h3><div class="grid">' +
      fld("العنوان بالعربي", inp("title.ar", u.title.ar)) + fld("العنوان بالإنجليزي (English title)", inp("title.en", u.title.en, 'class="ltr"')) +
      fld("نوع الوحدة", '<select name="type">' + opts(TYPES, u.type) + "</select>") +
      fld("الغرض", '<select name="purpose">' + opts([["sale", "للبيع"], ["rent", "للإيجار"]], u.purpose) + "</select>") +
      fld("الكمبوند (على خريطة الساحل)", '<select name="compound"><option value="">— مش في كمبوند —</option>' + opts(compList, u.compound || "") + "</select>", "fld--full") +
      fld("المدينة / المنطقة", '<select name="city">' + opts(CITIES, u.city) + "</select>") + fld("المرحلة داخل الكمبوند (اختياري)", inp("phase", u.phase || "")) +
      fld("الموقع بالعربي", inp("location.ar", u.location.ar)) + fld("Location (English)", inp("location.en", u.location.en, 'class="ltr"')) +
      "</div></div>" +
      '<div class="sec"><h3>السعر</h3><div class="grid grid--3">' +
      fld("السعر (جنيه)", num("price", u.price)) + fld("أعلى سعر (اختياري)", num("maxPrice", u.maxPrice)) +
      fld("نوع السعر", '<select name="priceUnit">' + opts([["total", "إجمالي"], ["monthly", "شهري (إيجار)"]], u.priceUnit || "total") + "</select>") +
      '<label class="chk fld--full"><input type="checkbox" name="priceOnRequest"' + (u.priceOnRequest ? " checked" : "") + '> السعر عند الطلب (يظهر "السعر عند الطلب" بدل الرقم)</label></div></div>' +
      '<div class="sec"><h3>المواصفات</h3><div class="grid grid--4">' +
      fld("المساحة (م²)", num("area", u.area)) + fld("أقصى مساحة", num("areaMax", u.areaMax)) + fld("غرف النوم", num("beds", u.beds)) + fld("الحمامات", num("baths", u.baths)) +
      "</div><div class=\"grid\" style=\"margin-top:12px\">" +
      fld("التشطيب (عربي)", inp("finishing.ar", u.finishing && u.finishing.ar)) + fld("Finishing (English)", inp("finishing.en", u.finishing && u.finishing.en, 'class="ltr"')) +
      fld("الاستلام (عربي) مثال: 2028 أو استلام فوري", inp("delivery.ar", u.delivery && u.delivery.ar)) + fld("Delivery (English) e.g. 2028 / Ready to move", inp("delivery.en", u.delivery && u.delivery.en, 'class="ltr"')) +
      fld("الدور", inp("floor", u.floor || "", 'class="ltr"')) + fld("نوع البيع", '<select name="saleType">' + opts([["", "—"], ["developer", "من المطور"], ["resale", "إعادة بيع"]], u.saleType || "") + "</select>") +
      fld("المطور (اختياري)", inp("developer", u.developer || ""), "fld--full") + "</div></div>" +
      '<div class="sec"><h3>أنظمة السداد</h3><div id="plans"></div><button type="button" class="btn btn--ghost btn--sm" data-addplan>+ إضافة نظام سداد</button>' +
      '<p class="hint">القسط بيظهر على الكارت. سيبيها فاضية لو مفيش تقسيط.</p></div>' +
      '<div class="sec"><h3>الوصف</h3><div class="grid">' +
      fld("الوصف بالعربي", '<textarea name="description.ar">' + esc(u.description && u.description.ar) + "</textarea>") +
      fld("Description (English)", '<textarea name="description.en" class="ltr">' + esc(u.description && u.description.en) + "</textarea>") + "</div></div>" +
      '<div class="sec"><h3>المميزات</h3><div class="feats">' + FEATURES.map(function (f) {
        return '<label class="chk"><input type="checkbox" name="feat" value="' + f[0] + '"' + ((u.features || []).indexOf(f[0]) > -1 ? " checked" : "") + "> " + f[1] + "</label>";
      }).join("") + "</div></div>" +
      '<div class="sec"><h3>الصور</h3><div class="imgs" id="imgs"></div>' +
      '<div class="bar" style="margin-bottom:8px"><label class="btn btn--ghost btn--sm" style="cursor:pointer">رفع صور من الجهاز<input id="upl" type="file" accept="image/*" multiple hidden></label><span id="upstat" class="count"></span></div>' +
      '<div class="addlink"><input id="lnk" placeholder="أو الصقي لينك صورة https://…"><button type="button" class="btn btn--ghost btn--sm" data-addlink>إضافة اللينك</button></div>' +
      '<p class="hint">أول صورة هي الرئيسية. لو مفيش صور بتظهر صورة الكمبوند تلقائيًا. الصور المرفوعة بتتصغّر تلقائيًا لو السيرفر بيدعم ذلك.</p></div>' +
      '<div class="sec"><h3>العرض على الموقع</h3><div class="grid">' +
      '<label class="chk"><input type="checkbox" name="featured"' + (u.featured ? " checked" : "") + '> وحدة مميزة (تظهر أول + في الرئيسية)</label>' +
      '<label class="chk"><input type="checkbox" name="recommended"' + (u.recommended ? " checked" : "") + '> مقترحة في الرئيسية</label>' +
      fld("الترتيب (رقم أصغر = يظهر أول، سيبيه فاضي لو تلقائي)", num("order", u.order === null || u.order === undefined ? "" : u.order)) +
      "</div></div>";
  }

  function renderImgs() {
    var box = $("#imgs"); if (!box) return;
    box.innerHTML = E.imgs.length ? E.imgs.map(function (s, i) {
      return '<div class="im"><img referrerpolicy="no-referrer" src="' + esc(C.imgSrc("../", s)) + '" alt="">' + (i === 0 ? '<span class="im__main">رئيسية</span>' : "") +
        '<div class="im__bar"><button type="button" data-imove="' + i + '" data-dir="-1" title="قدّم">→</button><button type="button" data-imove="' + i + '" data-dir="1" title="أخّر">←</button>' +
        '<button type="button" data-idel="' + i + '" title="احذف">✕</button></div></div>';
    }).join("") : '<p class="hint" style="grid-column:1/-1">مفيش صور — هتظهر صورة الكمبوند.</p>';
    if (window.EliteImgFix) window.EliteImgFix.sweep();
    schedulePreview();
  }
  function renderPlans() {
    var box = $("#plans"); if (!box) return;
    box.innerHTML = E.plans.map(function (p, i) {
      return '<div class="plan-row" data-plan="' + i + '"><label class="fld"><span>القسط</span><input class="ltr" data-pk="installment" inputmode="numeric" value="' + (p.installment ? esc(p.installment) : "") + '"></label>' +
        '<label class="fld"><span>التكرار</span><select data-pk="frequency">' + opts(FREQ, p.frequency || "monthly") + "</select></label>" +
        '<label class="fld"><span>عدد السنين</span><input class="ltr" data-pk="years" inputmode="decimal" value="' + (p.years ? esc(p.years) : "") + '"></label>' +
        '<label class="fld"><span>المقدم (جنيه)</span><input class="ltr" data-pk="down" inputmode="numeric" value="' + (p.down ? esc(p.down) : "") + '"></label>' +
        '<button type="button" class="iconbtn" data-delplan="' + i + '" title="احذف">✕</button></div>';
    }).join("");
  }
  function syncPriceUI() {
    var f = $("#edform"); if (!f) return;
    var c = $('[name="priceOnRequest"]', f), p = $('[name="price"]', f);
    if (c && p) { p.disabled = c.checked; }
  }

  function num2(v) { v = String(v == null ? "" : v).replace(/[,\s٬]/g, ""); var n = parseFloat(v); return isFinite(n) && n > 0 ? n : 0; }
  function readForm() {
    var root = $("#edform"), o = { title: {}, location: {}, finishing: {}, delivery: {}, description: {}, features: [] };
    $$("[name]", root).forEach(function (el) {
      var k = el.name, v;
      if (k === "feat") { if (el.checked) o.features.push(el.value); return; }
      v = el.type === "checkbox" ? el.checked : el.value;
      var parts = k.split(".");
      if (parts.length === 2) o[parts[0]][parts[1]] = v; else o[k] = v;
    });
    ["price", "maxPrice", "area", "areaMax", "beds", "baths"].forEach(function (k) { o[k] = num2(o[k]); });
    o.order = String(o.order).trim() === "" ? null : parseInt(o.order, 10);
    if (isNaN(o.order)) o.order = null;
    o.compound = o.compound || null;
    o.plans = E.plans.map(function (p) {
      return { installment: num2(p.installment), frequency: p.frequency || "monthly", years: num2(p.years) || null, down: num2(p.down) || null };
    }).filter(function (p) { return p.installment > 0; });
    o.images = E.imgs.slice();
    o.image = o.images[0] || (o.compound ? "assets/img/compounds/" + o.compound + ".jpg" : "assets/img/brand/fallback.jpg");
    o.gallery = o.images.slice();
    o.id = E.id; o.createdAt = E.u.createdAt; o.sourceUrl = E.u.sourceUrl;
    return o;
  }

  /* معاينة */
  var pvTimer = null, pvReady = false;
  function schedulePreview() { clearTimeout(pvTimer); pvTimer = setTimeout(sendPreview, 120); }
  function sendPreview() {
    var fr = $("#pv"); if (!fr || !E || !pvReady || !fr.contentWindow) return;
    var d = readForm();
    fr.contentWindow.postMessage({ type: "unit", unit: d, compound: S.comps[d.compound] || null, lang: E.lang }, location.origin);
  }
  window.addEventListener("message", function (e) {
    if (e.origin !== location.origin || !e.data) return;
    if (e.data.type === "preview-ready") { pvReady = true; sendPreview(); }
    if (e.data.type === "preview-height") { var fr = $("#pv"); if (fr) fr.style.height = Math.max(420, e.data.h + 8) + "px"; }
  });

  function saveUnit() {
    if (E.busy) return;
    var d = readForm();
    var btn = $("[data-ed-save]"); E.busy = true; btn.disabled = true; btn.textContent = "جاري الحفظ…";
    var payload = JSON.parse(JSON.stringify(d)); payload._existing = !E.isNew;
    api("unit_save", { unit: payload }).then(function (j) {
      replaceUnit(j.unit);
      E.dirty = false; closeModal(true);
      renderList();
      toast("تم الحفظ — التعديل ظاهر على الموقع دلوقتي", "ok");
    }).catch(function (er) {
      E.busy = false; btn.disabled = false; btn.textContent = "حفظ";
      var p = $("#ederr"); p.hidden = false; p.textContent = er.message; p.scrollIntoView({ block: "nearest" });
      toast(er.message, "err");
    });
  }

  /* ---------- المستخدمين ---------- */
  function usersView() {
    $("#view").innerHTML = '<div class="bar"><h2 class="grow">المستخدمين</h2><button class="btn btn--brass" data-newuser>+ مستخدم جديد</button></div><div id="ulist"><p class="count">جاري التحميل…</p></div>';
    api("users").then(function (j) { S.users = j.users; renderUsers(); }).catch(function (e) { $("#ulist").innerHTML = '<p class="err">' + esc(e.message) + "</p>"; });
  }
  function renderUsers() {
    var el = $("#ulist"); if (!el) return;
    el.innerHTML = '<div class="tbl-wrap"><table><thead><tr><th>اسم المستخدم</th><th>الاسم</th><th>الصلاحية</th><th>آخر دخول</th><th></th></tr></thead><tbody>' +
      S.users.map(function (u) {
        var me = u.username.toLowerCase() === S.user.username.toLowerCase();
        return "<tr><td class=\"ltr\">" + esc(u.username) + (me ? ' <span class="tag">إنتِ</span>' : "") + "</td><td>" + esc(u.name) + "</td><td>" + (u.role === "admin" ? "مدير" : "محرر وحدات") + "</td>" +
          "<td>" + esc(u.lastLogin || "—") + '</td><td class="act"><button class="btn btn--ghost btn--sm" data-edituser="' + esc(u.username) + '">تعديل</button> ' +
          (me ? "" : '<button class="btn btn--danger btn--sm" data-deluser="' + esc(u.username) + '">حذف</button>') + "</td></tr>";
      }).join("") + "</tbody></table></div><p class=\"hint\">المدير بيدير المستخدمين والوحدات. المحرر بيدير الوحدات بس.</p>";
  }
  function openUser(u) {
    var isNew = !u; u = u || { username: "", name: "", role: "editor" };
    modalRoot().innerHTML = '<div class="veil"><form class="modal" id="uform"><h2>' + (isNew ? "مستخدم جديد" : "تعديل " + esc(u.username)) + "</h2>" +
      '<div class="grid" style="grid-template-columns:1fr">' +
      fld("اسم المستخدم (إنجليزي)", '<input name="username" class="ltr" value="' + esc(u.username) + '"' + (isNew ? "" : " readonly") + " required>") +
      fld("الاسم", '<input name="name" value="' + esc(u.name) + '">') +
      fld("الصلاحية", '<select name="role">' + opts([["editor", "محرر وحدات"], ["admin", "مدير (كل الصلاحيات)"]], u.role) + "</select>") +
      fld(isNew ? "الباسورد (8 حروف على الأقل)" : "باسورد جديد (سيبيه فاضي لو مش هتغيّريه)", '<input name="password" type="password" class="ltr" autocomplete="new-password"' + (isNew ? " required" : "") + ">") +
      '</div><p class="err" id="uerr" hidden></p><div class="row-btns"><button class="btn btn--brass">حفظ</button><button type="button" class="btn btn--ghost" data-m-close>إلغاء</button></div></form></div>';
    $("#uform").addEventListener("submit", function (e) {
      e.preventDefault(); var f = e.target;
      api("user_save", { username: f.username.value, name: f.name.value, role: f.role.value, password: f.password.value, isNew: isNew }).then(function (j) {
        S.users = j.users; closeModal(true); renderUsers(); toast("تم حفظ المستخدم", "ok");
      }).catch(function (er) { var p = $("#uerr"); p.hidden = false; p.textContent = er.message; });
    });
  }
  function openPassword(forced) {
    modalRoot().innerHTML = '<div class="veil"><form class="modal" id="pform"><h2>' + (forced ? "غيّري الباسورد الأول" : "تغيير الباسورد") + "</h2>" +
      (forced ? '<p class="warn">الباسورد الحالي مؤقت. اختاري باسورد جديد قبل ما تكملي.</p>' : "") +
      '<div class="grid" style="grid-template-columns:1fr">' +
      fld("الباسورد الحالي", '<input name="current" type="password" class="ltr" autocomplete="current-password" required>') +
      fld("الباسورد الجديد (8 حروف على الأقل)", '<input name="next" type="password" class="ltr" autocomplete="new-password" required>') +
      fld("أكدي الباسورد الجديد", '<input name="again" type="password" class="ltr" autocomplete="new-password" required>') +
      '</div><p class="err" id="perr" hidden></p><div class="row-btns"><button class="btn btn--brass">حفظ</button>' +
      (forced ? "" : '<button type="button" class="btn btn--ghost" data-m-close>إلغاء</button>') + "</div></form></div>";
    $("#pform").addEventListener("submit", function (e) {
      e.preventDefault(); var f = e.target, p = $("#perr");
      if (f.next.value !== f.again.value) { p.hidden = false; p.textContent = "الباسوردين مش متطابقين"; return; }
      api("password", { current: f.current.value, next: f.next.value }).then(function (j) {
        S.user = j.user; closeModal(true); toast("تم تغيير الباسورد", "ok");
      }).catch(function (er) { p.hidden = false; p.textContent = er.message; });
    });
  }

  /* ---------- الأحداث ---------- */
  document.addEventListener("click", function (e) {
    var t = e.target.closest("button, a, [data-page]"); if (!t) return;
    var d = t.dataset;
    if (d.view) { S.view = d.view; renderView(); return; }
    if (d.logout !== undefined) { api("logout", {}).then(function () { S.user = null; loadSession().then(renderLogin); }); return; }
    if (d.pass !== undefined) { openPassword(false); return; }
    if (d.new !== undefined) { openEditor(blankUnit(S.fcomp && S.fcomp !== "__none" ? S.fcomp : ""), true); return; }
    if (d.edit) { var u = byId(d.edit); if (u) openEditor(u, false); return; }
    if (d.dup) {
      var s = byId(d.dup); if (!s) return;
      var c = JSON.parse(JSON.stringify(s)); c.id = ""; c.featured = false; c.order = null;
      c.title.ar += " (نسخة)"; c.title.en += " (copy)";
      openEditor(c, true); E.dirty = true; return;
    }
    if (d.del) {
      var x = byId(d.del); if (!x) return;
      if (!confirm("تمسحي الوحدة \"" + x.title.ar + "\" نهائيًا؟ ده هيشيلها من الموقع.")) return;
      api("unit_delete", { id: x.id }).then(function () { S.units = S.units.filter(function (y) { return y !== x; }); renderList(); toast("اتمسحت", "ok"); })
        .catch(function (er) { toast(er.message, "err"); });
      return;
    }
    if (d.star) { var y = byId(d.star); if (y) patch(y.id, { featured: !y.featured }); return; }
    if (d.page) { S.page = +d.page; renderList(); window.scrollTo(0, 0); return; }
    if (d.newuser !== undefined) { openUser(null); return; }
    if (d.edituser) { openUser(S.users.filter(function (z) { return z.username === d.edituser; })[0]); return; }
    if (d.deluser) {
      if (!confirm("تمسحي المستخدم " + d.deluser + "؟")) return;
      api("user_delete", { username: d.deluser }).then(function () { S.users = S.users.filter(function (z) { return z.username !== d.deluser; }); renderUsers(); toast("اتمسح", "ok"); })
        .catch(function (er) { toast(er.message, "err"); });
      return;
    }
    if (d.mClose !== undefined) { closeModal(true); return; }
    /* المحرر */
    if (!E) return;
    if (d.edClose !== undefined) { closeModal(false); return; }
    if (d.edSave !== undefined) { saveUnit(); return; }
    if (d.plang) { E.lang = d.plang; $$("[data-plang]").forEach(function (b) { b.classList.toggle("on", b.dataset.plang === E.lang); }); sendPreview(); return; }
    if (d.imove !== undefined) {
      var i = +d.imove, j = i + +d.dir;
      if (j >= 0 && j < E.imgs.length) { var tmp = E.imgs[i]; E.imgs[i] = E.imgs[j]; E.imgs[j] = tmp; E.dirty = true; renderImgs(); }
      return;
    }
    if (d.idel !== undefined) { E.imgs.splice(+d.idel, 1); E.dirty = true; renderImgs(); return; }
    if (d.addlink !== undefined) {
      var l = $("#lnk"), v = l.value.trim();
      if (!/^(https?:\/\/|assets\/img\/)/i.test(v)) { toast("اللينك لازم يبدأ بـ https://", "err"); return; }
      if (E.imgs.indexOf(v) < 0) E.imgs.push(v);
      l.value = ""; E.dirty = true; renderImgs(); return;
    }
    if (d.addplan !== undefined) { E.plans.push({ installment: "", frequency: "monthly", years: "", down: "" }); E.dirty = true; renderPlans(); return; }
    if (d.delplan !== undefined) { E.plans.splice(+d.delplan, 1); E.dirty = true; renderPlans(); schedulePreview(); return; }
  });

  document.addEventListener("input", function (e) {
    var el = e.target;
    if (el.matches("[data-pk]")) {
      var row = el.closest("[data-plan]"); E.plans[+row.dataset.plan][el.dataset.pk] = el.value; E.dirty = true; schedulePreview(); return;
    }
    if (E && el.closest("#edform")) {
      E.dirty = true;
      if (el.name === "priceOnRequest") syncPriceUI();
      schedulePreview();
    }
  });
  document.addEventListener("change", function (e) {
    var el = e.target;
    if (el.matches("[data-pk]")) { var row = el.closest("[data-plan]"); E.plans[+row.dataset.plan][el.dataset.pk] = el.value; schedulePreview(); return; }
    if (el.matches("[data-ord]")) {
      var u = byId(el.dataset.ord); if (!u) return;
      var v = el.value.trim(); patch(u.id, { order: v === "" ? null : parseInt(v, 10) }); return;
    }
    if (el.id === "upl" && el.files.length) {
      var files = Array.prototype.slice.call(el.files), st = $("#upstat"), n = 0;
      el.value = "";
      (function next() {
        var f = files.shift();
        if (!f) { st.textContent = ""; renderImgs(); return; }
        st.textContent = "جاري رفع " + (++n) + "…";
        upload(f).then(function (url) { E.imgs.push(url); E.dirty = true; renderImgs(); next(); })
          .catch(function (er) { toast(er.message, "err"); next(); });
      })();
      return;
    }
    if (E && el.name === "compound" && el.closest("#edform")) {
      /* أول ما تختاري كمبوند: نملى الموقع والمدينة لو فاضيين */
      var c = S.comps[el.value], f = $("#edform");
      if (c) {
        if (!$('[name="location.ar"]', f).value) $('[name="location.ar"]', f).value = c.name.ar + "، " + c.area.ar + "، الساحل الشمالي";
        if (!$('[name="location.en"]', f).value) $('[name="location.en"]', f).value = c.name.en + ", " + c.area.en + ", North Coast";
        $('[name="city"]', f).value = "north-coast";
      }
      schedulePreview();
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && E) closeModal(false);
  });
  window.addEventListener("beforeunload", function (e) { if (E && E.dirty) { e.preventDefault(); e.returnValue = ""; } });

  /* ---------- تشغيل ---------- */
  loadSession().then(function () { return S.user ? loadAll() : renderLogin(); })
    .catch(function (e) { app.innerHTML = '<p class="boot">' + esc(e.message) + "</p>"; });
})();
