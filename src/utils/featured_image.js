// Featured image — LOCAL per-service images from /images/blog/ (imageartikel/).
//
// Setiap layanan punya gambar sendiri (16:9, webp, ~100KB). Dipilih berdasarkan
// `post.service`, lalu infer dari title/slug bila field kosong, lalu fallback.
// Hash-based: same service → same image (konsisten + browser cache friendly).
//
// Fallback chain:
//   1. post.featuredImage (explicit override)
//   2. service image (this file) — by post.service or inferred from title
//   3. default digital-marketing image

const IMG_BASE = "/images/blog/";
const IMG_EXT = ".webp";

// Service → local image file (from imageartikel/)
const SERVICE_IMAGES = {
    "jasa-iklan-facebook": "jasafacebookads",
    "jasa-iklan-instagram": "jasainstagramads",
    "jasa-iklan-tiktok": "jasatiktokads",
    "jasa-iklan-google": "jasagoogleads",
    "jasa-iklan-youtube": "jasayoutubeads",
    "jasa-digital-marketing": "jasadigitalmarketing1",
    "jasa-pembuatan-website": "jasapembuatanwebsite",
    "jasa-pembuatan-landing-page": "jasapembuatanwebsite",
    "jasa-kelola-instagram": "jasainstagramads",
    "jasa-kelola-tiktok": "jasatiktokads",
    "jasa-view-live": "jasaviewlivetiktok",
    "jasa-view-live-tiktok": "jasaviewlivetiktok",
    "jasa-view-live-youtube": "jasaviewliveyoutube",
    "jasa-view-live-instagram": "jasaviewliveinstagram",
    "jasa-view-live-shopee": "jasaviewliveshopee",
    "jasa-view-live-twitch": "jasaviewlivetwitch",
    "jasa-buzzer": "jasaviewlivetiktok",
    "jasa-buzzer-tiktok": "jasaviewlivetiktok",
    "jasa-buzzer-youtube": "jasaviewliveyoutube",
    "jasa-buzzer-instagram": "jasaviewliveinstagram",
    "jasa-buzzer-shopee": "jasaviewliveshopee",
    "jasa-buzzer-twitch": "jasaviewlivetwitch",
    "jasa-viewers-youtube": "jasaviewliveyoutube",
    "jasa-viewers-instagram": "jasaviewliveinstagram",
    "jasa-viewers-shopee": "jasaviewliveshopee",
    "jasa-viewers-tiktok": "jasaviewlivetiktok",
    "jasa-viewers-twitch": "jasaviewlivetwitch",
};

const DEFAULT_IMG = "jasadigitalmarketing1";

// Infer service from title/slug (untuk post lama tanpa field service)
function inferServiceFromTitle(title) {
    const t = (title || "").toLowerCase();
    // Urutan paling spesifik → umum. Generic "ads" rule dihapus (terlalu greedy).
    const rules = [
        ["landing page", "jasa-pembuatan-landing-page"],
        ["pembuatan website", "jasa-pembuatan-website"],
        ["jasa website", "jasa-pembuatan-website"],
        ["jasa buat website", "jasa-pembuatan-website"],
        ["kelola instagram", "jasa-kelola-instagram"],
        ["kelola tiktok", "jasa-kelola-tiktok"],
        ["view live", "jasa-view-live"],
        ["live streaming", "jasa-view-live"],
        ["jasa live", "jasa-view-live"],
        ["viewers", "jasa-view-live"],
        ["jasa iklan facebook", "jasa-iklan-facebook"],
        ["facebook ads", "jasa-iklan-facebook"],
        ["iklan facebook", "jasa-iklan-facebook"],
        ["jasa iklan instagram", "jasa-iklan-instagram"],
        ["instagram ads", "jasa-iklan-instagram"],
        ["iklan instagram", "jasa-iklan-instagram"],
        ["jasa iklan tiktok", "jasa-iklan-tiktok"],
        ["tiktok ads", "jasa-iklan-tiktok"],
        ["iklan tiktok", "jasa-iklan-tiktok"],
        ["jasa iklan youtube", "jasa-iklan-youtube"],
        ["youtube ads", "jasa-iklan-youtube"],
        ["iklan youtube", "jasa-iklan-youtube"],
        ["jasa iklan google", "jasa-iklan-google"],
        ["google ads", "jasa-iklan-google"],
        ["iklan google", "jasa-iklan-google"],
        ["adwords", "jasa-iklan-google"],
        ["facebook", "jasa-iklan-facebook"],
        ["tiktok", "jasa-iklan-tiktok"],
        ["instagram", "jasa-iklan-instagram"],
        ["youtube", "jasa-iklan-youtube"],
        ["google", "jasa-iklan-google"],
        ["shopee", "jasa-view-live"],
        ["digital marketing", "jasa-digital-marketing"],
    ];
    for (const [kw, svc] of rules) if (t.includes(kw)) return svc;
    return "";
}

// For jasa-view-live: platform-specific image based on title/slug keyword
function viewLiveImage(title, slug) {
    const t = ((title || "") + " " + (slug || "")).toLowerCase();
    if (t.includes("youtube")) return "jasaviewliveyoutube";
    if (t.includes("instagram")) return "jasaviewliveinstagram";
    if (t.includes("shopee")) return "jasaviewliveshopee";
    if (t.includes("twitch")) return "jasaviewlivetwitch";
    if (t.includes("tiktok")) return "jasaviewlivetiktok";
    return "jasaviewlivetiktok";
}

// Simple string hash (deterministic)
function hashStr(s) {
    let h = 0;
    for (let i = 0; i < s.length; i++) {
        h = ((h << 5) - h) + s.charCodeAt(i);
        h |= 0;
    }
    return Math.abs(h);
}

function imageUrl(name) {
    return IMG_BASE + name + IMG_EXT;
}

export function getFeaturedImage(post) {
    // 1. Explicit override
    if (post && post.featuredImage) return post.featuredImage;
    // 2. Service-based local image. Infer dari title lebih spesifik dari service field
    //    yang kadang salah di artikel lama (mis. svc='jasa-iklan-tiktok' tapi title
    //    jelas-jelas "Jasa Pembuatan Landing Page").
    const SPECIFICITY = {
        "jasa-pembuatan-landing-page": 5,
        "jasa-pembuatan-website": 4,
        "jasa-iklan-facebook": 3,
        "jasa-iklan-google": 3,
        "jasa-iklan-tiktok": 3,
        "jasa-iklan-instagram": 3,
        "jasa-iklan-youtube": 3,
        "jasa-kelola-instagram": 2,
        "jasa-kelola-tiktok": 2,
        "jasa-digital-marketing": 1,
        "jasa-view-live": 0,
    };
    let svc = (post?.service || "").toLowerCase();
    const inferred = inferServiceFromTitle(post?.title);
    if (!svc || svc === "jasa-digital-marketing") {
        svc = inferred || svc;
    } else if (inferred && (SPECIFICITY[inferred] || 0) > (SPECIFICITY[svc] || 0)) {
        svc = inferred;
    }
    let name = "";
    if (svc === "jasa-view-live") {
        name = viewLiveImage(post?.title, post?.slug);
    } else if (SERVICE_IMAGES[svc]) {
        name = SERVICE_IMAGES[svc];
    } else {
        // kategori tanpa service → hash ke salah satu gambar digital marketing
        const alt = [SERVICE_IMAGES["jasa-digital-marketing"], SERVICE_IMAGES["jasa-pembuatan-website"]];
        name = alt[hashStr(post?.slug || "x") % alt.length];
    }
    return imageUrl(name);
}

// Thumbnail untuk related posts (pakai gambar service yang sama, kecil)
export function getRelatedImages(post, count = 3) {
    const cat = post?.category || "strategy";
    let svc = (post?.service || "").toLowerCase();
    const inferred = inferServiceFromTitle(post?.title);
    if (!svc || svc === "jasa-digital-marketing") svc = inferred || svc;
    const poolKeys = Object.keys(SERVICE_IMAGES);
    const start = hashStr(post?.slug || "x") % poolKeys.length;
    return Array.from({ length: count }, (_, i) => {
        const key = poolKeys[(start + i) % poolKeys.length];
        const name = SERVICE_IMAGES[key] || DEFAULT_IMG;
        return imageUrl(name);
    });
}

// Hero image with fallback (untuk <img onerror> pattern)
export function getFeaturedImageWithFallback(post) {
    return { primary: getFeaturedImage(post), fallback: imageUrl(DEFAULT_IMG) };
}

export const UNSPLASH_POOL = null;
export const SERVICE_IMAGE_MAP = SERVICE_IMAGES;
export const picsumFor = () => imageUrl(DEFAULT_IMG);
export const svgPlaceholderFor = () => imageUrl(DEFAULT_IMG);
