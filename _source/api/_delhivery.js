// Delhivery B2C API: pin code serviceability and shipment (waybill) creation.
// Vercel env: DELHIVERY_TOKEN, DELHIVERY_PICKUP (warehouse name exactly as registered in Delhivery),
// optional DELHIVERY_ENV=staging, DELHIVERY_GRAMS_PER_JAR (default 100), DELHIVERY_MODE (Surface|Express, default Surface).
const base = () => (process.env.DELHIVERY_ENV === "staging" ? "https://staging-express.delhivery.com" : "https://track.delhivery.com");
const token = () => process.env.DELHIVERY_TOKEN || "";
const pickup = () => process.env.DELHIVERY_PICKUP || "";
const delhiveryOn = () => Boolean(token() && pickup());
const RETURN = { name: "Beauty Mart", add: "Azad Nagar 4th Cross, Bhatkal", city: "Bhatkal", state: "Karnataka", pin: "581320", phone: "9980881230" };

async function serviceable(pin) {
  const r = await fetch(base() + "/c/api/pin-codes/json/?filter_codes=" + encodeURIComponent(pin), { headers: { Authorization: "Token " + token(), Accept: "application/json" } });
  const j = await r.json().catch(() => ({}));
  const pc = j && j.delivery_codes && j.delivery_codes[0] && j.delivery_codes[0].postal_code;
  if (!pc) return { known: false, cod: false, prepaid: false };
  return { known: true, cod: String(pc.cod).toUpperCase() === "Y", prepaid: String(pc.pre_paid).toUpperCase() === "Y", city: pc.city || "", state: pc.state_code || "" };
}

async function createShipment({ ref, c, q, pay }) {
  const grams = Math.max(1, q.units) * (Number(process.env.DELHIVERY_GRAMS_PER_JAR) || 100);
  const shipment = {
    name: c.name, add: [c.address, c.landmark ? "Near " + c.landmark : ""].filter(Boolean).join(", "), pin: c.pin, city: c.city, state: c.state, country: "India",
    phone: c.phone, order: ref, payment_mode: pay === "cod" ? "COD" : "Prepaid", cod_amount: pay === "cod" ? String(q.total) : "0", total_amount: String(q.total),
    products_desc: q.lines.map(l => `${l.name} x${l.qty}`).join(", ").slice(0, 200), quantity: String(q.lines.reduce((a, l) => a + l.qty, 0)),
    order_date: new Date().toISOString().slice(0, 19).replace("T", " "), weight: String(grams), shipment_length: "12", shipment_width: "10", shipment_height: "8",
    seller_name: "Beauty Mart", seller_add: RETURN.add, return_name: RETURN.name, return_add: RETURN.add, return_city: RETURN.city, return_state: RETURN.state,
    return_pin: RETURN.pin, return_country: "India", return_phone: RETURN.phone, shipping_mode: process.env.DELHIVERY_MODE || "Surface", address_type: "home", waybill: "",
  };
  const data = { shipments: [shipment], pickup_location: { name: pickup() } };
  const r = await fetch(base() + "/api/cmu/create.json", {
    method: "POST", headers: { Authorization: "Token " + token(), Accept: "application/json", "Content-Type": "application/x-www-form-urlencoded" },
    body: "format=json&data=" + encodeURIComponent(JSON.stringify(data)),
  });
  const j = await r.json().catch(() => ({}));
  const pkg = j && Array.isArray(j.packages) && j.packages[0];
  if (r.ok && pkg && pkg.waybill && String(pkg.status).toLowerCase() === "success") return { ok: true, awb: String(pkg.waybill) };
  const why = (pkg && (Array.isArray(pkg.remarks) ? pkg.remarks.join("; ") : pkg.remarks)) || j.rmk || j.error || ("HTTP " + r.status);
  return { ok: false, error: String(why).slice(0, 300) };
}
module.exports = { delhiveryOn, serviceable, createShipment };
