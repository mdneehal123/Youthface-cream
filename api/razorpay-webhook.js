// POST /api/razorpay-webhook — Razorpay calls this when a payment is captured, so a paid order reaches the
// Order Desk even if the shopper closed the page (or lost internet) right after paying.
// The Order Desk keeps one entry per order number, so the normal /api/verify-payment save and this backup never duplicate.
// Razorpay Dashboard → Account & Settings → Webhooks → Add: URL https://www.youthfacebeauty.com/api/razorpay-webhook,
// event payment.captured, secret = the value of RAZORPAY_WEBHOOK_SECRET in Vercel.
const crypto = require("crypto");
const { price } = require("./_pricing");
const { customer } = require("./_shared");
const { pushToDesk } = require("./_orderdesk");
const { rz } = require("./_razorpay");

async function rawBody(req) {
  const chunks = [];
  for await (const c of req) chunks.push(typeof c === "string" ? Buffer.from(c) : c);
  return Buffer.concat(chunks).toString("utf8");
}

module.exports = async (req, res) => {
  if (req.method !== "POST") { res.statusCode = 405; return res.end(); }
  const secret = process.env.RAZORPAY_WEBHOOK_SECRET;
  if (!secret) { res.statusCode = 503; return res.end(); }
  const body = await rawBody(req);
  const want = Buffer.from(crypto.createHmac("sha256", secret).update(body).digest("hex"));
  const got = Buffer.from(String(req.headers["x-razorpay-signature"] || ""));
  if (!(want.length === got.length && crypto.timingSafeEqual(want, got))) { res.statusCode = 400; return res.end(); }
  let ev = {}; try { ev = JSON.parse(body); } catch (e) { res.statusCode = 400; return res.end(); }
  const pay = ev.payload && ev.payload.payment && ev.payload.payment.entity;
  if (ev.event !== "payment.captured" || !pay || !pay.order_id) { res.statusCode = 200; return res.end('{"ok":true,"skipped":true}'); }

  let order = {};
  try { order = await rz("/orders/" + encodeURIComponent(pay.order_id)); } catch (e) { res.statusCode = 500; return res.end(); } // Razorpay retries
  const n = order.notes || {};
  if (n.site !== "youthfacebeauty.com") { res.statusCode = 200; return res.end('{"ok":true,"skipped":"other site"}'); }

  const items = String(n.cart || "").split(",").map(s => s.split(":")).filter(a => a[0]).map(([id, qty]) => ({ id, qty: Number(qty) || 1 }));
  let q;
  try { q = price(items, n.coupon, "online"); }
  catch (e) { q = { lines: [{ id: "yf-unknown", name: n.items || "Website order (see Razorpay)", qty: 1, price: pay.amount / 100 }], sub: pay.amount / 100, discount: 0, coupon: n.coupon || "" }; }

  const warn = [];
  let c;
  try { c = customer(n); }
  catch (e) {
    c = { name: n.name || "", phone: String(n.phone || pay.contact || "").replace(/\D/g, "").slice(-10), email: n.email || pay.email || "",
          address: n.address || "", landmark: n.landmark || "", city: n.city || "", state: n.state || "", pin: n.pin || "" };
    warn.push("⚠ address incomplete — call the customer");
  }
  const ref = String(n.ref || pay.order_id).replace(/[^A-Z0-9]/gi, "").slice(0, 20);
  const total = pay.amount / 100;
  if (q.total && q.total !== total) warn.push(`⚠ amount ₹${total} differs from cart ₹${q.total}`);
  const desk = await pushToDesk({ ref, c, q: { ...q, total }, pay: "upi", paid: true, payId: pay.id,
    note: [`Paid online via Razorpay (${pay.method || "online"}) ${pay.id} · saved by webhook backup`].concat(warn).join(" ") });
  if (!desk.ok) { res.statusCode = 500; return res.end(); } // let Razorpay retry later
  res.statusCode = 200; res.setHeader("Content-Type", "application/json"); res.end(JSON.stringify({ ok: true }));
};
