// POST /api/verify-payment — confirms with Razorpay that the payment is real and captured/authorised.
const { enabled, rz, validSignature, readJson, send } = require("./_razorpay");

module.exports = async (req, res) => {
  if (req.method !== "POST") return send(res, 405, { error: "Use POST" });
  if (!enabled()) return send(res, 503, { error: "Online payment is not switched on." });
  const b = await readJson(req);
  const { razorpay_order_id: orderId, razorpay_payment_id: paymentId, razorpay_signature: sig } = b;
  if (!orderId || !paymentId || !validSignature(orderId, paymentId, sig)) return send(res, 400, { ok: false, error: "Payment could not be verified." });
  try {
    const p = await rz("/payments/" + encodeURIComponent(paymentId));
    const ok = p.order_id === orderId && (p.status === "captured" || p.status === "authorized");
    send(res, ok ? 200 : 400, { ok, paymentId, status: p.status, amount: p.amount / 100, method: p.method });
  } catch (e) {
    send(res, 502, { ok: false, error: "Could not confirm the payment. If money was deducted, message us on WhatsApp." });
  }
};
