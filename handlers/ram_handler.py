from static.respcodes import *
from static.messages import *
from utils.utils import *

CLIENTS = {}
CURRENCIES = {}
TRANSACTIONS = {}


class Clients:

    @staticmethod
    def new(email):
        if email in Clients.list():
            return False, CLIENT_EXISTS, HTTP_CLIENTERR
        if not valid_email(email):
            return False, BAD_EMAIL, HTTP_CLIENTERR
        else:
            balances = {}
            for c in Currencies.list():
                balances[c] = 0.0

            client = {"balances": balances, "deposits": [], "withdrawals": [], }
            CLIENTS[email] = client
            msg = "OK: {} client added".format(email)
            return True, msg, HTTP_CREATED

    @staticmethod
    def list():
        return list(CLIENTS.keys())

    @staticmethod
    def data(email):
        client = CLIENTS[email].copy()
        client_transaction_ids = set(client['deposits'] + client['withdrawals'])
        client['deposits'] = []
        client['withdrawals'] = []
        for transaction_id in client_transaction_ids:
            current_transaction = Transactions.data_byid(transaction_id)
            current_transaction['id'] = transaction_id
            t_type = current_transaction['type']
            current_transaction.pop('type')
            client[t_type].append(current_transaction)

        return {email: client}


class Currencies:

    @staticmethod
    def new(name):
        if not valid_currency(name):
            return False, BAD_CURRENCY, HTTP_CLIENTERR
        if name not in CURRENCIES:
            CURRENCIES[name] = 0.0
            return True, NEW_CURRENCY_OK.format(name), HTTP_CREATED
        else:
            return False, CURRENCY_EXISTS, HTTP_CLIENTERR

    @staticmethod
    def list():
        return list(CURRENCIES.keys()).copy()

    @staticmethod
    def data():
        return CURRENCIES




class Transactions:
    #TODO add rollback
    @staticmethod
    def new(t_uuid, t_type, currency, amount, email, ):
        if not valid_uuid(t_uuid):
            return False, BAD_UUID, HTTP_CLIENTERR

        if t_uuid in Transactions.list():
            return False, TRANSACTION_EXISTS, HTTP_CLIENTERR

        if t_type not in ['withdrawals', 'deposits']:
            return False, NO_SUCH_TTYPE, HTTP_CLIENTERR

        if currency not in Currencies.list():
            return False, NO_SUCH_CURRENCY, HTTP_CLIENTERR

        if email not in Clients.list():
            return False, NO_SUCH_CLIENT, HTTP_CLIENTERR

        TRANSACTIONS[t_uuid] = {
            "timestamp": timestamp(),
            "currency": currency,
            "amount": abs(float(amount)) if t_type == 'deposits' else abs(float(amount)) * -1.0,
            "commited": False,
            "client": email,
            "type": t_type
        }

        CLIENTS[email][t_type].append(t_uuid)  # IMPORTANT
        return True, TRANSACTION_CREATED, HTTP_CREATED

    @staticmethod
    def list():
        return list(TRANSACTIONS.keys())

    @staticmethod
    def data():
        return TRANSACTIONS.copy()

    @staticmethod
    def data_byid(t_uuid):
        return TRANSACTIONS[t_uuid].copy()

    @staticmethod
    def commit(t_uuid):
        if t_uuid not in Transactions.list():
            return False, NO_SUCH_TRANSACTION, HTTP_NOTFOUND

        t = TRANSACTIONS[t_uuid]

        if t['commited']:
            return False, ALREADY_COMMITED, HTTP_FORBIDDEN

        currency = t['currency']
        client = t['client']
        amount = t['amount']
        t_type = t['type']

        if currency not in CLIENTS[client]['balances'].keys():  # TODO update customers on creating currency
            CLIENTS[client]['balances'][currency] = 0.0

        if CLIENTS[client]['balances'][currency] + amount < 0:
            return False, INSUFFICENT_FUNDS, HTTP_FORBIDDEN
        else:
            CURRENCIES[currency] += amount
            TRANSACTIONS[t_uuid]['commited'] = True
            CLIENTS[client]['balances'][currency] += amount
            t.pop('client', None)

            return True, TRANSACTION_COMMITED_OK, HTTP_OK
