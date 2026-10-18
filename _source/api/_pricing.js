// Server-side prices — the single source of truth for what a customer is charged online.
// Keep in sync with PRODUCTS / CONFIG in _source/index.html.
const PRODUCTS = {
  "cream-1": { name: "Youth Face Beauty Cream 25g (Pack of 1)", price: 549 },
  "cream-2": { name: "Youth Face Beauty Cream Pack of 2", price: 999 },
  "cream-3": { name: "Youth Face Beauty Cream Pack of 3", price: 1444 },
  "lotion":  { name: "Youth Face Body Lotion 40 ml", price: 599 },
};
const COUPONS = {
  WELCOME10: { type: "pct", value: 10, min: 0 },
  GLOW100: { type: "flat", value: 100, min: 999 },
};
const REWARDS = [{ at: 999, off: 50 }, { at: 1444, off: 150 }];
const PREPAID_PCT = 5;
const SHIPPING = 0;

function price(items, couponCode) {
  if (!Array.isArray(items) || !items.length || items.length > 10) throw new Error("Your cart is empty.");
  const lines = items.map(l => {
    const p = PRODUCTS[l && l.id];
    const qty = Math.floor(Number(l && l.qty));
    if (!p || !(qty >= 1 && qty <= 20)) throw new Error("A product in your cart is not available.");
    return { id: l.id, name: p.name, qty, price: p.price, total: p.price * qty };
  });
  const sub = lines.reduce((a, l) => a + l.total, 0);
  const code = String(couponCode || "").toUpperCase();
  const c = COUPONS[code];
  let coup = 0;
  if (c && sub >= c.min) coup = c.type === "pct" ? (sub * c.value) / 100 : c.value;
  let reward = 0;
  REWARDS.forEach(r => { if (sub >= r.at) reward = r.off; });
  const after = sub - coup - reward;
  const prepaid = (after * PREPAID_PCT) / 100;
  const total = Math.round(after - prepaid + SHIPPING);
  return { lines, sub, coupon: coup ? code : "", discount: Math.round(coup) + reward + Math.round(prepaid), total };
}
module.exports = { price };
