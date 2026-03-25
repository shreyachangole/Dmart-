# =============================================================================
#  D-MART PRODUCT CATALOGUE
#  ─────────────────────────────────────────────────────────────────────────────
#  To ADD a product    : copy any block below, change barcode + details
#  To REMOVE a product : delete its block
#  To UPDATE a product : change the value directly
#
#  Fields:
#    name       – Display name shown on screen and invoice
#    price      – Price in INR (without GST)
#    code       – Internal product code (also searchable)
#    category   – Product category
#    brand      – Brand name
#    image_url  – Direct image URL (replace with any public image URL)
#
#  NOTE: GST is fixed at 5% for ALL products (set in app.py → GST_RATE)
# =============================================================================
 
PRODUCTS = {
 
    # ── EXISTING PRODUCTS ─────────────────────────────────────────────────────
 
    "8901234567890": {
        "name":      "Comfort After Wash Lily Fresh Fabric Conditioner 2L",
        "price":     350.00,
        "code":      "CFL001",
        "category":  "Laundry Care",
        "brand":     "Comfort",
        "image_url": "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcR858EyktUTKF5tDdadxQ61ZxVGvm08XZmGf2fTtBaxemRk15njENEj6d5uKvwq9aDhD_ULfXBrF1BRImsG-cWnZDitYYLa"
    },
 
    "8902345678901": {
        "name":      "Surf Excel Easy Wash Detergent Powder 1kg",
        "price":     135.00,
        "code":      "SRF002",
        "category":  "Laundry Care",
        "brand":     "Surf Excel",
        "image_url": "https://hbkirana.in/wp-content/uploads/2025/03/61ak1gbTTXL._SL1000-2.webp"
    },
 
    "8903456789012": {
        "name":      "India Gate Basmati Rice 1kg",
        "price":     220.00,
        "code":      "IGB003",
        "category":  "Staples",
        "brand":     "India Gate",
        "image_url": "https://m.media-amazon.com/images/I/91aNKCj+l-L.jpg"
    },
 
    "8904567890123": {
        "name":      "Bella Vita CEO Man Eau De Parfum 100ml",
        "price":     499.00,
        "code":      "BVT004",
        "category":  "Personal Care",
        "brand":     "Bella Vita",
        "image_url": "https://m.media-amazon.com/images/I/51hJGmzG9PL._AC_UF1000,1000_QL80_.jpg"
    },
 
    "8905678901234": {
        "name":      "Amul Butter 500g",
        "price":     285.00,
        "code":      "AMU005",
        "category":  "Dairy",
        "brand":     "Amul",
        "image_url": "https://www.bbassets.com/media/uploads/p/l/104864_8-amul-butter-pasteurised.jpg"
    },
 
    "8906789012345": {
        "name":      "Tata Salt 1kg",
        "price":      25.00,
        "code":      "TTS006",
        "category":  "Staples",
        "brand":     "Tata",
        "image_url": "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcS7JeVeKO84sTLPuKbv0dVWD7e7rTnGAUtqLHoFFieORh_Oc14S7hv1c2Zz1C0iF_TEFNiJYKCL6Kqhs2mnzZNvUGa3He-l"
    },
 
    "8907890123456": {
        "name":      "Maggi 2-Minute Noodles Family Pack 832g",
        "price":      72.00,
        "code":      "MGI007",
        "category":  "Instant Food",
        "brand":     "Maggi",
        "image_url": "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcQBxXZYDHJvUeqt2NEenO6gjqJZ1chimI-Bi1NLbkHFEs3EIG4JBsXOyRA_A40sEI-sD2kf1Y_0crslimsLh97Bpjn6t2ns"
    },
 
    "8908901234567": {
        "name":      "Colgate MaxFresh Toothpaste 300g",
        "price":     190.00,
        "code":      "CLG008",
        "category":  "Oral Care",
        "brand":     "Colgate",
        "image_url": "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcTlwN_5USxVVw96yJpq9iIFGeUOw4WZqBT1bLwzYzo-q-JCfvy3HTWBL46bp6P3WA_H8mrf6G_579-HkiFdZN5_QNq7VGZsRQ"
    },
 
    "8909012345678": {
        "name":      "Real Fruit Power Orange Juice 1L",
        "price":     110.00,
        "code":      "RFP009",
        "category":  "Beverages",
        "brand":     "Real",
        "image_url": "https://www.jiomart.com/images/product/original/490001259/real-fruit-power-orange-juice-1-l-product-images-o490001259-p490001259-0-202511061646.jpg"
    },
 
    "8900123456789": {
        "name":      "Fortune Sunflower Oil 1L",
        "price":     132.00,
        "code":      "FSO010",
        "category":  "Cooking Oil",
        "brand":     "Fortune",
        "image_url": "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcRAasxHif6eUiCiEtXaYUJr-pem9iXGTfhBcMF7lDTbkyARSR0gbW-4d2O7cytPuPPRgGTrTXHqEzmLYpyChLkjeZlvSnRcl8XjPfYXJDj19QWuWWcZRsk1Iw"
    },
 
    "8906069401388": {
        "name":      "Veeba Creamy Peanut Butter 350g",
        "price":     159.00,
        "code":      "VBA011",
        "category":  "Spreads",
        "brand":     "Veeba",
        "image_url": "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcREL3pVM_3Kcg9VCLCqGt9kBdOuNUyUg7Vu6sIL7GZ5rX2S1FD_THJkhait-3eVFbrYhcYy2XXtHhiTGuaYzXGAEkcCKdT6I5A7KoTK85ENgs4a1XMz6SG4zg"
    },
 
    "8908018477215": {
        "name":      "FoxTale Vitamin C 15% Face Serum 50ml",
        "price":     549.00,
        "code":      "FXT012",
        "category":  "Skincare",
        "brand":     "FoxTale",
        "image_url": "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcSMEPrI73TdbABtTemr5L4EQuHT9cLz-9JURZarjHXJHDXUgwrFetcfOh6FoRAc64mLq7xqbzxYA9x49iOEILlRburIvgrs7DnPABOs4RIqLRdfSUbS4GZd0LE"
    },
 
    "8904417317244": {
        "name":      "Mamaearth Rice & Niacinamide Body Lotion 400ml",
        "price":     211.00,
        "code":      "MME013",
        "category":  "Body Care",
        "brand":     "Mamaearth",
        "image_url": "https://encrypted-tbn1.gstatic.com/shopping?q=tbn:ANd9GcRSyxE1y4jPo6qcP__8lLR1yt3yLIex5rqJJ4vY7rgj8o9rrzWVhCvtWnUFHb5FS25MaceO3-QVPgzlZ7LytI7cKLm_i32RgeucVF8ZLM0lkJRbrunXfqUB5g"
    },
 
    "8901764082405": {
        "name":      "Kinley Packaged Drinking Water 1L",
        "price":      20.00,
        "code":      "KNL014",
        "category":  "Beverages",
        "brand":     "Kinley",
        "image_url": "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcQT8JHiEr-oyLTr56Hk__5Y3Foso-M8vPzBxlSTvQdTg0-pE7_UPkry1Vlv5lSZGKfJLIsN5tn1Sm6n0k0_-GteGZoC8LL5i_Y6_5Irx29A5atWXAb-a3iTYg"
    },
 
    "8906117364016": {
        "name":      "Country Delight Dark Choco Peanut Butter 180g",
        "price":     200.00,
        "code":      "CDL015",
        "category":  "Spreads",
        "brand":     "Country Delight",
        "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRVe3jvJubiru27p9SRcUZ_Gg4X2S_jnuiPhg&s"
    },
 
}
 
# =============================================================================
#  COUPON CODES
#  type: "percent" → deducts % of total   |   "flat" → deducts fixed Rs. amount
# =============================================================================
 
COUPONS = {
    "DMART10":  { "type": "percent", "value": 10,  "desc": "10% off on total bill" },
    "DMART50":  { "type": "flat",    "value": 50,  "desc": "Rs.50 flat discount"   },
    "SAVE100":  { "type": "flat",    "value": 100, "desc": "Rs.100 flat discount"  },
    "WELCOME5": { "type": "percent", "value": 5,   "desc": "5% welcome discount"   },
}
 
# =============================================================================
#  STORE INFO
# =============================================================================
 
STORE = {
    "name":    "D-mart",
    "address": "Shri Krupa Colony, Sai Nagar, Amravati, Maharashtra - 444607",
    "phone":   "+91 022 3340 0500",
    "gstin":   "27AABCD1234E1Z6",
    "upi_id":  "sakshimore44422-1@okicici",
}