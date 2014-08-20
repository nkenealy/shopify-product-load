import shopify
shop_url = "https://3cf6a1e0b9b04c04092cb8ace60937f6:8224d17b2bce753a61537a0d2f44ec29@neil-test-shop.myshopify.com/admin"
shopify.ShopifyResource.set_site(shop_url)
shop = shopify.Shop.current
new_product = shopify.Product()
new_product.title = "Dodge 22000 Freestyle"
new_product.product_type = "Snowcar"
new_product.vendor = "Barton"
success = new_product.save()