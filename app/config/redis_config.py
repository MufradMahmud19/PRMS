from flask_caching import Cache

cache = Cache()

def init_redis(app):
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_HOST'] = 'redis-11953.c300.eu-central-1-1.ec2.redns.redis-cloud.com'
    app.config['CACHE_REDIS_PORT'] = 11953
    app.config['CACHE_REDIS_PASSWORD'] = 'SDfem40nfr766rsvkCHuWJAbGcSAr2Ye'
    app.config['CACHE_REDIS_DB'] = 0
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes default timeout
    
    cache.init_app(app) 