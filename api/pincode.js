// GET /api/pincode?pin=575001 — whether Delhivery allows Cash on Delivery for this pin code (lookup only; books nothing).
// { known, cod } — cod is true only when Delhivery answered and allows COD there; a failed check gives cod:false.
const { delhiveryOn, serviceable } = require("./_delhivery");
const { send } = require("./_razorpay");
module.exports = async (req, res) => {
  const pin = String((req.query && req.query.pin) || new URL(req.url, "http://x").searchParams.get("pin") || "").replace(/\D/g, "");
  res.setHeader && res.setHeader("Cache-Control", "no-store");
  if (!/^[1-9]\d{5}$/.test(pin)) return send(res, 400, { known: false, cod: false });
  if (!delhiveryOn()) return send(res, 200, { known: false, cod: false });
  try { const s = await serviceable(pin); return send(res, 200, { known: s.known, cod: !!(s.known && s.cod) }); }
  catch (e) { return send(res, 200, { known: false, cod: false }); }
};
