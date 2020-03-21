from zeep import Client
from pprint import pprint
import hashlib
import base64


wsdl = "https://secure.mobilpay.ro/api/payment2/?wsdl"
wsdl = "http://sandboxsecure.mobilpay.ro/api/payment2/?wsdl"
client = Client(wsdl)


def parseElements(elements):
    all_elements = {}
    for name, element in elements:
        all_elements[name] = {}
        all_elements[name]["optional"] = element.is_optional
        if hasattr(element.type, "elements"):
            all_elements[name]["type"] = parseElements(
                element.type.elements)
        else:
            all_elements[name]["type"] = str(element.type)

    return all_elements


interface = {}

for service in client.wsdl.services.values():
    interface[service.name] = {}
    for port in service.ports.values():
        interface[service.name][port.name] = {}
        operations = {}
        for operation in port.binding._operations.values():
            operations[operation.name] = {}
            operations[operation.name]["input"] = {}
            elements = operation.input.body.type.elements
            operations[operation.name]["input"] = parseElements(elements)

        interface[service.name][port.name]["operations"] = operations

# print("*****")
pprint(operations["doPay"]["input"]["request"]["type"].keys())
pprint(operations["doPay"]["input"]["request"]["type"]["order"])


password = "TCE9-LS89-XVHG-16MN-5X9P"
password = "0CA764E091AD059C9F60ED1DD02307E8"
password = "r0b0d3v31m0b1lp@y"
username = "costinbleotu"

# pass_hash = hashlib.sha256(password.encode()).hexdigest()
# pass_hash = str(base64.b64encode(pass_hash.encode()), 'utf-8')

pass_md5 = hashlib.md5(password.encode()).hexdigest()
order = {
    "amount": 10.00,
    "id":  "TEST123",
    "currency": "RON"
}

account = {
    "user_name": username, "id": "TCE9-LS89-XVHG-16MN-5X9P",
    "confirm_url": "http://dev.rohelp.ro:8000/ro/mobilpay/response",
    "return3d_url": "http://dev.rohelp.ro:8000/ro/mobilpay/confirm",
    "customer_ip": "127.0.0.1"
}
hash_string = pass_md5.upper() + order["id"] + f"{order['amount']:.2f}" + order["currency"] + account["id"]
print(hash_string)
account["hash"] =  hashlib.sha1(hash_string.encode()).hexdigest().upper()
print(account["hash"])
# $string = strtoupper(md5($pass)).$request->order->id.$request->order->amount.$request->order->currency.$request->account->id
# $request->account->hash = strtoupper(sha1($string))

# Deci acel hash nu este doar md5(pass) ci include si suma, moneda, contul
# (sac id, acel XXXX-YYYY-..) si order id (id-ul vostru adica). La urma se
# aplica si un sha1. Plus ca md5(parola) e facuta uppercase.
# Intrucat voi faceti apelul asta pentru a obtine un link unde sa trimiteti userul, customer_ip nu e relevant, pune 127.0.0.1 or so, el va fi suprascris in procesul de plata cu cel adevarat.
# URL - ul de confirm este cel unde primesti informari de la noi privitor la starea comenzii. La return este intors userul dupa plata. Mi - am dat seama ca pentru a putea citi informatiile la confirm veti avea nevoie de privatekey - ul acestui SAC. iar "desfacerea" IPNului - avand cheia - se face cu ajutorul functiei de la https:
    # L50 si pe modelul de la
    # https://github.com/mobilpay/python/blob/master/mobilpay/request.py#L68
    # //github.com / mobilpay / python / blob / master / mobilpay / util / encrypt_data.py


doPay = client.service.doPay(
    request={
        "order": order,
        "account": account
    })


# "confirm_url" : False, "type": "String(value)"},
# "customer_ip" : {"optional": False, "type": "String(value)"},
# "hash": {"optional": False, "type": "String(value)"},
# "id": {"optional": False, "type": "String(value)"},
# "return3d_url": {"optional": False, "type": "String(value)"},
# "user_name": {"optional": False, "type": "String(value)"}}}
