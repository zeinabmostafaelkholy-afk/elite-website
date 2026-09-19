/* ==========================================================================
   Elite Real Estate — shared behaviour
   ========================================================================== */
(function () {
  "use strict";

  var html = document.documentElement;
  var lang = html.lang === "ar" ? "ar" : "en";
  var base = html.dataset.base || "";

  /* ---------- preserve context when switching language ---------- */
  document.querySelectorAll(".lang-switch").forEach(function (link) {
    var href = link.getAttribute("href") || "";
    var isContextualPage = href.indexOf("property.html") !== -1 || href.indexOf("properties.html") !== -1;
    if (window.location.search && isContextualPage && href.indexOf("?") === -1) {
      link.setAttribute("href", href + window.location.search + window.location.hash);
    }
  });

  /* ---------- sticky header ---------- */
  var header = document.querySelector(".header");
  if (header) {
    var onScroll = function () {
      header.classList.toggle("is-solid", window.scrollY > 40);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---------- mobile drawer ---------- */
  var drawer = document.getElementById("drawer");
  var burger = document.querySelector(".burger");
  if (drawer && burger) {
    var setDrawer = function (open) {
      drawer.classList.toggle("is-open", open);
      burger.setAttribute("aria-expanded", String(open));
      document.body.style.overflow = open ? "hidden" : "";
    };
    burger.addEventListener("click", function () { setDrawer(true); });
    drawer.addEventListener("click", function (e) {
      if (e.target.closest("[data-drawer-close]") || e.target.tagName === "A") setDrawer(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setDrawer(false);
    });
  }

  /* ---------- WhatsApp widget ---------- */
  var wa = document.querySelector(".wa");
  if (wa) {
    var panel = wa.querySelector(".wa__panel");
    var toggle = wa.querySelector(".wa__btn");
    var closeBtn = wa.querySelector(".wa__close");
    var form = wa.querySelector(".wa__form");

    var setPanel = function (open) {
      panel.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      if (open) { var t = panel.querySelector("textarea"); if (t) t.focus(); }
    };
    toggle.addEventListener("click", function () { setPanel(!panel.classList.contains("is-open")); });
    if (closeBtn) closeBtn.addEventListener("click", function () { setPanel(false); });

    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var textarea = form.querySelector("textarea");
        var context = document.body.dataset.waContext || "";
        var msg = (textarea.value || "").trim();
        var full = context ? (msg ? context + "\n" + msg : context) : msg;
        window.open(window.waLink(full || undefined), "_blank", "noopener");
        textarea.value = "";
        setPanel(false);
      });
    }
  }

  /* every [data-wa] link opens WhatsApp with optional data-wa-message */
  document.querySelectorAll("[data-wa]").forEach(function (el) {
    el.addEventListener("click", function (e) {
      e.preventDefault();
      var msg = el.dataset.waMessage || document.body.dataset.waContext || undefined;
      window.open(window.waLink(msg), "_blank", "noopener");
    });
  });

  /* ---------- FAQ accordion ---------- */
  document.querySelectorAll(".faq-q").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var item = btn.closest(".faq-item");
      var open = item.classList.contains("is-open");
      item.classList.toggle("is-open", !open);
      btn.setAttribute("aria-expanded", String(!open));
    });
  });

  /* ---------- scroll reveal ---------- */
  var faders = document.querySelectorAll(".scroll-fade");
  if (faders.length && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    faders.forEach(function (el) { io.observe(el); });
  } else {
    faders.forEach(function (el) { el.classList.add("is-in"); });
  }

  /* ---------- hero search → properties page ---------- */
  var heroForm = document.getElementById("hero-search");
  if (heroForm) {
    heroForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var params = new URLSearchParams();
      new FormData(heroForm).forEach(function (value, key) {
        if (value) params.set(key, value);
      });
      var q = params.toString();
      window.location.href = "properties.html" + (q ? "?" + q : "");
    });
  }

  /* ---------- contact form → WhatsApp ---------- */
  var contactForm = document.getElementById("contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var d = new FormData(contactForm);
      var lines = lang === "ar"
        ? ["استفسار جديد من الموقع",
           "الاسم: " + (d.get("name") || "-"),
           "الموبايل: " + (d.get("phone") || "-"),
           "البريد: " + (d.get("email") || "-"),
           "مهتم بـ: " + (d.get("interest") || "-"),
           "الرسالة: " + (d.get("message") || "-")]
        : ["New enquiry from the website",
           "Name: " + (d.get("name") || "-"),
           "Phone: " + (d.get("phone") || "-"),
           "Email: " + (d.get("email") || "-"),
           "Interested in: " + (d.get("interest") || "-"),
           "Message: " + (d.get("message") || "-")];
      window.open(window.waLink(lines.join("\n")), "_blank", "noopener");
    });
  }

  /* ---------- newsletter ---------- */
  var news = document.getElementById("newsletter-form");
  if (news) {
    news.addEventListener("submit", function (e) {
      e.preventDefault();
      var email = news.querySelector("input").value.trim();
      if (!email) return;
      var msg = lang === "ar"
        ? "عايز أشترك في النشرة البريدية: " + email
        : "Please subscribe me to the newsletter: " + email;
      window.open(window.waLink(msg), "_blank", "noopener");
      news.reset();
    });
  }

  /* ---------- footer year ---------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });

  /* ---------- project tiles carousel (home) ---------- */
  var tiles = document.querySelector("[data-carousel]");
  if (tiles) {
    var step = function (dir) {
      var amount = tiles.clientWidth * 0.6 * dir;
      tiles.scrollBy({ left: html.dir === "rtl" ? -amount : amount, behavior: "smooth" });
    };
    document.querySelectorAll("[data-carousel-prev]").forEach(function (b) {
      b.addEventListener("click", function () { step(-1); });
    });
    document.querySelectorAll("[data-carousel-next]").forEach(function (b) {
      b.addEventListener("click", function () { step(1); });
    });
  }

  /* expose helpers for other scripts */
  window.ELITE = { lang: lang, base: base };
})();
