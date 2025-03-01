from main import redis
from main import Order
import time
key='refund_order'
group='payment_group'

try:
    redis.xgroup_create(key, group)
except:
    print('Group already exists')

while True:
    try:
        reasults = redis.xreadgroup(group, key,{key:'>'},None)
        
        if reasults != []:
            print(reasults)
            for reasult in reasults:
                try:
                   obj=reasult[1][0][1]
                   redis.xack(key, group, reasult[1][0][0])
                   print(obj)
                except Exception as e:
                     print(str(e))
                order=Order.get(obj['id'])
                order.status= "refunded"
                order.save()
               
    except Exception as e:
        print(str(e))
        time.sleep(1)