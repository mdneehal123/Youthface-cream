// GET /api/payment-config — tells the checkout whether online payment is switched on.
const { enabled, keyId, send } = require("./_razorpay");
module.exports = (req, res) => send(res, 200, { enabled: enabled(), keyId: enabled() ? keyId() : "" });
