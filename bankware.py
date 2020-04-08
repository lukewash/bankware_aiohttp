from aiohttp import web
from handlers.ram_handler import *
# from handlers.db_handler import * - as an alternative, same methods can be implemented with db instead of global vars

routes = web.RouteTableDef()


@routes.post('/transactions')
async def api_create_transaction(request):
    data = await request.json()

    required_keys = ["id", "amount", "currency", "email", "type"]
    for k in required_keys:
        if k not in data.keys():
            return False, WRONG_TRANSACTION_REQ, HTTP_CLIENTERR
    success, msg, status = Transactions.new(data['id'], data['type'], data['currency'], data['amount'], data['email'])
    return web.json_response({STATMSG: msg}, status=status)


@routes.get('/transactions')
async def api_get_transactions(request):
    return web.json_response(Transactions.data(), status=HTTP_OK)


@routes.post('/transactions/commit')
async def api_commit_transaction(request):
    data = await request.json()
    if 'id' in data.keys():
        success, msg, status = Transactions.commit(data['id'])
        return web.json_response({STATMSG: msg}, status=status)
    else:
        return web.json_response({STATMSG: NO_ID_IN_COMMIT}, status=HTTP_CLIENTERR)


@routes.get('/currency')
async def api_list_currencies(request):
    return web.json_response(Currencies.data(), status=HTTP_OK)


@routes.post('/currency')
async def api_create_currency(request):
    data = await request.json()
    if 'name' in data.keys():
        success, msg, status = Currencies.new(data['name'])
        return web.json_response({STATMSG: msg}, status=status)
    else:
        return web.json_response({STATMSG: NO_CURRENCY_NAME}, status=400)


@routes.get('/clients')
async def api_list_clients(request, limit=None, offset=None):
    clientlist = Clients.list()

    if "offset" in request.query.keys():
        offset = abs(int(request.query.getone("offset")))
        clientlist = clientlist[offset:-1]

    if "limit" in request.query.keys():
        limit = abs(int(request.query.getone("limit")))
        clientlist = clientlist[0:limit]

    result = {}

    for email in clientlist:
        result[email] = Clients.data(email)

    return web.json_response({"limit": limit, "offset": offset, "clients": result})


@routes.post('/client')
async def api_create_client(request):
    data = await request.json()
    if 'email' in data.keys():
        success, msg, status = Clients.new(data['email'])
        return web.json_response({STATMSG: msg}, status=status)
    else:
        return web.json_response({STATMSG: NO_EMAIL}, status=HTTP_CLIENTERR)


@routes.get('/client/{clientmail}')
async def api_get_client(request):
    email = "{}".format(request.match_info['clientmail'])
    if email not in Clients.list():
        return web.json_response({STATMSG: NO_SUCH_CLIENT}, status=HTTP_NOTFOUND)
    else:
        return web.json_response(Clients.data(email), status=HTTP_OK)

app = web.Application()
app.router.add_routes(routes)


if __name__ == '__main__':

    web.run_app(app)
