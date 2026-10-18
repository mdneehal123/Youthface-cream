// POST /api/cod-order — Cash on Delivery: prices the order on the server and books it with Delhivery.
// Every COD order is also saved in the Order Desk (customer record); the label is printed from Delhivery.
const { price } = require("./_pricing");
const { customer } = require("./_shared");
const { delhiveryOn, serviceable, createShipment } = require("./_delhivery");
const { pushToDesk } = require("./_orderdesk");
const { readJson, send } = require("./_razorpay");

module.exports = async (req, res) => {
  if (req.method !== "POST") return send(res, 405, { error: "Use POST" });
  if (!delhiveryOn()) return send(res, 503, { error: "COD booking is not switched on." });
  const b = await readJson(req);
  if (b.website) return send(res, 200, { ok: true });
  let q, c;
  try { q = price(b.items, b.coupon, "cod"); c = customer(b.customer); } catch (e) { return send(res, 400, { error: e.message }); }
  const ref = String(b.ref || "").replace(/[^A-Z0-9]/gi, "").slice(0, 20) || "YF" + Date.now().toString().slice(-7);
  try {
    const s = await serviceable(c.pin);
    if (s.known && !s.cod) return send(res, 409, { error: "Cash on Delivery isn't available for pin code " + c.pin + ". Please pay online instead.", codUnavailable: true });
  } catch (e) { /* if the check fails, still try to book */ }
  let d;
  try { d = await createShipment({ ref, c, q, pay: "cod" }); } catch (e) { d = { ok: false, error: String(e.message || e) }; }
  // Every COD order is also saved in the Order Desk as a customer record.
  // Booked: courier Delhivery + AWB, label printed from the Delhivery panel. Not booked: flagged for manual booking.
  const desk = await pushToDesk(d.ok
    ? { ref, c, q, pay: "cod", paid: false, courier: "Delhivery", awb: d.awb, note: `COD booked with Delhivery · AWB ${d.awb} · print the label from the Delhivery panel` }
    : { ref, c, q, pay: "cod", paid: false, note: "⚠ COD website order — Delhivery booking failed: " + d.error + ". Please book it in Delhivery." });
  if (d.ok) return send(res, 200, { ok: true, ref, awb: d.awb, courier: "Delhivery", total: q.total, savedToDesk: desk.ok, trackUrl: "https://www.delhivery.com/track/package/" + d.awb });
  return send(res, 200, { ok: true, ref, awb: "", courier: "", total: q.total, pending: true, savedToDesk: desk.ok });
};
