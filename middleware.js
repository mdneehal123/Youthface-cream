// TEMPORARY PAUSE (owner asked 22 Nov 2026). Every page shows a "back soon" page with HTTP 503 + Retry-After,
// which tells Google the site is only paused (rankings are kept). New orders are blocked; payment
// confirmation/webhook endpoints keep working for orders already placed.
// TO REOPEN THE SITE: delete this file (middleware.js), commit and push.
const KEEP = /^\/api\/(razorpay-webhook|verify-payment|verify|track)(\/|$)/;
const HTML = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Youth Face · Back soon</title><meta name="robots" content="noarchive"><style>
body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#fbf7f4;color:#2b2b2b}
.c{max-width:440px;padding:32px 24px;text-align:center}h1{font-size:28px;margin:0 0 12px}p{font-size:16px;line-height:1.55;color:#555;margin:0 0 20px}
a{display:inline-block;background:#25D366;color:#fff;text-decoration:none;font-weight:700;padding:14px 22px;border-radius:999px}</style></head>
<body><main class="c"><h1>We'll be back soon</h1><p>Our website is taking a short break. For orders or questions, message us on WhatsApp and we'll help you right away.</p>
<a href="https://wa.me/919980881230">Chat on WhatsApp</a></main></body></html>`;
export const config = { matcher: "/:path*" };
export default function middleware(req) {
  const p = new URL(req.url).pathname;
  if (KEEP.test(p)) return; // let existing payments finish
  if (p.startsWith("/api/")) return new Response(JSON.stringify({ ok: false, error: "The store is temporarily closed. Please message us on WhatsApp." }), { status: 503, headers: { "content-type": "application/json", "retry-after": "86400", "cache-control": "no-store" } });
  return new Response(HTML, { status: 503, headers: { "content-type": "text/html; charset=utf-8", "retry-after": "86400", "cache-control": "no-store" } });
}
