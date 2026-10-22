// POST /api/lead — shopper ticked the WhatsApp consent box at checkout; the lead goes to the private Order Desk.
// Always answers {ok:true} for a valid request, even if the Order Desk is off or fails (the shopper never sees an error).
const { pushLead } = require("./_orderdesk");
const { readJson, send } = require("./_razorpay");

const HOUR = 3600 * 1000, PER_PHONE = 5, GLOBAL = 300;
const seen = new Map(); // phone -> [timestamps]  (in-memory, per warm instance: a light brake, not a guarantee)
let all = [];

function allowed(phone) {
  const now = Date.now();
  all = all.filter(t => now - t < HOUR);
  if (all.length >= GLOBAL) return false;
  const mine = (seen.get(phone) || []).filter(t => now - t < HOUR);
  if (mine.length >= PER_PHONE) { seen.set(phone, mine); return false; }
  mine.push(now); seen.set(phone, mine); all.push(now);
  if (seen.size > 5000) for (const [k, v] of seen) if (!v.some(t => now - t < HOUR)) seen.delete(k);
  return true;
}
const clean = (v, n) => String(v == null ? "" : v).replace(/[\u0000-\u001f\u007f-\u009f]/g, " ").replace(/\s+/g, " ").trim().slice(0, n);

module.exports = async (req, res) => {
  res.setHeader("Cache-Control", "no-store");
  if (req.method !== "POST") return send(res, 405, { error: "Use POST" });
  const b = await readJson(req);
  if (b.consent !== true) return send(res, 400, { error: "Consent is required." });
  const phone = String(b.phone == null ? "" : b.phone).replace(/\D/g, "").slice(-10);
  if (!/^[6-9]\d{9}$/.test(phone)) return send(res, 400, { error: "Enter a valid 10-digit mobile number." });
  if (!allowed(phone)) return send(res, 200, { ok: true });
  try { await pushLead({ name: clean(b.name, 80), phone, product: clean(b.product, 120) }); } catch (e) { /* ignore */ }
  return send(res, 200, { ok: true });
};
module.exports._reset = () => { seen.clear(); all = []; };
