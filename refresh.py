import requests, json

url = "https://shop.myshopify.com/admin/oauth/access_token.json"

data = { "client_id": "3b41c62bfa2c9da3fac17748448f3b69","client_secret": "692c26e565939a9f683f8f889168c3a8","refresh_token": "aebf5b50e91f5ecbaa84d0f0643276a0" }
r = requests.post(url,data)
print r.json

