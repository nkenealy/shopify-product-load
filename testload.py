import requests, json

github_url = "http://localhost:5000/api/v1.0/products/"
headers = {'content-type': 'application/json'}
data =  json.dumps( {"title": "2006 Audi A6 Midsize Sedan", "pos_product_id": 4100})
r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
print r.json
data = json.dumps( {"title": "2006 BMW 5Series Midsize Sedan", "pos_product_id": 4101})
r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
print r.json
data =  json.dumps( {"title": "2006 Cadillac STS Large Sedan", "pos_product_id": 4102, "title": "2006 Audi A6 Midsize Sedan"})
r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
print r.json


github_url = "http://localhost:5000/api/v1.0/products/variants/"
data =  json.dumps( {"sku": "CARACC01", "pos_product_id": 4100, "title": "2006 Audi A6 Midsize Sedan"})
r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
print r.json
data =  json.dumps({"sku": "CARACC02", "pos_product_id": 4101, "title": "2006 BMW 5Series Midsize Sedan"})
r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
print r.json
data =  json.dumps({"sku": "CARACC03", "pos_product_id": 4102, "title": "2006 Cadillac STS Large Sedan"})
r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
print r.json


github_url = "http://localhost:5000/api/v1.0/products/images/"
data =  json.dumps( {"pos_product_id": 4100, "src": "mylovelyaudo.jpg"})
r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
print r.json
data =  json.dumps({"pos_product_id": 4101, "title": "mylovelyBMW.jpg"})
r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
print r.json
data =  json.dumps({"pos_product_id": 4102, "title": "mylovelycadillax.jpg"})
r = requests.post(github_url, data, headers=headers, auth=('neilkenealy@gmail.com', 'n3wmediam3d'))
print r.json


