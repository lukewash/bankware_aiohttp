import aiohttp
import datetime
import asyncio
import random
import string
import requests

IP = '127.0.0.1'
PORT = 8080
CURRLIST = []
HTTP_CREATED, HTTP_OK = 201, 200


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
        assert (response.status == HTTP_CREATED)
        return response


def test_create_currencies():
    currlist()

    start = now()
    tasks = [create_currency(c) for c in CURRLIST]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))
    elapsed = ms_since(start)

    print(f"Sent {len(CURRLIST)} currencies to bankware in {elapsed} ms")


def test_get_currencies():
    resp = requests.get(f"http://{IP}:{PORT}/currency")
    print("HTTP status is OK")
    assert resp.status_code == HTTP_OK

    print("Bankware contains valid amount of currencies")
    assert len(list(resp.json().keys())) == len(CURRLIST)

