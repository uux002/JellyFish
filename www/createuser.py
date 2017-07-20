import orm
import asyncio
from models import User, Blog, Comment

async def createUser(loop):
    await orm.create_pool(loop = loop,user='awesome',password='jkilopqcv0968',database='awesome')
    u = User(name='Test', email='test@example.com', passwd='12345678', image='about:blank')
    await u.save()


loop = asyncio.get_event_loop()
loop.run_until_complete(createUser(loop))
loop.close()







