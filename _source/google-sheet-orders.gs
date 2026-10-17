/**
 * Youth Face — save every website order to this Google Sheet.
 * Setup (5 minutes):
 *  1. Create a new Google Sheet named "Youth Face Orders".
 *  2. Extensions → Apps Script → delete everything → paste this file → Save.
 *  3. Deploy → New deployment → type "Web app" → Execute as: Me → Who has access: Anyone → Deploy.
 *  4. Copy the Web app URL and put it in CONFIG.orderWebhook in _source/index.html (or send it to Claude).
 */
const COLUMNS = ["Received", "Order ID", "Status", "Name", "Phone", "Email", "Address", "Landmark", "City", "State", "Pin code",
                 "Items", "Subtotal", "Coupon", "Discount", "COD charge", "Total", "Payment", "Order time", "Page"];

function doPost(e) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
  if (sheet.getLastRow() === 0) sheet.appendRow(COLUMNS);
  let d = {};
  try { d = JSON.parse(e.postData.contents); } catch (err) { return ContentService.createTextOutput("bad request"); }
  const clean = v => String(v == null ? "" : v).replace(/^[=+\-@]/, "'$&").slice(0, 2000);  // stop formula injection
  sheet.appendRow([new Date(), clean(d.id), "New", clean(d.name), "'" + clean(d.phone), clean(d.email), clean(d.address), clean(d.landmark),
                   clean(d.city), clean(d.state), "'" + clean(d.pin), clean(d.items), Number(d.subtotal) || 0, clean(d.coupon),
                   Number(d.discount) || 0, Number(d.cod) || 0, Number(d.total) || 0, clean(d.payment), clean(d.at), clean(d.page)]);
  return ContentService.createTextOutput("ok");
}
