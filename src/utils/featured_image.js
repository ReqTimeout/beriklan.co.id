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
    "jasa-iklan-facebook": "jasafacebokads",
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
    const rules = [
        ["facebook", "jasa-iklan-facebook"],
        ["instagram", "jasa-iklan-instagram"],
        ["tiktok", "jasa-iklan-tiktok"],
        ["google", "jasa-iklan-google"],
        ["youtube", "jasa-iklan-youtube"],
        ["website", "jasa-pembuatan-website"],
        ["landing page", "jasa-pembuatan-landing-page"],
        ["kelola instagram", "jasa-kelola-instagram"],
        ["kelola tiktok", "jasa-kelola-tiktok"],
        ["digital marketing", "jasa-digital-marketing"],
        ["view live", "jasa-view-live"],
        ["viewers", "jasa-view-live"],
        ["shopee", "jasa-view-live"],
        ["ads", "jasa-iklan-google"],
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
    // 2. Service-based local image. Service default 'jasa-digital-marketing' sering
    //    dipakai sebagai fallback saat generate — coba infer dari title dulu biar
    //    shopee/tiktok/google dll dapat gambar yang sesuai konten.
    let svc = (post?.service || "").toLowerCase();
    const inferred = inferServiceFromTitle(post?.title);
    if (!svc || svc === "jasa-digital-marketing") svc = inferred || svc;
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
