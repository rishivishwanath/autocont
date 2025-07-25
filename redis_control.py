import redis
import redis

r = redis.Redis(
    host='redis-19355.crce179.ap-south-1-1.ec2.redns.redis-cloud.com',
    port=19355,
    decode_responses=True,
    username="default",
    password="wHonTPQpKK96o60fNAfRhnqSwniKjxL0",
)
print(r.get("num"))