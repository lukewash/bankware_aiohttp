import aiohttp
import datetime
import asyncio
import random
import string

IP = '127.0.0.1'
PORT = 8080
CURRLIST = []
MESSAGES = []
HTTP_CREATED = 201


def now():
    return datetime.datetime.now()


def ms_since(start):
    elapsed = now() - start
    ms = elapsed.total_seconds() * 1000
    return float(ms)


def random_currency():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase) for _ in range(3))


def currlist(n=1000):
    while len(CURRLIST) < n:
        c = random_currency()
        if c not in CURRLIST:
            CURRLIST.append(c)
    assert len(CURRLIST) == n
    CURRLIST.sort()
    return (CURRLIST)


async def create_currency(currency_name):
    async with aiohttp.request('POST', f"http://{IP}:{PORT}/currency", json={"name": f"{currency_name}"}) as r:
        response = await r
        msg = f"Request for creating '{currency_name}' returned {response.status}"
        MESSAGES.append(msg)
        assert (response.status == HTTP_CREATED)


def test_main():
    currlist()

    start = now()
    tasks = [create_currency(c) for c in CURRLIST]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    elapsed = ms_since(start)
    loop.close()
    print(f"Sent {len(CURRLIST)} currencies to bankware in {elapsed} ms")
