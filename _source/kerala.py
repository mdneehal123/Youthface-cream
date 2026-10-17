"""Kerala city pages for Youth Face. Each city has its own copy so pages are not near-duplicates."""

HUB = {
    "path": "/youth-face-cream-kerala/",
    "title": "Youth Face Cream in Kerala – Price, COD & Delivery | Youth Face",
    "description": "Order original Youth Face Beauty Cream anywhere in Kerala: ₹549 for 25g, free shipping, Cash on Delivery and UPI. Delivery to Kochi, Thiruvananthapuram, Kozhikode and more.",
    "h1": "Youth Face Cream in Kerala",
    "ml": "കേരളത്തിൽ എല്ലായിടത്തും ഒറിജിനൽ യൂത്ത് ഫേസ് ക്രീം ഓൺലൈനായി ഓർഡർ ചെയ്യാം. ക്യാഷ് ഓൺ ഡെലിവറി ലഭ്യമാണ്.",
}

# order = north to south, used for "nearby" links
CITIES = [
    {
        "slug": "kasaragod", "name": "Kasaragod", "ml": "കാസർഗോഡ്", "district": "Kasaragod", "aka": "",
        "areas": [("Kasaragod town", "671121"), ("Kanhangad", "671315"), ("Nileshwar", "671314"), ("Uppala", "671322"), ("Manjeshwar", "671323")],
        "intro": "Kasaragod is Kerala's northernmost district and the part of the state closest to our dispatch point in Bhatkal, on the Karnataka coast. Many families here shop across both Kerala and Karnataka, and Youth Face Cream reaches Kasaragod homes the same way it reaches the rest of India: ordered online or on WhatsApp and delivered to your door.",
        "climate": "Coastal Kasaragod stays warm and humid most of the year, with a heavy south-west monsoon. Humid air means less need for thick layers. A thin layer of cream at night and a light, non-greasy sunscreen in the morning is usually enough.",
        "faq": ("Is a lightweight routine better for Kasaragod's coastal humidity?", "Yes. In humid weather a small amount of cream spread thinly at night works well. Skip heavy layering and use a light gel or lotion sunscreen in the daytime."),
    },
    {
        "slug": "kannur", "name": "Kannur", "ml": "കണ്ണൂർ", "district": "Kannur", "aka": "",
        "areas": [("Kannur town", "670001"), ("Thalassery", "670101"), ("Payyanur", "670307"), ("Taliparamba", "670141"), ("Iritty", "670703")],
        "intro": "Kannur, along with Thalassery, Payyanur and Taliparamba, is one of the north Malabar areas where we get regular WhatsApp enquiries. You can order Youth Face Beauty Cream online from anywhere in Kannur district, pay on delivery, and get the same price as everywhere else in India.",
        "climate": "Kannur's coastline brings strong sun between the monsoon months and high humidity during them. Daily sunscreen matters more than any cream for marks and tan, because sun exposure can make dark spots look darker again.",
        "faq": ("I ride a two-wheeler daily in Kannur. How do I protect my results?", "Sun exposure on the commute can undo progress. Apply sunscreen before you leave, reapply if you are out for long, and keep the cream for your night routine."),
    },
    {
        "slug": "kozhikode", "name": "Kozhikode", "ml": "കോഴിക്കോട്", "district": "Kozhikode", "aka": "Calicut",
        "areas": [("Kozhikode city", "673001"), ("Medical College area", "673008"), ("Feroke", "673631"), ("Vadakara", "673101"), ("Koyilandy", "673305")],
        "intro": "Kozhikode, also known as Calicut, is the commercial centre of the Malabar coast. Whether you live in the city, near Medical College, or in Vadakara or Koyilandy, you can order original Youth Face Cream online and pay by Cash on Delivery or UPI when it arrives.",
        "climate": "Kozhikode gets some of the heaviest monsoon rain on the coast, and the months around it are hot and sticky. In sticky weather, cleanse well at night before applying the cream so sweat and sunscreen don't stay trapped on the skin.",
        "faq": ("Is Youth Face Cream also searched as 'Calicut' Youth Face Cream?", "Yes. Kozhikode and Calicut are the same city. Delivery, prices and payment options are the same for every pin code in Kozhikode district."),
    },
    {
        "slug": "malappuram", "name": "Malappuram", "ml": "മലപ്പുറം", "district": "Malappuram", "aka": "",
        "areas": [("Malappuram town", "676505"), ("Manjeri", "676121"), ("Tirur", "676101"), ("Perinthalmanna", "679322"), ("Ponnani", "679577"), ("Kondotty", "673638")],
        "intro": "Malappuram is one of Kerala's most populous districts, with busy towns like Manjeri, Tirur, Perinthalmanna and Ponnani. Many customers here order on WhatsApp first, ask a question, and then complete the order. Both ways work, and Cash on Delivery is available.",
        "climate": "Inland towns like Manjeri and Perinthalmanna get hot afternoons, while Tirur and Ponnani on the coast stay more humid. Either way, keep the routine simple: cleanse, a thin layer of cream at night, and sunscreen in the day.",
        "faq": ("Can I order on WhatsApp from Malappuram instead of the website?", "Yes. Message +91 99808 81230 with your pack choice, name, address and pin code, and our team will confirm the order. The price is the same as on the website."),
    },
    {
        "slug": "palakkad", "name": "Palakkad", "ml": "പാലക്കാട്", "district": "Palakkad", "aka": "",
        "areas": [("Palakkad town", "678001"), ("Ottapalam", "679101"), ("Shoranur", "679121"), ("Mannarkkad", "678582"), ("Chittur", "678101")],
        "intro": "Palakkad sits inland at the Palakkad Gap, the break in the Western Ghats that connects Kerala with Tamil Nadu. Youth Face Cream delivers to Palakkad town and across the district, including Ottapalam, Shoranur, Mannarkkad and Chittur.",
        "climate": "Palakkad is hotter and drier than coastal Kerala, especially from March to May, and the dry winds through the gap can leave skin feeling tight. If your skin feels dry after cleansing, follow the cream with a gentle moisturiser.",
        "faq": ("My skin feels dry in Palakkad's summer heat. What should I do?", "Use a gentle cleanser, apply the cream as directed, and add a plain moisturiser if your skin feels tight. Drink enough water and always wear sunscreen outdoors."),
    },
    {
        "slug": "thrissur", "name": "Thrissur", "ml": "തൃശ്ശൂർ", "district": "Thrissur", "aka": "",
        "areas": [("Thrissur city", "680001"), ("Guruvayur", "680101"), ("Chalakudy", "680307"), ("Irinjalakuda", "680121"), ("Kunnamkulam", "680503")],
        "intro": "Thrissur is often called the cultural capital of Kerala, and it is a busy shopping centre for central Kerala. You can order Youth Face Beauty Cream to Thrissur city, Guruvayur, Chalakudy, Irinjalakuda or Kunnamkulam and pay on delivery.",
        "climate": "Thrissur is humid for much of the year with a long monsoon. Outdoor festival days, like the Pooram season in April and May, mean hours in strong sun. Those are the days sunscreen does the most to protect your routine.",
        "faq": ("I'll be outdoors for a festival in Thrissur. Should I still use the cream?", "Keep using the cream at night as usual. During the day, focus on sunscreen and reapply it if you are in the sun for several hours."),
    },
    {
        "slug": "kochi", "name": "Kochi", "ml": "കൊച്ചി", "district": "Ernakulam", "aka": "Ernakulam",
        "areas": [("Ernakulam / MG Road", "682011"), ("Kakkanad", "682030"), ("Edappally", "682024"), ("Vyttila", "682019"), ("Aluva", "683101"), ("Fort Kochi", "682001")],
        "intro": "Kochi, in Ernakulam district, is Kerala's largest urban area and the city we deliver to most in the state. From offices in Kakkanad and Infopark to homes in Edappally, Vyttila, Aluva and Fort Kochi, you can order original Youth Face Cream online with free shipping and Cash on Delivery.",
        "climate": "Kochi is coastal and humid all year, and city commutes mean daily sun and pollution. A night routine works best here: cleanse well to remove sweat, dust and sunscreen, then apply a thin layer of cream.",
        "faq": ("Do you deliver to offices in Kakkanad or Infopark?", "Yes. Use your office address and pin code at checkout, and add a landmark or building name so the courier can find you."),
    },
    {
        "slug": "kottayam", "name": "Kottayam", "ml": "കോട്ടയം", "district": "Kottayam", "aka": "",
        "areas": [("Kottayam town", "686001"), ("Changanassery", "686101"), ("Pala", "686575"), ("Ettumanoor", "686631"), ("Vaikom", "686141")],
        "intro": "Kottayam, between the backwaters and the hills, includes busy towns like Changanassery, Pala, Ettumanoor and Vaikom. Youth Face Cream delivers across the district, and you can pay on delivery or online.",
        "climate": "Kottayam gets heavy rainfall and high humidity for much of the year. Humid, rainy weather can make skin feel oily, so use a small amount of cream and spread it thinly rather than layering several products.",
        "faq": ("Do I need sunscreen in Kottayam during the rainy season?", "Yes. UV still reaches your skin on cloudy days. A light sunscreen in the morning helps protect the even-looking tone you are working towards."),
    },
    {
        "slug": "alappuzha", "name": "Alappuzha", "ml": "ആലപ്പുഴ", "district": "Alappuzha", "aka": "Alleppey",
        "areas": [("Alappuzha town", "688001"), ("Cherthala", "688524"), ("Kayamkulam", "690502"), ("Haripad", "690514"), ("Mavelikkara", "690101")],
        "intro": "Alappuzha, also called Alleppey, is known for its backwaters and coastline. We deliver Youth Face Beauty Cream to Alappuzha town, Cherthala, Kayamkulam, Haripad and Mavelikkara, with free shipping and Cash on Delivery.",
        "climate": "Sun reflects off water, so days on the backwaters or beach mean more sun on your face than you might expect. Wear sunscreen and a hat outdoors, and keep the cream for your night routine.",
        "faq": ("Is Youth Face Cream also searched as 'Alleppey' Youth Face Cream?", "Yes. Alappuzha and Alleppey are the same place. Prices, delivery and payment options are the same across Alappuzha district."),
    },
    {
        "slug": "kollam", "name": "Kollam", "ml": "കൊല്ലം", "district": "Kollam", "aka": "Quilon",
        "areas": [("Kollam town", "691001"), ("Karunagappally", "690518"), ("Kottarakkara", "691506"), ("Punalur", "691305")],
        "intro": "Kollam, once known as Quilon, is a coastal district between Alappuzha and Thiruvananthapuram, with towns like Karunagappally, Kottarakkara and Punalur. You can order Youth Face Cream online from anywhere in Kollam district and pay when it arrives.",
        "climate": "Coastal Kollam is warm and humid, while inland Punalur can get very hot in summer. Adjust to how your skin feels: thinner layers when it's humid, and a gentle moisturiser if it feels dry.",
        "faq": ("Is it the same price in Kollam as on the website?", "Yes. The price is the same for every pin code in Kerala: ₹549 for one jar, ₹999 for two and ₹1,444 for three, with free shipping."),
    },
    {
        "slug": "thiruvananthapuram", "name": "Thiruvananthapuram", "ml": "തിരുവനന്തപുരം", "district": "Thiruvananthapuram", "aka": "Trivandrum",
        "areas": [("Thampanoor / city centre", "695001"), ("Pattom", "695004"), ("Vazhuthacaud", "695014"), ("Kazhakoottam / Technopark", "695582"), ("Neyyattinkara", "695121")],
        "intro": "Thiruvananthapuram, also known as Trivandrum, is Kerala's capital. We deliver to homes and offices across the city, from Pattom and Vazhuthacaud to Kazhakoottam near Technopark, and out to Neyyattinkara. Order online or on WhatsApp, with Cash on Delivery available.",
        "climate": "Trivandrum is warm and humid with strong sun for much of the year, and it gets rain from both the south-west and north-east monsoons. Daily sunscreen and a consistent night routine matter more than how much cream you use.",
        "faq": ("Is 'Trivandrum' the same delivery area as Thiruvananthapuram?", "Yes. Trivandrum and Thiruvananthapuram are the same city. All pin codes in the district get the same price, free shipping and Cash on Delivery."),
    },
]

# Extra per-city content (delivery tips, seasonal notes, second local FAQ)
EXTRA = {
    "kasaragod": {
        "tip": "Many Kasaragod addresses are written in a mix of Malayalam and Kannada place names. Write your house name, the nearest junction or mosque, temple or church, and a phone number the courier can call.",
        "season": "Kasaragod families often order before wedding season and festivals like Onam and Eid. If you're buying for yourself and a family member, Pack of 2 works out to about ₹500 per jar.",
        "faq2": ("I live near the Karnataka border in Manjeshwar. Can I still order?", "Yes. Manjeshwar, Uppala and other border towns are part of Kasaragod district, and delivery works the same way. Use your full Kerala address and pin code at checkout."),
    },
    "kannur": {
        "tip": "Rural Kannur addresses can be hard for couriers to find. Add a landmark such as a school, bus stop or temple, and keep your phone on the day the parcel is out for delivery.",
        "season": "If you are ordering a gift for someone in Kannur while you work outside Kerala, enter their name and Kannur address at checkout and add a note on WhatsApp. Cash on Delivery lets them pay on arrival, or you can pay online in advance.",
        "faq2": ("Can I send Youth Face Cream to a family member in Kannur from another state?", "Yes. Enter their name, Kannur address and phone number at checkout. Choose online payment if you want to pay for it yourself."),
    },
    "kozhikode": {
        "tip": "For city flats in Kozhikode, include the apartment name, floor and flat number. For addresses near Medical College or the beach road, a nearby landmark helps the courier reach you faster.",
        "season": "Kozhikode customers often ask on WhatsApp whether the cream suits oily skin in the monsoon. A small amount spread thinly suits most skin types. If your skin is sensitive, patch test first.",
        "faq2": ("Does the monsoon in Kozhikode delay deliveries?", "Very heavy rain can sometimes slow courier routes. Check the estimated date for your pin code on the product page, and message us on WhatsApp if your parcel seems late."),
    },
    "malappuram": {
        "tip": "Malappuram has many towns with similar place names across different taluks. Always enter the correct six-digit pin code, and add your post office name if you know it.",
        "season": "Orders from Malappuram often go up before Eid and the wedding season. If you need the cream before a specific date, order early and ask us on WhatsApp for a delivery estimate.",
        "faq2": ("Can the parcel be delivered to my shop instead of my house in Malappuram?", "Yes. Use your shop address and pin code at checkout, and add the shop name so the courier can find it."),
    },
    "palakkad": {
        "tip": "Palakkad addresses outside the town can be spread out. Add a landmark like a bus stop, school or temple, and make sure the phone number on the order is one you will answer.",
        "season": "Summer in Palakkad is the season when sunscreen matters most. Keep the cream for night, and use sunscreen every morning before going out.",
        "faq2": ("I'm near the Tamil Nadu border in Palakkad. Is delivery the same?", "Yes. Any Kerala pin code in Palakkad district gets the same price, free shipping and Cash on Delivery."),
    },
    "thrissur": {
        "tip": "If your Thrissur address is near Swaraj Round or a temple area that gets crowded on festival days, add a second landmark and pick a delivery address you can reach easily.",
        "season": "Many Thrissur customers buy a Pack of 2 or 3 to share with family. Pack of 3 works out to about ₹481 per jar, the lowest price per jar.",
        "faq2": ("Do you deliver to Guruvayur and Chalakudy as well as Thrissur city?", "Yes. All of Thrissur district is covered, including Guruvayur, Chalakudy, Irinjalakuda and Kunnamkulam."),
    },
    "kochi": {
        "tip": "Fort Kochi and Mattancherry have narrow lanes and old house numbers, so a landmark helps. For flats in Kakkanad, Edappally or Vyttila, include the tower name and flat number.",
        "season": "Long commutes across Kochi mean daily sun and dust. A consistent night routine, with the cream on clean skin, and sunscreen before you leave usually matter more than any product change.",
        "faq2": ("Can I pay by UPI when the parcel arrives in Kochi?", "Choose Cash on Delivery at checkout. Many couriers in Kochi also accept UPI at the door, but this depends on the delivery person, so keep cash ready just in case."),
    },
    "kottayam": {
        "tip": "Kottayam addresses near the backwaters or in hilly areas around Pala can be harder to reach. Add a landmark and the name of your ward or locality.",
        "season": "Kottayam customers often order before Christmas and the wedding season. If you need the cream by a certain day, ask us on WhatsApp for a delivery estimate for your pin code.",
        "faq2": ("Do you deliver to Pala and Changanassery?", "Yes. Pala, Changanassery, Ettumanoor and Vaikom are all covered, with the same price and free shipping."),
    },
    "alappuzha": {
        "tip": "Some homes in Alappuzha are only reachable by narrow roads along canals. Give a landmark on the main road, such as a jetty, junction or church, and keep your phone on so the courier can call you.",
        "season": "Alappuzha's backwater sun and humidity make it easy to skip sunscreen without noticing. If you spend time near the water, sunscreen is the single most useful habit for your routine.",
        "faq2": ("Can I get delivery to Cherthala or Kayamkulam?", "Yes. Cherthala, Kayamkulam, Haripad and Mavelikkara are all covered across Alappuzha district."),
    },
    "kollam": {
        "tip": "For Kollam addresses near the coast or in inland towns like Punalur, add your post office name and a landmark. It helps the courier when house names repeat in the same area.",
        "season": "Kollam customers often ask which pack to start with. If this is your first time, Pack of 1 lets you patch test and see how your skin responds before buying more.",
        "faq2": ("Which pack should I start with in Kollam?", "Start with Pack of 1 if you are new to the cream. Once you know it suits your skin, Pack of 2 or 3 lowers the price per jar."),
    },
    "thiruvananthapuram": {
        "tip": "For Technopark or office deliveries in Kazhakoottam, include the building name and your company. For homes in the city, add the residents' association name or a nearby landmark.",
        "season": "Trivandrum's two monsoon seasons mean many cloudy days, but UV still reaches your skin. Daily sunscreen protects the even-looking tone you're working towards.",
        "faq2": ("Can I get delivery at my Technopark office in Trivandrum?", "Yes. Enter your office address with the building name and pin code 695582 (Kazhakoottam), and add your company name."),
    },
}
for _c in CITIES:
    _c.update(EXTRA[_c["slug"]])

GEO = {"kasaragod": (12.4996, 74.9869), "kannur": (11.8745, 75.3704), "kozhikode": (11.2588, 75.7804), "malappuram": (11.0510, 76.0711),
       "palakkad": (10.7867, 76.6548), "thrissur": (10.5276, 76.2144), "kochi": (9.9312, 76.2673), "kottayam": (9.5916, 76.5222),
       "alappuzha": (9.4981, 76.3388), "kollam": (8.8932, 76.6141), "thiruvananthapuram": (8.5241, 76.9366)}
for _c in CITIES:
    _c["geo"] = GEO[_c["slug"]]
