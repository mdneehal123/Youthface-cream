#!/usr/bin/env python3
"""Build the Youth Face static site (dist/) for GitHub + Vercel.

- Store views (home, shop, products, checkout) at the same URLs as the old WordPress site
- Every WordPress article and page re-created at its old URL, cleaned into the new design
- Rank Math titles/descriptions, canonicals, Open Graph, JSON-LD, sitemap.xml, robots.txt, redirects
"""
import json, glob, os, re, html, shutil, datetime
from bs4 import BeautifulSoup, Comment
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kerala

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_APP = os.path.join(ROOT, "index.html")
CONTENT = os.path.join(ROOT, "content")
DIST = os.path.join(ROOT, "dist")
SITE = "https://www.youthfacebeauty.com"
GSV = "CUCKzAwX0QpgN9ntR1HKxMjwp7u0wgm0n50vmqDsHRk"
INDEXNOW_KEY = "7c1f4e9a2b8d4f6e9a3c5b7d1e2f4a6c"
UP = "/wp-content/uploads/2026/09/"
OG_DEFAULT = SITE + UP + "Youth-Face-Beauty-Cream-25g.png"
ICON = "/favicon.svg"
AUTHOR = "Mohammed Nihal"

# Rank Math canonical / robots settings found on the old site
CANONICAL_OVERRIDE = {
    "/youth-face-cream-ingredients-list-full-breakdown/": "/youth-face-cream-ingredients/",
    "/kojic-acid-dark-spots-guide/": "/kojic-acid-for-dark-spots-how-it-works-how-to-use-it-what-to-know/",
    "/understanding-kojic-acid-and-alpha-arbutin/": "/kojic-acid-and-alpha-arbutin-benefits-how-to-use-skincare-guide/",
    "/how-to-find-original-youth-face-cream/": "/where-to-buy-original-youth-face-cream-avoiding-fakes/",
    "/is-youth-face-cream-good-or-bad/": "/is-youth-face-cream-good-for-skin/",
}
NOINDEX = {"/youth-face-cream-ingredients-list-full-breakdown/", "/checkout/", "/order-success/", "/wishlist/", "/track-order/"}

PRODUCT_ROUTES = {
    "/product/youth-face-beauty-cream-25g/": "cream-1",
    "/product/youth-face-beauty-cream-pack-of-2/": "cream-2",
    "/product/youth-face-beauty-cream-pack-of-3/": "cream-3",
    "/product/youth-face-body-lotion/": "lotion",
}
ADD_TO_CART = {"22": "/product/youth-face-beauty-cream-25g/", "159": "/product/youth-face-beauty-cream-pack-of-2/",
               "160": "/product/youth-face-beauty-cream-pack-of-3/", "330": "/product/youth-face-body-lotion/"}
HOW_ORDERS_WORK = (
    '<h2>How ordering works on this website</h2>'
    '<p>When you place an order, the details you enter at checkout (name, phone number, email if given, delivery address, items and payment choice) are prepared as a message that you send to us on WhatsApp at +91 99808 81230. '
    'We use these details to confirm, pack, ship and support your order. If you choose to pay online, we send you a secure payment link from our payment partner. We do not see or store your card or UPI PIN.</p>'
    '<p>We may also keep a record of each order in a private order sheet so that no order is missed. Only Youth Face staff can access it.</p>'
    '<h2>Information stored in your browser</h2>'
    '<p>Our website saves your cart, wishlist and checkout details in your own browser (local storage) so you don\'t lose them if you leave the page. This information stays on your device. You can clear it at any time by clearing your browser data.</p>'
    '<h2>Analytics</h2><p>We may use tools such as Google Analytics and the Meta Pixel to understand how visitors use our website, for example which pages are viewed and when an order is placed. These tools may use cookies. You can block cookies in your browser settings.</p>')
GRIEVANCE_HTML = lambda: (
    '<h2>Grievance redressal</h2><p>If you have a complaint about a product, order, payment or this website, contact us and we will acknowledge it within 48 hours and work to resolve it as quickly as possible.</p>'
    '<ul><li><b>Seller:</b> Beauty Mart, Azad Nagar, 4th Cross, Bhatkal, Karnataka, India</li>'
    + (f'<li><b>Grievance officer:</b> {html.escape(APPCFG["grievanceOfficer"])}</li>' if APPCFG["grievanceOfficer"] else "")
    + '<li><b>Phone / WhatsApp:</b> +91 99808 81230</li><li><b>Email:</b> mdneehal@gmail.com</li></ul>')
def _subs(h, pairs):
    for a, b in pairs:
        h = re.sub(a, b, h)
    return h


POLICY_FIX = {
    "/privacy-policy/": lambda h: h + HOW_ORDERS_WORK + GRIEVANCE_HTML(),
    "/terms-conditions/": lambda h: h + (
        '<h2>Placing an order</h2><p>Orders are placed by completing checkout on this website and sending the order details to us on WhatsApp. '
        'An order is confirmed when we reply on WhatsApp. For online payment, we send a secure payment link and dispatch the order after payment is received. '
        'For Cash on Delivery, please pay the courier the amount shown at checkout.</p>') + GRIEVANCE_HTML(),
    "/security/": lambda h: _subs(h, [
        (r"transactions are processed through Razorpay using its payment infrastructure\.", "online payments are made through a secure payment link that we send you on WhatsApp from our verified number +91 99808 81230."),
        (r"Please complete payments only through our official website checkout\.", "Only pay through links sent from this number or shown on this website."),
        (r"Make payments only through the official Youth Face website checkout\.", "Place orders only on youthfacebeauty.com or our verified WhatsApp number, and pay only through links we send from that number."),
        (r"Payment details are entered through the Razorpay payment flow\.", "Card and UPI details are entered on our payment partner's secure page, never on WhatsApp."),
        (r"Our checkout uses Razorpay and supports the payment methods shown below\.", "You can pay by Cash on Delivery, or online through our payment partner using the methods below."),
        (r"Razorpay", "our payment partner")]),
    "/shipping-delivery/": lambda h: h.replace("Please use the estimated delivery date shown at checkout or in your order confirmation where available.",
                                              "Message us on WhatsApp at +91 99808 81230 with your pin code for a delivery estimate. We share tracking details on WhatsApp after dispatch."),
    "/contact/": lambda h: h + GRIEVANCE_HTML(),
}

# Pages already rebuilt inside the store app — not generated as article pages
APP_PAGES = {"/", "/shop/"}
GUIDE_PAGES = ["/youth-face-beauty-cream/", "/youth-face-cream-price-in-india/", "/youth-face-cream-results-how-long-does-it-take/",
               "/youth-face-cream-skin-types-who-can-use-it/", "/youth-face-cream-ingredients/", "/is-youth-face-cream-good-for-skin/",
               "/how-to-apply-youth-face-cream/", "/youth-face-beauty-cream-benefits/", "/who-is-the-owner-of-youth-face-cream/",
               "/kojic-acid-and-alpha-arbutin-benefits-how-to-use-skincare-guide/", "/youth-face-cream-bhatkal-karnataka/",
               "/is-youth-face-cream-good-or-bad/", "/how-to-find-original-youth-face-cream/"]
HELP_PAGES = ["/how-to-use/", "/faq/", "/track-order/", "/contact/", "/about-us/", "/about-the-author/", "/editorial-policy/", "/security/"]
POLICY_PAGES = ["/shipping-delivery/", "/refund-returns-policy/", "/privacy-policy/", "/terms-conditions/"]

esc = lambda s: html.escape(s or "", quote=True)


def load():
    items = {}
    for f in glob.glob(os.path.join(CONTENT, "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        d["title"] = html.unescape(d["title"])
        items[d["path"]] = d
    return items


def strip_site(title):
    return re.sub(r"\s*[|–-]\s*Youth Face\s*$", "", title).strip()


def fix_url(u):
    if not u:
        return u
    u = u.strip()
    m = re.search(r"[?&]add-to-cart=(\d+)", u)
    if m and m.group(1) in ADD_TO_CART:
        return ADD_TO_CART[m.group(1)]
    u = re.sub(r"^https?://(www\.)?youthfacebeauty\.com", "", u)
    if u == "":
        u = "/"
    if u in ("/cart/", "/cart"):
        return "/checkout/"
    if u in ("/my-account/", "/my-account"):
        return "/track-order/"
    return u


def clean(content):
    """Turn Gutenberg/theme HTML into clean semantic HTML. Returns (html, first_h1, ld_json_list)."""
    content = re.sub(r"\[/?woocommerce[^\]]*\]", "", content)
    soup = BeautifulSoup(content, "html.parser")
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        c.extract()
    ld = []
    for sc in soup.find_all("script"):
        if (sc.get("type") or "") == "application/ld+json":
            try:
                ld.append(json.loads(sc.string or ""))
            except Exception:
                pass
        sc.decompose()
    # accordion/FAQ triggers carry the question text: keep them as headings
    for b in soup.find_all("button"):
        cls = " ".join(b.get("class") or [])
        txt = b.get_text(" ", strip=True)
        if ("accordion" in cls or "toggle" in cls) and txt and txt not in "+−-":
            b.name = "h3"
            b.attrs = {}
            for sv in b.find_all("svg"):
                sv.decompose()
    for t in soup.find_all(["style", "svg", "noscript", "form", "input", "button", "iframe", "select", "textarea", "label"]):
        t.decompose()
    first_h1 = None
    for h in soup.find_all("h1"):
        if first_h1 is None:
            first_h1 = h.get_text(" ", strip=True)
            h.decompose()
        else:
            h.name = "h2"
    for h in soup.find_all("h6"):
        h.name = "p"
        h.attrs = {"class": ["kicker"]}
    for h in soup.find_all("h5"):
        h.name = "h4"
    for t in soup.find_all(["div", "section", "span", "main", "article", "header", "footer", "font", "center", "nav", "aside"]):
        t.unwrap()
    keep = {"a": {"href"}, "img": {"src", "alt", "width", "height"}, "td": {"colspan", "rowspan"},
            "th": {"colspan", "rowspan"}, "details": {"open"}}
    for t in soup.find_all(True):
        if t.name == "p" and t.get("class") == ["kicker"]:
            continue
        style = t.get("style", "")
        allowed = keep.get(t.name, set())
        t.attrs = {k: v for k, v in t.attrs.items() if k in allowed}
        if t.name == "a":
            t["href"] = fix_url(t.get("href", ""))
            if "background" in style:
                t["class"] = ["cta"]
            if t["href"].startswith("http"):
                t["target"] = "_blank"
                t["rel"] = "noopener"
        if t.name == "img":
            t["src"] = fix_url(t.get("src", ""))
            t["loading"] = "lazy"
            t["decoding"] = "async"
    for a in soup.find_all("a", href=re.compile(r"^#yfb")):
        a.decompose()
    for tb in soup.find_all("table"):
        wrap = soup.new_tag("div")
        wrap["class"] = ["tbl"]
        tb.wrap(wrap)
    # drop empties
    changed = True
    while changed:
        changed = False
        for t in soup.find_all(["p", "li", "h2", "h3", "h4", "strong", "em", "ul", "ol", "figure", "blockquote", "a"]):
            if not t.get_text(strip=True) and not t.find("img"):
                t.decompose()
                changed = True
    # a leading kicker just repeats the page eyebrow
    first = next((c for c in soup.contents if getattr(c, "name", None)), None)
    if first is not None and first.name == "p" and first.get("class") == ["kicker"]:
        first.decompose()
    out = str(soup)
    out = re.sub(r"\n\s*\n+", "\n", out).strip()
    return out, first_h1, ld


def fmt_date(s):
    try:
        return datetime.datetime.strptime(s[:10], "%Y-%m-%d").strftime("%d %b %Y").lstrip("0")
    except Exception:
        return ""


def iso(s):
    try:
        return datetime.datetime.strptime(s[:19], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S+05:30")
    except Exception:
        return s


# ---------------------------------------------------------------- app pieces
APP = open(SRC_APP, encoding="utf-8").read()


def _cfg(key):
    m = re.search(r'\n  ' + key + r': "([^"]*)"', APP)
    return m.group(1) if m else ""


APPCFG = {k: _cfg(k) for k in ("ga4Id", "metaPixelId", "grievanceOfficer", "manufacturer", "countryOfOrigin")}
STYLE = re.search(r"<style>.*?</style>", APP, re.S).group(0)
APP_BODY = APP[APP.index('<div class="ticker"'):]
APP_BODY = APP_BODY.replace('const IMG = "https://youthfacebeauty.com/wp-content/uploads/2026/09/";', 'const IMG = "/wp-content/uploads/2026/09/";')
FONTS_URL = "https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=optional"
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         f'<link rel="preload" as="style" href="{FONTS_URL}" onload="this.onload=null;this.rel=\'stylesheet\'"><noscript><link rel="stylesheet" href="{FONTS_URL}"></noscript>')


def head(title, desc, path, *, canonical=None, robots="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1",
         og_type="website", image=None, ld=None, extra=""):
    canonical = SITE + (canonical or CANONICAL_OVERRIDE.get(path) or path)
    if path in NOINDEX:
        robots = "noindex, follow"
    image = image or OG_DEFAULT
    if image.startswith("/"):
        image = SITE + image
    lds = "".join(f'\n<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in (ld or []))
    return f'''<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{canonical}">
<meta name="google-site-verification" content="{GSV}">
<meta name="theme-color" content="#fbe4e6">
<script>document.documentElement.classList.add("js")</script>
<link rel="icon" href="{ICON}">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:locale" content="en_IN">
<meta property="og:site_name" content="Youth Face">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{image}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{image}">{lds}
{FONTS}
{extra}'''


ORG = {"@context": "https://schema.org", "@type": "Organization", "@id": SITE + "/#organization", "name": "Youth Face",
       "legalName": "Beauty Mart", "url": SITE + "/", "logo": SITE + "/logo.png",
       "address": {"@type": "PostalAddress", "streetAddress": "Azad Nagar, 4th Cross", "addressLocality": "Bhatkal", "addressRegion": "Karnataka", "addressCountry": "IN"},
       "email": "mdneehal@gmail.com", "telephone": "+91-9980881230", "areaServed": {"@type": "Country", "name": "India"},
       "brand": {"@type": "Brand", "name": "Youth Face"},
       "contactPoint": {"@type": "ContactPoint", "telephone": "+91-9980881230", "contactType": "customer service", "areaServed": "IN",
                        "availableLanguage": ["en", "hi"]}}
WEBSITE = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "name": "Youth Face", "url": SITE + "/",
           "publisher": {"@id": SITE + "/#organization"}}


def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(items)]}


WEBP = {os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(ROOT, "static", "wp-content", "uploads", "*", "*", "*.webp"))}


def webp(doc):
    """Serve WebP in <img> tags and app image names; keep PNG/JPG for social previews and schema."""
    def sub(m):
        stem = m.group(2)
        return f'{m.group(1)}{stem}.webp' if stem in WEBP else m.group(0)
    doc = re.sub(r'(src="/wp-content/uploads/\d{4}/\d{2}/)([^"/]+?)\.(?:png|jpe?g)', sub, doc)
    doc = re.sub(r'(IMG\s*\+\s*")([^"]+?)\.(?:png|jpe?g)', sub, doc)
    return doc


def write(path, doc):
    doc = webp(doc)
    out = os.path.join(DIST, path.strip("/"), "index.html") if path != "/" else os.path.join(DIST, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)


# ---------------------------------------------------------------- static page chrome
HEADER = '''<div class="ticker" aria-hidden="true"><div class="ticker-track"><span>FREE SHIPPING ACROSS INDIA</span><span>✦</span><span>CASH ON DELIVERY AVAILABLE</span><span>✦</span><span>EXTRA 5% OFF ON ONLINE PAYMENT</span><span>✦</span><span>100% ORIGINAL YOUTH FACE</span><span>✦</span><span>FREE SHIPPING ACROSS INDIA</span><span>✦</span><span>CASH ON DELIVERY AVAILABLE</span><span>✦</span><span>EXTRA 5% OFF ON ONLINE PAYMENT</span><span>✦</span><span>100% ORIGINAL YOUTH FACE</span><span>✦</span></div></div>
<header class="top"><div class="wrap">
  <a class="logo" href="/">Youth<span>Face</span><small>Beauty Mart</small></a>
  <nav class="main" aria-label="Main"><a href="/shop/">Shop</a><a href="/skincare-guides/">Guides</a><a href="/how-to-use/">How to use</a><a href="/faq/">FAQ</a><a href="/contact/">Contact</a></nav>
  <a class="cart-btn" href="/checkout/" style="text-decoration:none">Cart <b id="cartCount" class="tnum">0</b></a>
</div></header>'''

FOOTER_TPL = '''<footer><div class="wrap">
  <div><div class="logo" style="color:inherit">Youth<span>Face</span></div>
    <p style="opacity:.75;max-width:34ch">Simple everyday skincare with Kojic Acid &amp; Alpha Arbutin. Beauty Mart · Bhatkal, Karnataka, India.</p>
    <p style="opacity:.75;margin:0">WhatsApp: <span style="user-select:all">+91 99808 81230</span></p></div>
  <div><p class="fh">Shop</p><a href="/product/youth-face-beauty-cream-25g/">Beauty Cream 25g</a><a href="/product/youth-face-beauty-cream-pack-of-2/">Pack of 2</a><a href="/product/youth-face-beauty-cream-pack-of-3/">Pack of 3</a><a href="/product/youth-face-body-lotion/">Body Lotion</a></div>
  <div><p class="fh">Help</p><a href="/how-to-use/">How to use</a><a href="/faq/">FAQ</a><a href="/track-order/">Track order</a><a href="/contact/">Contact us</a><a href="/skincare-guides/">Skincare guides</a></div>
  <div><p class="fh">Policies</p><a href="/shipping-delivery/">Shipping &amp; delivery</a><a href="/refund-returns-policy/">Refund &amp; returns</a><a href="/privacy-policy/">Privacy policy</a><a href="/terms-conditions/">Terms &amp; conditions</a><a href="/about-us/">About us</a><a href="/youth-face-cream-kerala/">Delivery in Kerala</a><a href="/sitemap/">Sitemap</a></div>
  <div class="krow"><b>Delivery in Kerala:</b> <a href="/youth-face-cream-kochi/">Kochi</a> · <a href="/youth-face-cream-thiruvananthapuram/">Thiruvananthapuram</a> · <a href="/youth-face-cream-kozhikode/">Kozhikode</a> · <a href="/youth-face-cream-thrissur/">Thrissur</a> · <a href="/youth-face-cream-malappuram/">Malappuram</a> · <a href="/youth-face-cream-kannur/">Kannur</a> · <a href="/youth-face-cream-kasaragod/">Kasaragod</a> · <a href="/youth-face-cream-palakkad/">Palakkad</a> · <a href="/youth-face-cream-kottayam/">Kottayam</a> · <a href="/youth-face-cream-alappuzha/">Alappuzha</a> · <a href="/youth-face-cream-kollam/">Kollam</a></div>
  <div class="copy">© 2026 Youth Face · Sold by Beauty Mart, Azad Nagar, 4th Cross, Bhatkal, Karnataka, India · Customer care &amp; grievances: +91 99808 81230 · mdneehal@gmail.com{GRIEVANCE}</div>
</div></footer>
<a class="wa" href="https://wa.me/919980881230?text=Hi%20Youth%20Face%2C%20I%20need%20help." target="_blank" rel="noopener">WhatsApp us</a>
<script>try{var c=JSON.parse(localStorage.getItem("yf_cart"))||[];document.getElementById("cartCount").textContent=c.reduce(function(a,l){return a+l.qty},0)}catch(e){}</script>'''
FOOTER = FOOTER_TPL.replace("{GRIEVANCE}", (" · Grievance officer: " + html.escape(APPCFG["grievanceOfficer"])) if APPCFG["grievanceOfficer"] else "")
ANALYTICS = ""
if APPCFG["ga4Id"]:
    ANALYTICS += (f'<script async src="https://www.googletagmanager.com/gtag/js?id={APPCFG["ga4Id"]}"></script>'
                  f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{APPCFG["ga4Id"]}");</script>')
if APPCFG["metaPixelId"]:
    ANALYTICS += ('<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version="2.0";n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,"script","https://connect.facebook.net/en_US/fbevents.js");'
                  f'fbq("init","{APPCFG["metaPixelId"]}");fbq("track","PageView");</script>')

ARTICLE_CSS = '''<style>
.article{padding-block:22px 56px}
.article .inner{max-width:760px;margin:0 auto}
.crumbs{font-size:13px;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px}
.crumbs a{text-decoration:none;color:var(--muted)} .crumbs a:hover{color:var(--pink)}
.article h1{font-size:clamp(30px,5vw,46px);font-weight:800;color:var(--head);margin:8px 0 12px}
.byline{font-size:13.5px;color:var(--muted);display:flex;flex-wrap:wrap;gap:6px 14px;margin-bottom:18px}
.byline a{color:var(--ink)}
.hero-img{border-radius:var(--r);overflow:hidden;background:var(--petal);margin-bottom:22px;aspect-ratio:16/9}
.hero-img img{width:100%;height:100%;object-fit:cover}
.prose{font-size:16.5px;line-height:1.75}
.prose > *:first-child{margin-top:0}
.prose h2{font-size:clamp(22px,3vw,28px);margin:34px 0 10px;color:var(--head);line-height:1.2}
.prose h3{font-size:19px;margin:24px 0 8px}
.prose h4{font-size:17px;margin:18px 0 6px}
.prose p,.prose ul,.prose ol,.prose blockquote,.prose details{margin:0 0 14px}
.prose ul,.prose ol{padding-left:22px}
.prose li{margin-bottom:6px}
.prose a{color:var(--pink);text-underline-offset:2px}
.prose a.cta{display:inline-block;background:var(--pink);color:var(--on-pink);padding:11px 22px;border-radius:999px;text-decoration:none;font-weight:700;margin:6px 8px 6px 0}
.prose img{border-radius:12px;margin:10px 0;height:auto}
.prose blockquote{border-left:3px solid var(--gold);padding:4px 0 4px 16px;color:var(--muted)}
.prose .kicker{font-size:12px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--gold);margin:28px 0 -4px}
.prose details{border:1px solid var(--line);border-radius:12px;padding:12px 16px;background:var(--surface)}
.prose summary{font-weight:700;cursor:pointer}
.prose hr{border:0;border-top:1px solid var(--line);margin:28px 0}
.prose .tbl{overflow-x:auto;margin:0 0 16px}
.prose table{border-collapse:collapse;width:100%;font-size:14.5px;min-width:420px}
.prose th,.prose td{border:1px solid var(--line);padding:9px 10px;text-align:left;vertical-align:top}
.prose th{background:var(--petal)}
.buybox{display:grid;grid-template-columns:120px 1fr;gap:16px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:16px;margin:34px 0}
.buybox .pic{aspect-ratio:1/1;border-radius:12px;overflow:hidden;background:var(--petal)}
.buybox .pic img{width:100%;height:100%;object-fit:cover}
.buybox h3{font-size:19px;margin:4px 0 6px}
.buybox .row{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}
.buybox .btn{padding:10px 18px;font-size:14px}
@media (max-width:520px){.buybox{grid-template-columns:1fr}.buybox .pic{max-width:140px}}
.related{margin-top:30px}
.related h2{font-size:22px;color:var(--head);margin-bottom:12px}
.rel-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.gcard{display:flex;flex-direction:column;background:var(--surface);border:1px solid var(--line);border-radius:var(--r);overflow:hidden;text-decoration:none}
.gcard .gimg{aspect-ratio:16/9;background:var(--petal)}
.gcard .gimg img{width:100%;height:100%;object-fit:cover}
.gcard .gb{padding:14px;display:flex;flex-direction:column;gap:6px}
.gcard b{font-family:var(--display);font-size:17px;line-height:1.25}
.gcard small{color:var(--muted);font-size:13px;line-height:1.5}
.gcard:hover b{color:var(--pink)}
.listing h2{font-size:24px;color:var(--head);margin:34px 0 14px}
.linklist{columns:2 260px;gap:24px;padding-left:18px}
.linklist li{margin-bottom:8px;break-inside:avoid}
.linklist a{color:var(--ink)} .linklist a:hover{color:var(--pink)}
.trackbox{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:20px;margin:0 0 20px}
</style>'''

BUYBOX = '''<aside class="buybox" aria-label="Shop Youth Face Beauty Cream">
  <div class="pic"><img src="/wp-content/uploads/2026/09/Youth-Face-Beauty-Cream-25g-600x600.png" alt="Youth Face Beauty Cream 25g jar" width="600" height="600" loading="lazy"></div>
  <div><div class="eyebrow">Official store</div><h3>Youth Face Beauty Cream 25g</h3>
    <div class="price"><span class="now tnum">₹549</span><s class="tnum">₹899</s><span class="off">39% OFF</span></div>
    <div class="per">Kojic Acid &amp; Alpha Arbutin · COD available · Free shipping</div>
    <div class="row"><a class="btn btn-pink" href="/product/youth-face-beauty-cream-25g/">Buy now</a><a class="btn btn-line" href="/shop/">See packs from ₹481/jar</a></div></div>
</aside>'''


def static_page(path, title, desc, body, *, ld=None, og_type="website", image=None, extra_head=""):
    doc = head(title, desc, path, ld=ld, og_type=og_type, image=image,
               extra=extra_head + STYLE + "\n" + ARTICLE_CSS + ANALYTICS)
    doc += "\n</head>\n<body>\n" + HEADER + "\n<main class=\"article\"><div class=\"wrap\"><div class=\"inner\">\n" + body + "\n</div></div></main>\n" + FOOTER + "\n</body>\n</html>\n"
    write(path, doc)


def gcard(d):
    img = fix_url(d.get("featured_image") or "") or (UP + "Youth-Face-Beauty-Cream-skincare-product-for-dark-spot-care-600x600.png")
    ex = html.unescape(re.sub("<[^>]+>", "", d.get("seo_description") or d.get("excerpt") or ""))[:150]
    return f'<a class="gcard" href="{d["path"]}"><div class="gimg"><img src="{esc(img)}" alt="" loading="lazy"></div><div class="gb"><b>{esc(strip_site(d["title"]))}</b><small>{esc(ex)}</small></div></a>'


def main():
    items = load()
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    posts = sorted([d for d in items.values() if d["type"] == "post"], key=lambda d: d["date"], reverse=True)
    sitemap = []  # (url, lastmod)

    # ------------------------------------------------ store app pages
    seo = {}
    home = items["/"]
    seo["home"] = {"title": home["seo_title"], "description": home["seo_description"], "canonical": SITE + "/"}
    shop = items["/shop/"]
    seo["shop"] = {"title": shop["seo_title"], "description": shop["seo_description"], "canonical": SITE + "/shop/"}
    desc_html, product_ld = {}, {}
    for path, pid in PRODUCT_ROUTES.items():
        d = items[path]
        seo["p-" + pid] = {"title": d["seo_title"], "description": d["seo_description"], "canonical": SITE + path}
        h, _, ld = clean(d["content"])
        desc_html[pid] = h
        product_ld[pid] = ld
    seo["checkout"] = {"title": "Checkout | Youth Face", "description": "Secure checkout for Youth Face.", "canonical": SITE + "/checkout/"}
    seo["success"] = {"title": "Order placed | Youth Face", "description": "", "canonical": SITE + "/order-success/"}
    seo["wishlist"] = {"title": "Wishlist | Youth Face", "description": "", "canonical": SITE + "/wishlist/"}
    boot = f'<script>window.YF_PATH_MODE=true;window.YF_SEO={json.dumps(seo, ensure_ascii=False)};</script>'

    price = {"cream-1": (549, 899, "YFB-PACK-1"), "cream-2": (999, 1599, "YFB-PACK-2"), "cream-3": (1444, 1899, "YFB-PACK-3"), "lotion": (599, 599, "YFB-LOTION-40")}
    img = {"cream-1": "Youth-Face-Beauty-Cream-25g-600x600.png", "cream-2": "ChatGPT-Image-Sep-17-2026-08_27_12-PM-600x600.png",
           "cream-3": "Youth-Face-Beauty-Cream-skincare-product-for-dark-spot-care-600x600.png", "lotion": "ChatGPT-Image-Sep-19-2026-01_47_45-AM-600x600.png"}

    DET = json.loads(re.search(r'<script type="application/json" id="yf-details">(.*?)</script>', APP, re.S).group(1).replace("<\\/", "</"))
    PINFO = {"cream-1": ("Youth Face Beauty Cream", 1, "1 × 25g jar"), "cream-2": ("Youth Face Beauty Cream", 2, "2 × 25g jars (50g total)"),
             "cream-3": ("Youth Face Beauty Cream", 3, "3 × 25g jars (75g total)"), "lotion": ("Youth Face Body Lotion", 1, "40 ml")}
    inr = lambda n: "₹" + format(round(n), ",")

    def static_product(pid):
        """Plain HTML copy of the product page for search engines and AI crawlers (the app replaces it on load)."""
        name, units, qty = PINFO[pid]
        pr, mrp, sku = price[pid]
        D = DET["lotion" if pid == "lotion" else "cream"]
        rows = [("Brand", "Youth Face"), ("Product", name), ("Also known as", D["aka"]), ("Net quantity", qty)]
        if D["ingredients"]:
            rows.append(("Key ingredients", " and ".join(i["name"] for i in D["ingredients"]) + " (as listed on the pack)"))
        rows += [("Product type", D["type"]), ("Best for", D["bestFor"]), ("Skin types", D["skinTypes"]), ("When to use", D["when"]),
                 ("Price", inr(pr) + (f" (MRP {inr(mrp)}, {round((1 - pr / mrp) * 100)}% off)" if mrp > pr else ""))]
        if units > 1:
            rows.append(("Price per jar", inr(pr / units)))
        rows += [("Payment", "Cash on Delivery, UPI, cards, net banking"), ("Shipping", "Free shipping across India"),
                 ("Sold and shipped by", "Beauty Mart, Azad Nagar, 4th Cross, Bhatkal, Karnataka, India")]
        if APPCFG.get("manufacturer"):
            rows.append(("Manufactured by", APPCFG["manufacturer"]))
        if APPCFG.get("countryOfOrigin"):
            rows.append(("Country of origin", APPCFG["countryOfOrigin"]))
        rows += [("Customer care", "+91 99808 81230 (WhatsApp & call) · mdneehal@gmail.com"), ("SKU", sku)]
        h = [f'<section class="pdp"><div class="wrap"><div><div class="gallery"><img src="{UP}{img[pid]}" alt="{esc(name)} {esc(qty)}" width="600" height="600" fetchpriority="high"></div></div><div>',
             f'<h1>{esc(name)} – {esc(qty)}</h1><div class="price"><span class="now tnum">{inr(pr)}</span>' + (f'<s>MRP {inr(mrp)}</s>' if mrp > pr else "") + '</div>',
             f'<p>{esc(D["summary"])}</p><p><a class="btn btn-pink" href="/checkout/">Buy now</a></p></div></div></section>',
             '<section class="pinfo"><div class="wrap"><article class="pi-main">',
             f'<h2>About {esc(name)} {esc(qty)}</h2><div class="answer"><b>In short</b><p>{esc(D["summary"])}</p></div>',
             '<h3>Product facts</h3><div class="tbl"><table class="facts"><tbody>' + "".join(f'<tr><th scope="row">{k}</th><td>{esc(v)}</td></tr>' for k, v in rows) + '</tbody></table></div>']
        if D["ingredients"]:
            h.append('<h2>Key ingredients</h2>' + "".join(f'<h3>{esc(i["name"])}</h3><p>{esc(i["text"])} <a href="{i["guide"]}">Read the {esc(i["name"])} guide</a></p>' for i in D["ingredients"]))
        h.append(f'<p class="note">{esc(D["ingredientsNote"])}</p><h2>How to use</h2>' + "".join(f'<h3>{esc(t)}</h3><ol>' + "".join(f'<li>{esc(x)}</li>' for x in st) + '</ol>' for t, st in D["how"].items()))
        if D["who"]:
            h.append('<h2>Who can use it</h2><div class="tbl"><table class="facts"><tbody>' + "".join(f'<tr><th scope="row">{k}</th><td>{esc(v)}</td></tr>' for k, v in D["who"]) + '</tbody></table></div>')
        if D["expect"]:
            h.append(f'<h3>What results to expect</h3><p>{esc(D["expect"])}</p>')
        h.append('<h2>Safety and patch test</h2><ul>' + "".join(f'<li>{esc(x)}</li>' for x in D["safety"]) + '</ul>')
        h.append('<h2>Frequently asked questions</h2>' + "".join(f'<h3>{esc(q)}</h3><p>{esc(a)}</p>' for q, a in D["faqs"]))
        if pid != "lotion":
            h.append('<h2>Compare packs</h2><ul>' + "".join(f'<li><a href="{pp}">Pack of {PINFO[k][1]} ({PINFO[k][2]})</a>: {inr(price[k][0])}, {inr(price[k][0] / PINFO[k][1])} per jar</li>' for pp, k in PRODUCT_ROUTES.items() if k != "lotion") + '</ul>')
        h.append('<h2>Helpful guides</h2><ul>' + "".join(f'<li><a href="{u}">{esc(t)}</a></li>' for t, u in D["guides"]) + '</ul>')
        h.append('</article></div></section>')
        return "".join(h)

    def static_home():
        D = DET["cream"]
        lis = "".join(f'<li><a href="{pp}">{esc(PINFO[k][0])} – {esc(PINFO[k][2])}</a>: {inr(price[k][0])}</li>' for pp, k in PRODUCT_ROUTES.items())
        faqs = "".join(f'<h3>{esc(q)}</h3><p>{esc(a)}</p>' for q, a in D["faqs"][:6])
        return (f'<section class="hero"><div class="wrap"><div><h1>Youth Face Beauty Cream – Kojic Acid &amp; Alpha Arbutin Face Cream</h1><p class="lede">{esc(D["summary"])}</p>'
                f'<p><a class="btn btn-pink" href="/shop/">Shop now</a></p></div></div></section><section class="block"><div class="wrap"><h2>Products</h2><ul>{lis}</ul>'
                f'<h2>Delivering across Kerala</h2><p>' + " · ".join(f'<a href="/youth-face-cream-{c["slug"]}/">Youth Face Cream in {esc(c["name"])}</a>' for c in kerala.CITIES) + f' · <a href="/youth-face-cream-kerala/">All Kerala</a></p>'
                f'<h2>Questions, answered</h2>{faqs}<p><a href="/skincare-guides/">Read all skincare guides</a></p></div></section>')

    def app_page(path, key, ld, image=None, prerender=""):
        m = seo[key]
        doc = head(m["title"], m["description"], path, ld=ld, image=image,
                   og_type="product" if key.startswith("p-") else "website",
                   extra=STYLE + "\n" + boot)
        body = APP_BODY.replace('<main id="view"></main>', f'<main id="view"><div class="prerender">{prerender}</div></main>', 1) if prerender else APP_BODY
        doc += "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n"
        write(path, doc)

    def faq_ld(faqs, url):
        return {"@context": "https://schema.org", "@type": "FAQPage", "url": url,
                "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

    home_ld = [ORG, WEBSITE]
    # keep the old home page's own JSON-LD if it had any
    _, _, old_home_ld = clean(home["content"])
    home_ld += [x for x in old_home_ld if isinstance(x, dict) and x.get("@type") not in ("Organization", "WebSite")]
    home_ld.append(faq_ld(DET["cream"]["faqs"], SITE + "/"))
    app_page("/", "home", [x for x in home_ld if not (isinstance(x, dict) and x.get("@type") == "FAQPage" and x.get("url") != SITE + "/")], prerender=static_home())
    sitemap.append(("/", home["modified"]))
    app_page("/shop/", "shop", [crumbs([("Home", "/"), ("Shop", "/shop/")])])
    sitemap.append(("/shop/", shop["modified"]))
    for path, pid in PRODUCT_ROUTES.items():
        d = items[path]
        p, mrp, sku = price[pid]
        ld = [crumbs([("Home", "/"), ("Shop", "/shop/"), (strip_site(d["title"]).split(" – ")[0], path)])]
        D = DET["lotion" if pid == "lotion" else "cream"]
        name, units, qty = PINFO[pid]
        props = [{"@type": "PropertyValue", "name": "Net quantity", "value": qty}, {"@type": "PropertyValue", "name": "Product type", "value": D["type"]},
                 {"@type": "PropertyValue", "name": "Skin types", "value": D["skinTypes"]}]
        if D["ingredients"]:
            props.insert(0, {"@type": "PropertyValue", "name": "Key ingredients", "value": ", ".join(i["name"] for i in D["ingredients"])})
        if True:
            ld.append({"@context": "https://schema.org", "@type": "Product", "@id": SITE + path + "#product", "name": f"{name} – {qty}",
                       "alternateName": [a.strip() for a in D["aka"].split(",")], "sku": d.get("sku") or sku, "mpn": d.get("sku") or sku,
                       "category": "Health & Beauty > Personal Care > Cosmetics > Skin Care", "additionalProperty": props,
                       "weight": {"@type": "QuantitativeValue", "value": 40 if pid == "lotion" else 25 * units, "unitCode": "MLT" if pid == "lotion" else "GRM"},
                       "manufacturer": {"@id": SITE + "/#organization"}, "countryOfOrigin": "IN",
                       "image": [SITE + UP + img[pid]], "description": D["summary"], "brand": {"@type": "Brand", "name": "Youth Face"},
                       "offers": {"@type": "Offer", "url": SITE + path, "priceCurrency": "INR", "price": str(p),
                                  "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition", "priceValidUntil": "2027-03-31",
                                  "hasMerchantReturnPolicy": {"@type": "MerchantReturnPolicy", "applicableCountry": "IN", "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
                                                              "merchantReturnDays": 7, "merchantReturnLink": SITE + "/refund-returns-policy/"},
                                  "seller": {"@id": SITE + "/#organization"},
                                  "shippingDetails": {"@type": "OfferShippingDetails", "shippingRate": {"@type": "MonetaryAmount", "value": "0", "currency": "INR"},
                                                      "shippingDestination": {"@type": "DefinedRegion", "addressCountry": "IN"}}}})
        ld.append(faq_ld(D["faqs"], SITE + path))
        app_page(path, "p-" + pid, ld, image=UP + img[pid], prerender=static_product(pid))
        sitemap.append((path, d["modified"]))
    for path, key in (("/checkout/", "checkout"), ("/order-success/", "success"), ("/wishlist/", "wishlist")):
        app_page(path, key, [])

    # ------------------------------------------------ articles + pages
    def related(cur, n=3):
        pool = [d for d in posts if d["path"] != cur and d["path"] not in CANONICAL_OVERRIDE]
        words = set(re.findall(r"[a-z]{4,}", cur))
        pool.sort(key=lambda d: -len(words & set(re.findall(r"[a-z]{4,}", d["path"]))))
        return pool[:n]

    for path, d in items.items():
        if d["type"] == "product" or path in APP_PAGES:
            continue
        body_html, h1, ld = clean(d["content"])
        title_h1 = h1 or strip_site(d["title"])
        seo_title = d["seo_title"] or (strip_site(d["title"]) + " | Youth Face")
        seo_desc = d["seo_description"] or html.unescape(re.sub("<[^>]+>", "", d.get("excerpt") or ""))[:155]
        if path == "/security/":
            seo_desc = "How Youth Face keeps your purchase safe: Cash on Delivery, secure online payment links from our verified WhatsApp number, and how your personal information is protected."
        is_post = d["type"] == "post"
        if path in POLICY_PAGES:
            section = ("Policies", None)
        elif is_post or path in GUIDE_PAGES:
            section = ("Skincare guides", "/skincare-guides/")
        else:
            section = (None, None)
        cr = [("Home", "/")] + ([(section[0], section[1])] if section[1] else []) + [(title_h1, path)]
        crumb_html = '<nav class="crumbs" aria-label="Breadcrumb">' + " <span>›</span> ".join(
            f'<a href="{p}">{esc(n)}</a>' if i < len(cr) - 1 else f'<span>{esc(n)}</span>' for i, (n, p) in enumerate(cr)) + "</nav>"
        eyebrow = "Skincare guide" if (is_post or path in GUIDE_PAGES) else ("Policy" if path in POLICY_PAGES else "Youth Face")
        by = ""
        if is_post or path in GUIDE_PAGES:
            by = f'<div class="byline"><span>By <a href="/about-the-author/">{AUTHOR}</a></span><span>Updated {fmt_date(d["modified"])}</span></div>'
        feat = fix_url(d.get("featured_image") or "")
        hero = f'<div class="hero-img"><img src="{esc(feat)}" alt="{esc(title_h1)}"></div>' if feat else ""
        if path in POLICY_FIX:
            body_html = POLICY_FIX[path](body_html)
        if path == "/track-order/":
            body_html = ('<div class="trackbox"><p><b>Track your order on WhatsApp.</b> Send your order ID (it starts with YF) and the phone number you ordered with, and we will reply with your tracking details.</p>'
                         '<a class="btn btn-pink" href="https://wa.me/919980881230?text=Hi%20Youth%20Face%2C%20please%20share%20tracking%20for%20order%20" target="_blank" rel="noopener">Track on WhatsApp</a>'
                         '<p style="margin:10px 0 0;font-size:14px;color:var(--muted)">WhatsApp number: <span style="user-select:all">99808 81230</span></p></div>'
                         '<h2>Where to find your order ID</h2><p>Your order ID is shown on the confirmation screen after you place an order and in the WhatsApp message you send us. It starts with <b>YF</b>, for example YF1234567.</p>'
                         '<h2>Ordered on our old website?</h2><p>Orders placed before our website update can also be tracked on WhatsApp. Send us your old order number and the phone number used for the order.</p>'
                         '<h2>Parcel delayed or damaged?</h2><p>Message us on WhatsApp with your order ID and a photo if the parcel is damaged. See our <a href="/shipping-delivery/">Shipping &amp; Delivery</a> and <a href="/refund-returns-policy/">Refund &amp; Returns</a> policies.</p>')
        if path == "/youth-face-cream-bhatkal-karnataka/":
            body_html += ('<h2>Also delivering in Kerala</h2><p>From Bhatkal, orders also go to every district in Kerala, starting with nearby '
                          '<a href="/youth-face-cream-kasaragod/">Kasaragod</a> and <a href="/youth-face-cream-kannur/">Kannur</a>. '
                          'See <a href="/youth-face-cream-kerala/">Youth Face Cream in Kerala</a>.</p>')
        show_buy = path not in POLICY_PAGES and path not in ("/about-the-author/", "/editorial-policy/", "/security/", "/track-order/")
        rel = ""
        if is_post or path in GUIDE_PAGES:
            rel = '<section class="related"><h2>Keep reading</h2><div class="rel-grid">' + "".join(gcard(x) for x in related(path)) + "</div></section>"
        body = (crumb_html + f'<div class="eyebrow">{eyebrow}</div><h1>{esc(title_h1)}</h1>' + by + hero +
                f'<div class="prose">{body_html}</div>' + (BUYBOX if show_buy else "") + rel)
        ld_all = [crumbs(cr)]
        if ld:
            ld_all += ld
        elif is_post:
            ld_all.append({"@context": "https://schema.org", "@type": "BlogPosting", "headline": title_h1[:110], "description": seo_desc,
                           "datePublished": iso(d["date"]), "dateModified": iso(d["modified"]),
                           "author": {"@type": "Person", "name": AUTHOR, "url": SITE + "/about-the-author/"},
                           "publisher": {"@id": SITE + "/#organization"}, "mainEntityOfPage": SITE + path,
                           **({"image": SITE + feat} if feat else {})})
        static_page(path, seo_title, seo_desc, body, ld=ld_all, og_type="article" if is_post else "website", image=feat or None)
        if path not in CANONICAL_OVERRIDE and path not in NOINDEX:
            sitemap.append((path, d["modified"]))

    # ------------------------------------------------ guides index (replaces old /skincare-guides/ page)
    sg = items["/skincare-guides/"]
    canon_posts = [d for d in posts if d["path"] not in CANONICAL_OVERRIDE]
    body = ('<nav class="crumbs"><a href="/">Home</a> <span>›</span> <span>Skincare guides</span></nav>'
            '<div class="eyebrow">Skincare journal</div><h1>Skincare Guides</h1>'
            '<p style="color:var(--muted);font-size:17px;max-width:60ch">Practical routines, ingredient explainers and honest answers about Youth Face Beauty Cream, written for Indian skin and climate.</p>'
            '<div class="listing"><h2>Latest guides</h2><div class="rel-grid">' + "".join(gcard(d) for d in canon_posts) + "</div>"
            '<h2>Youth Face Cream questions</h2><ul class="linklist">' +
            "".join(f'<li><a href="{p}">{esc(strip_site(items[p]["title"]))}</a></li>' for p in GUIDE_PAGES if p in items and p not in CANONICAL_OVERRIDE) +
            "</ul></div>" + BUYBOX)
    static_page("/skincare-guides/", sg["seo_title"] or "Skincare Guides | Youth Face", sg["seo_description"], body,
                ld=[crumbs([("Home", "/"), ("Skincare guides", "/skincare-guides/")]),
                    {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Skincare Guides", "url": SITE + "/skincare-guides/",
                     "hasPart": [{"@type": "BlogPosting", "headline": strip_site(d["title"]), "url": SITE + d["path"]} for d in canon_posts]}])

    # ------------------------------------------------ Kerala hub + city pages
    KCSS = """<style>
.lead{font-size:17.5px;color:var(--ink)}
.ml{font-size:15px;color:var(--head);background:var(--petal);border-radius:10px;padding:10px 14px;margin:6px 0 18px}
.quick{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:18px 0 6px}
.quick div{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px}
.quick b{display:block;font-family:var(--display);font-size:20px;color:var(--pink-deep)}
.quick span{font-size:13px;color:var(--muted)}
@media (max-width:560px){.quick{grid-template-columns:1fr 1fr}}
.pins{display:flex;flex-wrap:wrap;gap:8px;list-style:none;padding:0!important}
.pins li{background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:6px 12px;font-size:14px;margin:0!important}
.pins small{color:var(--muted)}
.citygrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px;margin:10px 0 18px}
.citygrid a{display:block;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px 14px;text-decoration:none;color:var(--ink)}
.citygrid a b{display:block;font-family:var(--display);font-size:17px}
.citygrid a small{color:var(--muted);font-size:12.5px}
.citygrid a:hover{border-color:var(--pink)}
</style>"""
    K = kerala.CITIES
    PRICE_ROWS = '<div class="tbl"><table><thead><tr><th>Pack</th><th>What you get</th><th>Price</th><th>Per jar</th></tr></thead><tbody>' + \
        '<tr><td><a href="/product/youth-face-beauty-cream-25g/">Pack of 1</a></td><td>1 × 25g jar</td><td>₹549</td><td>₹549</td></tr>' + \
        '<tr><td><a href="/product/youth-face-beauty-cream-pack-of-2/">Pack of 2</a></td><td>2 × 25g jars (50g)</td><td>₹999</td><td>₹500</td></tr>' + \
        '<tr><td><a href="/product/youth-face-beauty-cream-pack-of-3/">Pack of 3</a></td><td>3 × 25g jars (75g)</td><td>₹1,444</td><td>₹481</td></tr></tbody></table></div>'
    QUICK = '<div class="quick"><div><b>₹549</b><span>25g jar · from ₹481/jar in packs</span></div><div><b>Free</b><span>shipping to every Kerala pin code</span></div><div><b>COD</b><span>plus UPI, cards and net banking</span></div></div>'
    kpages = []

    def kerala_page(path, title, desc, h1, body, crumb, faqs, area_ld, geo_head=""):
        ld = [crumbs(crumb), {"@context": "https://schema.org", "@type": "FAQPage", "url": SITE + path,
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
              {"@context": "https://schema.org", "@type": "WebPage", "@id": SITE + path, "url": SITE + path, "name": h1, "description": desc,
               "inLanguage": "en-IN", "dateModified": datetime.date.today().isoformat(), "publisher": {"@id": SITE + "/#organization"},
               "about": {"@type": "Product", "name": "Youth Face Beauty Cream", "brand": {"@type": "Brand", "name": "Youth Face"},
                         "image": SITE + UP + "Youth-Face-Beauty-Cream-25g-600x600.png", "sku": "YFB-PACK-1",
                         "offers": {"@type": "AggregateOffer", "priceCurrency": "INR", "lowPrice": "549", "highPrice": "1444", "offerCount": 3,
                                    "availability": "https://schema.org/InStock", "areaServed": area_ld, "seller": {"@id": SITE + "/#organization"}}}}]
        static_page(path, title, desc, body, ld=ld, extra_head=geo_head)
        kpages.append(path)

    def faq_html(faqs):
        return "".join(f"<details{' open' if i < 2 else ''}><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for i, (q, a) in enumerate(faqs))

    for i, c in enumerate(K):
        path = f"/youth-face-cream-{c['slug']}/"
        nm, aka = c["name"], c["aka"]
        label = f"{nm} ({aka})" if aka else nm
        title = f"Youth Face Cream in {label} – ₹549, COD Available"
        desc = (f"Buy original Youth Face Beauty Cream in {label}, {c['district']} district, Kerala. ₹549 for 25g, free shipping, "
                f"Cash on Delivery and UPI. Delivery to {', '.join(a for a, _ in c['areas'][:3])} and more.")[:300]
        near = [K[j] for j in (i - 1, i + 1, i + 2 if i == 0 else i - 2) if 0 <= j < len(K) and j != i][:3]
        v = i % 3  # rotate wording so shared sections differ between cities
        areas3 = ", ".join(a for a, _ in c["areas"][:3])
        faqs = [
            [(f"Is Youth Face Cream available in {nm}?", f"Yes. Order online or on WhatsApp and it is delivered to your door anywhere in {c['district']} district, including {areas3}."),
             (f"Can I get Youth Face Cream delivered in {nm}?", f"Yes. Youth Face delivers to homes and offices across {c['district']} district, such as {areas3}. Order on the website or WhatsApp."),
             (f"Does Youth Face deliver to {nm}?", f"Yes, to every serviceable pin code in {c['district']} district, including {areas3}.")][v],
            [(f"Is Cash on Delivery available in {nm}?", f"Yes. You can pay in cash when the parcel arrives in {nm}, or pay online by UPI, card or net banking for an extra 5% off."),
             (f"Can I pay on delivery in {nm}?", f"Yes. Choose Cash on Delivery at checkout. Online payment is also available and gives an extra 5% off."),
             (f"What payment options are there for {nm} orders?", "Cash on Delivery, UPI, cards and net banking. Paying online at checkout gives an extra 5% off.")][v],
            [(f"What is the Youth Face Cream price in {nm}?", "₹549 for a 25g jar, ₹999 for two and ₹1,444 for three, the same as everywhere in India, with free shipping."),
             (f"How much does Youth Face Cream cost in {nm}?", "One 25g jar is ₹549. Pack of 2 is ₹999 and Pack of 3 is ₹1,444. There is no delivery charge."),
             (f"Is Youth Face Cream more expensive in {nm}?", "No. The price is the same across India: ₹549, ₹999 or ₹1,444 depending on the pack, with free shipping.")][v],
            c["faq"], c["faq2"],
            (f"Is there a Youth Face store in {nm}?", "No. There is no physical Youth Face shop in Kerala. The original is sold only on youthfacebeauty.com and WhatsApp +91 99808 81230, and ships from Beauty Mart in Bhatkal, Karnataka."),
        ]
        pins = "".join(f"<li>{esc(a)} <small>{z}</small></li>" for a, z in c["areas"])
        lead = [f"<b>Yes, you can order original Youth Face Beauty Cream in {esc(nm)}.</b> A 25g jar costs ₹549, shipping to every {esc(nm)} pin code is free, and you can pay by Cash on Delivery or UPI.",
                f"<b>Youth Face Beauty Cream delivers to {esc(nm)} and all of {esc(c['district'])} district.</b> It's ₹549 for 25g with free shipping, and Cash on Delivery is available.",
                f"<b>Looking for Youth Face Cream in {esc(nm)}?</b> Order the original online for ₹549 (25g), get free delivery to your door, and pay in cash on arrival if you prefer."][v]
        price_intro = ["Prices are the same across Kerala and the rest of India. Paying online at checkout gives an extra 5% off.",
                       f"There is no extra charge for {esc(nm)} delivery. Bigger packs lower the price per jar.",
                       f"{esc(nm)} customers pay the same price as anywhere else in India. Pack of 3 is the best value per jar."][v]
        routine = [f"<p>For most people in {esc(nm)}, a simple routine is enough: a small amount of cream on clean skin at night, sunscreen every morning, and a patch test before the first full use.</p>",
                   "<ol><li><b>Night:</b> cleanse, pat dry, then apply a thin layer to the face and neck.</li><li><b>Morning:</b> cleanse and use sunscreen (SPF 30+).</li><li><b>Before first use:</b> patch test on the inner arm for 24 hours.</li></ol>",
                   f"<p>Use the cream at night after cleansing, wear sunscreen during the day, and patch test first. <a href=\"/how-to-apply-youth-face-cream/\">See the full application guide</a>.</p>"][v]
        orig = [f"<p>Order only from youthfacebeauty.com or WhatsApp +91 99808 81230, and check the seal on the lid when your parcel arrives in {esc(nm)}. <a href=\"/where-to-buy-original-youth-face-cream-avoiding-fakes/\">How to spot fakes</a>.</p>",
                "<ul><li>Buy only from the official website or the verified WhatsApp number.</li><li>Check the authentication seal on the lid.</li><li>Be wary of unusually low prices from unknown sellers.</li></ul>",
                f"<p>There is no Youth Face reseller in {esc(nm)}. If someone offers the cream at a very low price, it may not be original. <a href=\"/where-to-buy-original-youth-face-cream-avoiding-fakes/\">Read how to check</a>.</p>"][v]
        h_order = [f"Ordering Youth Face Cream in {esc(nm)}", f"About delivery in {esc(nm)}", f"Youth Face Cream for {esc(nm)} customers"][v]
        h_pins = [f"Areas and pin codes we deliver to in {esc(c['district'])}", f"Delivery areas in {esc(c['district'])} district", f"{esc(nm)} pin codes we cover"][v]
        body = (f'<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span>›</span> <a href="{kerala.HUB["path"]}">Kerala</a> <span>›</span> <span>{esc(nm)}</span></nav>'
                f'<div class="eyebrow">Delivery in {esc(c["district"])} district, Kerala</div><h1>Youth Face Cream in {esc(label)}</h1>'
                f'<div class="byline"><span>By <a href="/about-the-author/">{AUTHOR}</a></span><span>Updated {datetime.date.today().strftime("%d %b %Y").lstrip("0")}</span></div>'
                f'<div class="prose"><p class="lead">{lead}</p>'
                f'<p class="ml" lang="ml">{c["ml"]}: ഒറിജിനൽ യൂത്ത് ഫേസ് ക്രീം ഓൺലൈനായി ഓർഡർ ചെയ്യാം. ക്യാഷ് ഓൺ ഡെലിവറി ലഭ്യമാണ്.</p>'
                f'{QUICK}<p><a class="cta" href="/product/youth-face-beauty-cream-25g/">Order for {esc(nm)} delivery</a> <a class="cta" href="https://wa.me/919980881230?text={("Hi Youth Face, I want to order Youth Face Cream to " + nm).replace(" ", "%20")}" target="_blank" rel="noopener">Order on WhatsApp</a></p>'
                f'<h2>{h_order}</h2><p>{esc(c["intro"])}</p><p>{esc(c["season"])}</p>'
                f'<h2>{h_pins}</h2><ul class="pins">{pins}</ul>'
                f'<h3>Address tip for {esc(nm)}</h3><p>{esc(c["tip"])}</p>'
                f'<p>Not on the list? Enter your pin code on the <a href="/product/youth-face-beauty-cream-25g/">product page</a> to check delivery to your area, or ask us on WhatsApp for a delivery estimate.</p>'
                f'<h2>Price in {esc(nm)}</h2>{PRICE_ROWS}<p>{price_intro}</p>'
                f'<h2>Skincare for {esc(nm)}\'s weather</h2><p>{esc(c["climate"])}</p>{routine}'
                f'<h2>Getting the original in {esc(nm)}</h2>{orig}'
                f'<h2>{esc(nm)} FAQs</h2>{faq_html(faqs)}'
                f'<p class="note" lang="ml">യൂത്ത് ഫേസ് ക്രീം {c["ml"]} · യൂത്ത് ഫേസ് ബ്യൂട്ടി ക്രീം വില · ഒറിജിനൽ യൂത്ത് ഫേസ് ക്രീം ഓൺലൈൻ</p>'
                f'<h2>Nearby delivery areas</h2><div class="citygrid">' + "".join(f'<a href="/youth-face-cream-{n["slug"]}/"><b>{esc(n["name"])}</b><small>{esc(n["district"])} district</small></a>' for n in near) +
                f'<a href="{kerala.HUB["path"]}"><b>All of Kerala</b><small>{len(K)} districts</small></a></div></div>' + BUYBOX)
        body = KCSS + body
        lat, lng = c["geo"]
        geo_head = (f'<meta name="geo.region" content="IN-KL">\n<meta name="geo.placename" content="{esc(nm)}, Kerala">\n'
                    f'<meta name="geo.position" content="{lat};{lng}">\n<meta name="ICBM" content="{lat}, {lng}">\n')
        area = {"@type": "City", "name": nm, **({"alternateName": aka} if aka else {}),
                "geo": {"@type": "GeoCoordinates", "latitude": lat, "longitude": lng},
                "containedInPlace": {"@type": "AdministrativeArea", "name": f"{c['district']} district", "containedInPlace": {"@type": "State", "name": "Kerala"}}}
        kerala_page(path, title, desc, f"Youth Face Cream in {label}", body,
                    [("Home", "/"), ("Kerala", kerala.HUB["path"]), (nm, path)], faqs, area, geo_head)

    H = kerala.HUB
    hub_faqs = [
        ("Can I buy Youth Face Cream in Kerala?", "Yes. Youth Face Beauty Cream delivers to every serviceable pin code in Kerala. Order on youthfacebeauty.com or on WhatsApp at +91 99808 81230."),
        ("Is Cash on Delivery available in Kerala?", "Yes. Cash on Delivery is available across Kerala, along with UPI, cards and net banking."),
        ("What is the price of Youth Face Cream in Kerala?", "₹549 for one 25g jar, ₹999 for two and ₹1,444 for three. Shipping is free and the price is the same as in the rest of India."),
        ("Where does my Kerala order ship from?", "All orders are packed and shipped by Beauty Mart in Bhatkal, Karnataka, on the coast just north of Kerala."),
        ("How long does delivery take in Kerala?", "It depends on your pin code and the courier route. Message us on WhatsApp at +91 99808 81230 with your pin code for a delivery estimate before you order."),
        ("Is the cream suitable for Kerala's humid weather?", "Most people use a thin layer at night and a light sunscreen during the day. In humid months avoid layering several heavy products. Patch test before first use."),
    ]
    rows = "".join(f'<tr><td><a href="/youth-face-cream-{c["slug"]}/">{esc(c["name"])}</a>{" <small>(" + esc(c["aka"]) + ")</small>" if c["aka"] else ""}</td><td>{esc(c["district"])}</td><td>{esc(", ".join(a for a, _ in c["areas"][:3]))}</td></tr>' for c in K)
    body = (KCSS + '<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> <span>›</span> <span>Kerala</span></nav>'
            f'<div class="eyebrow">Delivery across Kerala</div><h1>{H["h1"]}</h1>'
            f'<div class="prose"><p class="lead"><b>Youth Face Beauty Cream delivers to every district in Kerala</b>, from Kasaragod in the north to Thiruvananthapuram in the south. It costs ₹549 for a 25g jar, shipping is free, and Cash on Delivery is available.</p>'
            f'<p class="ml" lang="ml">{H["ml"]}</p>{QUICK}'
            '<h2>Choose your city</h2><div class="citygrid">' + "".join(f'<a href="/youth-face-cream-{c["slug"]}/"><b>{esc(c["name"])}</b><small>{esc(c["district"])} district</small></a>' for c in K) + '</div>'
            f'<div class="tbl"><table><thead><tr><th>City</th><th>District</th><th>Main delivery areas</th></tr></thead><tbody>{rows}</tbody></table></div>'
            f'<h2>Youth Face Cream price in Kerala</h2>{PRICE_ROWS}'
            '<h2>A routine that suits Kerala\'s climate</h2><p>Most of Kerala is warm and humid, with two monsoon seasons and strong sun in between. That favours a light routine: a thin layer of cream at night on clean skin, and a non-greasy sunscreen every morning, even on cloudy days. Inland areas such as Palakkad get drier, hotter summers, where a gentle moisturiser after the cream can help.</p>'
            '<h2>Buy the original</h2><p>The original Youth Face Cream is sold only on youthfacebeauty.com and through WhatsApp +91 99808 81230. There is no Youth Face shop in Kerala, so be careful with other sellers. See <a href="/where-to-buy-original-youth-face-cream-avoiding-fakes/">how to spot fakes</a>.</p>'
            f'<h2>Kerala delivery questions</h2>{faq_html(hub_faqs)}<p>Also delivering in Karnataka: <a href="/youth-face-cream-bhatkal-karnataka/">Youth Face Cream in Bhatkal</a>.</p></div>' + BUYBOX)
    ld = [crumbs([("Home", "/"), ("Kerala", H["path"])]),
          {"@context": "https://schema.org", "@type": "FAQPage", "url": SITE + H["path"], "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in hub_faqs]},
          {"@context": "https://schema.org", "@type": "CollectionPage", "url": SITE + H["path"], "name": H["h1"], "description": H["description"],
           "hasPart": [{"@type": "WebPage", "name": f"Youth Face Cream in {c['name']}", "url": SITE + f"/youth-face-cream-{c['slug']}/"} for c in K]}]
    static_page(H["path"], H["title"], H["description"], body, ld=ld,
                extra_head='<meta name="geo.region" content="IN-KL">\n<meta name="geo.placename" content="Kerala, India">\n')
    kpages.insert(0, H["path"])
    for kp in kpages:
        sitemap.append((kp, datetime.date.today().isoformat()))

    # ------------------------------------------------ HTML sitemap
    def ul(paths):
        return '<ul class="linklist">' + "".join(f'<li><a href="{p}">{esc(strip_site(items[p]["title"]) if p in items else n)}</a></li>' for p, n in paths) + "</ul>"
    body = ('<nav class="crumbs"><a href="/">Home</a> <span>›</span> <span>Sitemap</span></nav><h1>Sitemap</h1><div class="listing">'
            '<h2>Shop</h2>' + ul([("/", "Home"), ("/shop/", "Shop")] + [(p, "") for p in PRODUCT_ROUTES]) +
            '<h2>Skincare guides</h2>' + ul([("/skincare-guides/", "All skincare guides")] + [(d["path"], "") for d in canon_posts]) +
            '<h2>Youth Face Cream questions</h2>' + ul([(p, "") for p in GUIDE_PAGES if p not in CANONICAL_OVERRIDE]) +
            '<h2>Delivery in Kerala</h2>' + ul([(kerala.HUB["path"], "Youth Face Cream in Kerala")] + [(f"/youth-face-cream-{c['slug']}/", f"Youth Face Cream in {c['name']}") for c in kerala.CITIES]) +
            '<h2>Help</h2>' + ul([(p, "") for p in HELP_PAGES]) +
            '<h2>Policies</h2>' + ul([(p, "") for p in POLICY_PAGES]) + "</div>")
    static_page("/sitemap/", "Sitemap | Youth Face", "Every page on the Youth Face website: shop, products, skincare guides, help and policies.", body,
                ld=[crumbs([("Home", "/"), ("Sitemap", "/sitemap/")])])
    sitemap.append(("/sitemap/", datetime.date.today().isoformat()))
    sitemap = [(p, m) for p, m in sitemap if p != "/skincare-guides/"] + [("/skincare-guides/", sg["modified"])]

    # ------------------------------------------------ 404
    body = ('<div class="eyebrow">Page not found</div><h1>We couldn\'t find that page</h1>'
            '<p class="prose">The link may be old or mistyped. Try the shop or browse the skincare guides.</p>'
            '<p><a class="btn btn-pink" href="/shop/">Go to shop</a> <a class="btn btn-line" href="/skincare-guides/">Skincare guides</a></p>' + BUYBOX)
    static_page("/__404__/", "Page not found | Youth Face", "", body)
    shutil.move(os.path.join(DIST, "__404__", "index.html"), os.path.join(DIST, "404.html"))
    os.rmdir(os.path.join(DIST, "__404__"))
    s404 = open(os.path.join(DIST, "404.html")).read().replace('content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"', 'content="noindex"')
    open(os.path.join(DIST, "404.html"), "w").write(s404)

    # ------------------------------------------------ sitemap.xml + robots.txt
    seen, rows = set(), []
    for p, m in sitemap:
        if p in seen:
            continue
        seen.add(p)
        rows.append(f"  <url><loc>{SITE}{p}</loc><lastmod>{(m or '')[:10]}</lastmod></url>")
    open(os.path.join(DIST, "sitemap.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(rows) + "\n</urlset>\n")
    C = DET["cream"]
    llms = [
        "# Youth Face", "",
        "> " + C["summary"], "",
        "Youth Face is an Indian skincare brand operated by Beauty Mart, Azad Nagar, 4th Cross, Bhatkal, Karnataka, India. Official website: https://youthfacebeauty.com. WhatsApp and phone: +91 99808 81230. Email: mdneehal@gmail.com.", "",
        "## Products and prices (INR, official website)", "",
    ] + [f"- [{PINFO[k][0]} – {PINFO[k][2]}]({SITE}{pp}): {inr(price[k][0])}" + (f" (MRP {inr(price[k][1])})" if price[k][1] > price[k][0] else "") + (f", {inr(price[k][0] / PINFO[k][1])} per jar" if PINFO[k][1] > 1 else "") for pp, k in PRODUCT_ROUTES.items()] + [
        "", "Payment: Cash on Delivery, UPI, cards and net banking. Free shipping across India. Returns for damaged, defective or incorrect items within 7 days of delivery.", "",
        "## Key facts about Youth Face Beauty Cream", "",
        "- Also known as: " + C["aka"],
        "- Key ingredients (as listed on the pack): Kojic Acid and Alpha Arbutin. Full ingredient list is on the product label.",
        "- Product type: " + C["type"],
        "- Best for: " + C["bestFor"],
        "- Skin types: " + C["skinTypes"],
        "- How to use: apply a small amount to clean, dry skin on the face and neck, mainly at night; use sunscreen in the daytime.",
        "- Results: judged over several weeks of regular use; results vary.",
        "- Safety: patch test first; ask a doctor if pregnant, breastfeeding or using prescription skin treatments.",
        "- Customer rating: 4.0 out of 5 from 17 ratings on Amazon.",
        "- Original product is sold only on youthfacebeauty.com and the verified WhatsApp number +91 99808 81230.", "",
        "## FAQs", "",
    ] + [f"- **{q}** {a}" for q, a in C["faqs"]] + [
        "", "## Guides", "",
    ] + [f"- [{strip_site(d['title'])}]({SITE}{d['path']})" for d in canon_posts] + [f"- [{strip_site(items[p]['title'])}]({SITE}{p})" for p in GUIDE_PAGES if p in items and p not in CANONICAL_OVERRIDE] + [
        "", "## Delivery in Kerala", "",
        f"- [Youth Face Cream in Kerala]({SITE}{kerala.HUB['path']}): delivers to every district, free shipping, Cash on Delivery.",
    ] + [f"- [Youth Face Cream in {c['name']}{' (' + c['aka'] + ')' if c['aka'] else ''}]({SITE}/youth-face-cream-{c['slug']}/)" for c in kerala.CITIES] + [
        "", "## Policies", "",
    ] + [f"- [{strip_site(items[p]['title'])}]({SITE}{p})" for p in POLICY_PAGES]
    llms += ["", "## Full text", "", f"- [Full text of all guides and product pages]({SITE}/llms-full.txt)"]
    open(os.path.join(DIST, "llms.txt"), "w").write("\n".join(llms) + "\n")
    BLOCK = "Disallow: /checkout/\nDisallow: /order-success/\nDisallow: /wishlist/\n"
    AI_BOTS = ["Googlebot", "Bingbot", "Google-Extended", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User",
               "ClaudeBot", "Claude-SearchBot", "Claude-User", "Applebot", "Applebot-Extended", "DuckDuckBot", "YandexBot", "CCBot", "Amazonbot", "Meta-ExternalAgent"]
    robots = "# Search engines and AI assistants are welcome to read and cite this site.\n"
    robots += "".join(f"User-agent: {b}\n" for b in AI_BOTS) + "Allow: /\n" + BLOCK + "\n"
    robots += "User-agent: *\nAllow: /\n" + BLOCK + f"\nSitemap: {SITE}/sitemap.xml\n"
    open(os.path.join(DIST, "robots.txt"), "w").write(robots)

    # llms-full.txt: plain-text copy of the guides, product facts and Kerala pages for AI assistants
    def to_md(h):
        b = BeautifulSoup(h, "html.parser")
        out = []
        for el in b.find_all(["h2", "h3", "h4", "p", "li", "summary", "td"]):
            if el.find_parent(["li", "td"]) and el.name in ("p",):
                continue
            t = re.sub(r"\s+", " ", el.get_text(" ", strip=True))
            if not t or (el.get("class") == ["kicker"]):
                continue
            out.append({"h2": "## ", "h3": "### ", "h4": "#### ", "li": "- ", "summary": "**Q:** ", "td": "| "}.get(el.name, "") + t)
        return "\n".join(out)
    full = [f"# Youth Face – full site text", "", f"> Official website of Youth Face (Beauty Mart, Bhatkal, Karnataka, India): {SITE}/", "",
            "This file contains the text of the Youth Face product pages and skincare guides so that AI assistants can read and cite them accurately. Prices are in Indian rupees (INR).", ""]
    full += ["", "---", "", "## Products", ""] + [l for l in llms if l.startswith("- [") and "/product/" in l]
    C2 = DET["cream"]
    full += ["", "### Youth Face Beauty Cream – key facts", ""] + [f"- **{k}:** {v}" for k, v in (("Also known as", C2["aka"]), ("Type", C2["type"]), ("Best for", C2["bestFor"]), ("Skin types", C2["skinTypes"]), ("When to use", C2["when"]))]
    full += ["", "### Youth Face Beauty Cream – FAQs", ""] + [f"**Q: {q}**\nA: {a}\n" for q, a in C2["faqs"]]
    for d in canon_posts + [items[p_] for p_ in GUIDE_PAGES if p_ in items and p_ not in CANONICAL_OVERRIDE]:
        h_, h1_, _ = clean(d["content"])
        full += ["", "---", "", f"## {h1_ or strip_site(d['title'])}", f"URL: {SITE}{d['path']}", f"Updated: {d['modified'][:10]}", "", to_md(h_)]
    for c in kerala.CITIES:
        full += ["", "---", "", f"## Youth Face Cream in {c['name']}", f"URL: {SITE}/youth-face-cream-{c['slug']}/", "", c["intro"], c["climate"], c["tip"]]
    open(os.path.join(DIST, "llms-full.txt"), "w").write("\n".join(full) + "\n")

    # IndexNow key (Bing, Yandex, Seznam, Naver) – the GitHub workflow pings these engines after each deploy
    open(os.path.join(DIST, INDEXNOW_KEY + ".txt"), "w").write(INDEXNOW_KEY)

    # ------------------------------------------------ vercel.json
    OLD_HOST = "https://old.youthfacebeauty.com"
    redirects = [
        {"source": "/cart", "destination": "/checkout/", "permanent": True},
        {"source": "/cart/", "destination": "/checkout/", "permanent": True},
        {"source": "/my-account/", "destination": "/track-order/", "permanent": True},
        {"source": "/feed/", "destination": "/skincare-guides/", "permanent": True},
        {"source": "/my-account/:path*", "destination": "/track-order/", "permanent": True},
        {"source": "/my-account", "destination": "/track-order/", "permanent": True},
        {"source": "/sitemap_index.xml", "destination": "/sitemap.xml", "permanent": True},
        {"source": "/wp-sitemap.xml", "destination": "/sitemap.xml", "permanent": True},
        *[{"source": f"/{n}-sitemap.xml", "destination": "/sitemap.xml", "permanent": True} for n in ("post", "page", "product", "category", "product_cat", "local")],
        {"source": "/feed/:path*", "destination": "/skincare-guides/", "permanent": True},
        {"source": "/feed", "destination": "/skincare-guides/", "permanent": True},
        {"source": "/category/:path*", "destination": "/skincare-guides/", "permanent": True},
        {"source": "/tag/:path*", "destination": "/skincare-guides/", "permanent": True},
        {"source": "/author/:path*", "destination": "/about-the-author/", "permanent": True},
        {"source": "/product-category/:path*", "destination": "/shop/", "permanent": True},
        {"source": "/product-tag/:path*", "destination": "/shop/", "permanent": True},
        {"source": "/brand/:path*", "destination": "/shop/", "permanent": True},
        {"source": "/shop/page/:n", "destination": "/shop/", "permanent": True},
        {"source": "/page/:n", "destination": "/", "permanent": True},
        {"source": "/wp-admin/:path*", "destination": "/", "permanent": False},
        {"source": "/wp-login.php", "destination": "/", "permanent": False},
        {"source": "/favicon.ico", "destination": "/favicon-48.png", "permanent": True},
        {"source": "/:slug/amp", "destination": "/:slug/", "permanent": True},
        *[{"source": "/", "has": [{"type": "query", "key": "add-to-cart", "value": k}], "destination": v, "permanent": False} for k, v in ADD_TO_CART.items()],
        {"source": "/", "has": [{"type": "query", "key": "add-to-cart"}], "destination": "/shop/", "permanent": False},
        *[{"source": f"/{pre}/:slug/", "destination": dst, "permanent": True} for pre, dst in (("category", "/skincare-guides/"), ("tag", "/skincare-guides/"),
          ("author", "/about-the-author/"), ("product-category", "/shop/"), ("product-tag", "/shop/"), ("brand", "/shop/"))],
        *[{"source": f"/{pre}/:slug/page/:n/", "destination": dst, "permanent": True} for pre, dst in (("category", "/skincare-guides/"), ("tag", "/skincare-guides/"))],
    ]
    vercel = {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        "trailingSlash": True,
        "redirects": redirects,
        # Photos: while testing on vercel.app they load from the live WordPress site;
        # after the domain moves they load from WordPress at old.youthfacebeauty.com (or from /wp-content in this repo if added).
        "rewrites": [{"source": "/wp-content/:path*", "has": [{"type": "host", "value": "(?<sub>.*)\\.vercel\\.app"}],
                      "destination": "https://youthfacebeauty.com/wp-content/:path*"},
                     {"source": "/wp-content/:path*", "destination": OLD_HOST + "/wp-content/:path*"}],
        "headers": [
            {"source": "/(.*)", "has": [{"type": "host", "value": "(?<sub>.*)\\.vercel\\.app"}],
             "headers": [{"key": "X-Robots-Tag", "value": "noindex, nofollow"}]},
            {"source": "/(.*)", "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"},
                                            {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"}]},
            {"source": "/wp-content/(.*)", "headers": [{"key": "Cache-Control", "value": "public, max-age=31536000, immutable"}]},
        ],
    }
    json.dump(vercel, open(os.path.join(DIST, "vercel.json"), "w"), indent=2)
    for f in glob.glob(os.path.join(ROOT, "static", "*")):
        if os.path.isdir(f):
            shutil.copytree(f, os.path.join(DIST, os.path.basename(f)), dirs_exist_ok=True)
        else:
            shutil.copy(f, DIST)
    print("built", sum(len(f) for _, _, f in os.walk(DIST)), "files;", len(rows), "URLs in sitemap.xml")


if __name__ == "__main__":
    main()
