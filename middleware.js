// TEMPORARY PAUSE (owner asked 22 Nov 2026). Every page shows a "back soon" page with HTTP 503 + Retry-After,
// which tells Google the site is only paused (rankings are kept). New orders are blocked; payment
// confirmation/webhook endpoints keep working for orders already placed.
// TO REOPEN THE SITE: delete this file (middleware.js), commit and push.
const KEEP = /^\/api\/(razorpay-webhook|verify-payment|verify|track)(\/|$)/;
const HTML = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>503 Service Unavailable</title><meta name="robots" content="noarchive"><style>
body{margin:0;min-height:100vh;display:grid;place-items:center;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:#fff;color:#222}
.c{text-align:center;padding:24px}.code{font-size:96px;font-weight:800;letter-spacing:2px;color:#d93025;margin:0}
h1{font-size:22px;font-weight:600;margin:8px 0 10px}p{color:#666;margin:0 0 6px;font-size:15px}hr{border:0;border-top:1px solid #e5e5e5;margin:22px auto;width:220px}
small{color:#999;font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px}</style></head>
<body><main class="c"><p class="code">503</p><h1>Service Temporarily Unavailable</h1><p>The server is temporarily unable to handle your request.</p><p>Please try again later.</p><hr><small>Error code: 503 · SERVICE_UNAVAILABLE</small></main></body></html>`;
export const config = { matcher: "/:path*" };
export default function middleware(req) {
  const p = new URL(req.url).pathname;
  if (KEEP.test(p)) return; // let existing payments finish
  if (p.startsWith("/api/")) return new Response(JSON.stringify({ ok: false, error: "The store is temporarily closed. Please check back soon." }), { status: 503, headers: { "content-type": "application/json", "retry-after": "86400", "cache-control": "no-store" } });
  return new Response(HTML, { status: 503, headers: { "content-type": "text/html; charset=utf-8", "retry-after": "86400", "cache-control": "no-store" } });
}
