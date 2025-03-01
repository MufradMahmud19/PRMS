from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection,HashModel
import time
app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)


redis = get_redis_connection(
    host='redis-13980.c339.eu-west-3-1.ec2.redns.redis-cloud.com',
    port=13980,
    password='A9EAM68RA1HgkYsP4jxFQctXE5ZRuaiP',
    decode_responses=True
)

class Product(HashModel):
    name: str
    price: float
    quantity: int  
    time: str = time.strftime("%Y-%m-%d %H:%M:%S")
    class Meta:
        database = redis
       


@app.post('/products')
def create_product(product: Product):
    
    return product.save()

def format_product (pk:str):
    product = Product.get(pk)
    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }

@app.get('/products')
def all_products():
    
    return [format_product(pk) for pk in Product.all_pks()]


@app.get('/products/{pk}')
def get_product(pk: str):
    return Product.get(pk)

@app.delete('/products/{pk}')
def delete_product(pk: str):
    return Product.delete(pk)
