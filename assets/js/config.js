/* ==========================================================================
   Elite Real Estate — site configuration
   Change contact details here once; every page picks them up.
   ========================================================================== */
window.ELITE_CONFIG = {
  /* WhatsApp: local number and international format (no +, no spaces) */
  phoneLocal: "01111788812",
  phoneIntl: "201111788812",
  phoneDisplay: "+20 111 178 8812",

  email: "info@eliterealestateco.com",
  address: {
    ar: "123 شارع الكورنيش، الإسكندرية، مصر",
    en: "123 El Corniche St., Alexandria, Egypt"
  },

  social: {
    facebook: "https://facebook.com/",
    instagram: "https://instagram.com/",
    linkedin: "https://linkedin.com/",
    youtube: "https://youtube.com/"
  },

  /* Production domain — used for canonical URLs and structured data */
  siteUrl: "https://www.eliterealestateco.com",

  /* Default WhatsApp opening message per language */
  waIntro: {
    ar: "السلام عليكم، أنا مهتم بمعرفة تفاصيل أكتر عن الوحدات المتاحة.",
    en: "Hello, I'd like to know more about the available properties."
  }
};

window.waLink = function (message) {
  var c = window.ELITE_CONFIG;
  var lang = document.documentElement.lang === "ar" ? "ar" : "en";
  var text = message || c.waIntro[lang];
  return "https://wa.me/" + c.phoneIntl + "?text=" + encodeURIComponent(text);
};
