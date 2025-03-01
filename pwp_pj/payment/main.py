import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection,HashModel
from starlette.requests import Request
import requests

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


class Order(HashModel):
    id: str
    price: float
    quantity: int  
    fee : float
    total : float
    status : str  # pending, paid, failed
    time: str = time.strftime("%Y-%m-%d %H:%M:%S")

    class Meta:
        database = redis


@app.get("/orders/{pk}")
def get_order(pk: str):
    return Order.get(pk)


@app.get("/orders")
def all_orders():
    return [Order.get(pk) for pk in Order.all_pks()]

@app.post('/orders')
async def create_order(request: Request, background_task: BackgroundTasks): #id,quantity

    body = await request.json()

    req = requests.get('http://127.0.0.1:8000/products/%s' % body['id'])
    product = req.json()
    order = Order(
        id=body['id'],
        price=product['price'],
        quantity=body['quantity'],
        fee=0.1 * product['price'],
        total=product['price']*body['quantity']*1.1,
        status='pending'
    )
    order.save()
    background_task.add_task(order_completed, order)
    return order

def order_completed(order: Order):
    time.sleep(5)
    order.status = 'paid'
    order.save()
    redis.xadd('order_completed', order.dict(),'*')
