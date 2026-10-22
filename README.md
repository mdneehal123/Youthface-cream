# Youth Face — website

Static site for youthfacebeauty.com, ready for GitHub + Vercel. Every old WordPress URL (4 products, 25 blog posts, all pages) is at the same address, plus 12 Kerala delivery pages, with SEO titles, canonicals, schema, `sitemap.xml`, `robots.txt` and `llms.txt`.

## 1. Before going live — switch these on
All store settings are in `_source/index.html` → `const CONFIG` (top of the script). Fill these in, then rebuild (step 4) — or send the values to Claude.

| Setting | What it does |
|---|---|
| `paymentLink` | Razorpay / Cashfree payment page URL. Shows a "Pay now" button after online orders. Empty = we send a payment link on WhatsApp. |
| `upiId` | e.g. `youthface@okaxis`. Shows a "Pay by UPI" button after online orders. |
| `orderWebhook` | Saves every order to a Google Sheet (see step 2). Strongly recommended. |
| `ga4Id` / `metaPixelId` | Google Analytics and Meta Pixel. Tracks page views, add to cart, checkout and orders. |
| `grievanceOfficer`, `manufacturer`, `countryOfOrigin` | Shown in the footer and on product pages when filled. |
| `deliveryDays` | e.g. `{metro:[2,4], other:[4,7]}`. When filled, the pin-code checker shows delivery dates. Empty = no dates promised. |
| `codFee`, `prepaidDiscountPct`, `coupons`, `rewards` | Offers. Currently: no COD charge, 5% off online, WELCOME10, GLOW100, ₹50 off at ₹999, ₹150 off at ₹1,444. |

## Online payment (Razorpay)
Server code in `api/` creates Razorpay orders (amount calculated on the server) and verifies every payment signature.
To switch it on: Vercel → Settings → Environment Variables → add `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET` (Production) → Redeploy.
Prices for online payment live in `api/_pricing.js` — keep them the same as `PRODUCTS`/`CONFIG` in `_source/index.html`.

## COD → Delhivery, paid orders → Order Desk
- **COD:** `api/cod-order` checks the pin code with Delhivery, then books the shipment and shows the customer the AWB.
  Vercel env: `DELHIVERY_TOKEN`, `DELHIVERY_PICKUP` (warehouse name exactly as in Delhivery), optional `DELHIVERY_GRAMS_PER_JAR` (default 100), `DELHIVERY_MODE` (Surface/Express).
- **Paid online:** after Razorpay verification the order goes to the Order Desk inbox, marked Paid.
  Vercel env: `WEB_ORDER_KEY` (same long random value as in the Order Desk project), optional `ORDERDESK_URL` (default https://www.skinday.shop).
- **Checkout leads:** if a shopper ticks the WhatsApp consent box at checkout, `api/lead` sends their name, mobile number and cart to the Order Desk (same `WEB_ORDER_KEY`) so the owner can message them on WhatsApp later. Nothing is sent unless the box is ticked.
- Vercel Hobby allows 12 functions; `api/` now has 6 (`cod-order`, `create-order`, `delhivery-check`, `lead`, `payment-config`, `verify-payment`) — files starting with `_` are helpers, not functions.
- If Delhivery can't book a COD order, it goes to the Order Desk with a warning so it is never lost.

## 2. Order backup to Google Sheet (5 minutes)
1. Create a Google Sheet called "Youth Face Orders".
2. Extensions → Apps Script → paste `_source/google-sheet-orders.gs` → Save.
3. Deploy → New deployment → Web app → Execute as **Me**, access **Anyone** → Deploy.
4. Put the Web app URL in `CONFIG.orderWebhook` and rebuild.

## 3. Photos
All photos live in WordPress under `/wp-content/uploads/`. Before moving the domain, either:
- download that folder from your hosting and add it to this repo as `wp-content/uploads/...`, or
- keep WordPress running at `old.youthfacebeauty.com` (`vercel.json` already forwards `/wp-content/*` there).

## 4. Deploy / rebuild
1. Upload everything in this folder to a GitHub repo.
2. Vercel → Add New → Project → import the repo → Framework preset: **Other** → Deploy.
3. Vercel → Settings → Domains → add `youthfacebeauty.com` and `www.youthfacebeauty.com`, update DNS. Keep existing TXT records (Google verification).
4. After editing `_source`, run `python3 _source/build.py` (needs `pip install beautifulsoup4`) and copy `_source/dist/*` to the repo root.

## 5. Launch day
- Test on your phone: a COD order, an online order, a coupon, the pin-code checker, a blog post, a Kerala page.
- Google Search Console → submit `https://youthfacebeauty.com/sitemap.xml` → Request indexing for home, products and Kerala pages.
- Export your WooCommerce orders and keep WordPress (with a full backup) for at least a month.
