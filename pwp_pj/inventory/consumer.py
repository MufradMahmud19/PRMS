from main import redis
from main import Product
import time
key='order_completed'
group='inventory_group'

try:
    redis.xgroup_create(key, group)
except:
    print('Group already exists')

while True:
    try:
        reasults = redis.xreadgroup(group, key,{key:'>'},None)
        
        if reasults != []:
            for reasult in reasults:
               
                
                try:
                   obj=reasult[1][0][1]
                   redis.xack(key, group, reasult[1][0][0])
                   print(obj)
                except Exception as e:
                     print(str(e))
                try:
                    product=Product.get(obj['id'])
                    print(product)
                    product.quantity-= int(obj['quantity'])
                    product.save()
                
                except:
                    redis.xadd('refund_order', obj, '*')
                

        

    except Exception as e:
        print(str(e))
        time.sleep(1)