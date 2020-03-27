from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from hub.models import NGO
from mobilpay.models import PaymentOrder, PaymentResponse
from mobilpay.mobilpay.request import Request
from mobilpay.mobilpay.payment.request.crc import Crc
from .utils import get_and_send_request
from hub import utils

from urllib.parse import unquote, quote
import requests
from pprint import pprint


def initialize_payment(request, order):
    # ngo = NGO.objects.get(name="Code4")
    order = PaymentOrder.objects.get(order_id=order)
    ngo = order.ngo
    base_path = f"{request.scheme}://{request.META['HTTP_HOST']}"
    data, env_key = get_and_send_request(base_path, order)

    return render(
        request,
        "mobilpay/initialize_payment.html",
        {"data": data, "env_key": env_key, "base_path": base_path, "ngo": ngo, "order": order,},
    )


def response(request, order):
    order = PaymentOrder.objects.get(order_id=order)
    return render(request, "mobilpay/response.html", {"order": order})


@csrf_exempt
def confirm(request, order):
    pprint(request.POST)
    order = PaymentOrder.objects.get(order_id=order)
    ngo = order.ngo
    error_code = 0
    error_type = Request.CONFIRM_ERROR_TYPE_NONE
    error_message = ""
    payment_response = PaymentResponse()
    payment_response.payment_order = order
    base_path = f"{request.scheme}://{request.META['HTTP_HOST']}"

    if request.method == "POST":

        """calea catre cheia privata aflata pe serverul dumneavoastra"""
        private_key_path = order.ngo.mobilpay_private_key.path

        """verifica daca exista env_key si data in request"""

        env_key = request.POST.get("env_key")
        env_data = request.POST.get("data")
        # env_key = post['env_key']
        # env_data = post['data']
        print(env_key)
        print("-----")
        print(env_data)

        """daca env_key si env_data exista, se incepe decriptarea"""
        if env_key is not None and len(env_key) > 0 and env_data is not None and len(env_data) > 0:
            print("IN!")
            try:
                """env_key si data trebuie parsate pentru ca vin din url, se face cu function unquote din urllib

                in cazul in care decriptarea nu este reusita, raspunsul v-a contine o eroare si mesajul acesteia
                """
                obj_pm_request = Request().factory_from_encrypted(unquote(env_key), unquote(env_data), private_key_path)

                """obiectul notify contine metode pentru setarea si citirea proprietatilor"""
                print("obj_pm_request", obj_pm_request)
                print(obj_pm_request.get_notify())
                notify = obj_pm_request.get_notify()
                if int(notify.errorCode) == 0:
                    payment_response.action = notify.action
                    """
                    orice action este insotit de un cod de eroare si de un mesaj de eroare. Acestea pot fi citite
                    folosind error_code = obj_pm_req.get_notify().errorCode
                    respectiv error_message = obj_pm_req.get_notify()errorMessage
                    pentru a identifica ID-ul comenzii pentru care primim rezultatul platii folosim
                    order_id = obj_pm_req.get_order_id()
                    """
                    if notify.action == "confirmed":
                        print("CONFIRMED!!")
                        """ 
                        cand action este confirmed avem certitudinea ca banii au plecat din contul posesorului de
                        card si facem update al starii comenzii si livrarea produsului
                        update DB, SET status = "confirmed/captured"
                        """
                        order.success = True
                        order.save()
                        error_message = notify.errorMessage
                        for user in order.ngo.users.all():
                            print(f"send mail to ngo: {user.email}")
                            utils.send_email(
                                template="mail/new_donation.html",
                                context={"base_path": base_path},
                                subject="[RO HELP] Donație inregistrată",
                                to=user.email,
                            )
                        print(f"send mail to order: {order.email}")
                        utils.send_email(
                            template="mail/new_payment.html",
                            context={"ngo": ngo, "base_path": base_path},
                            subject="[RO HELP] Plată confirmată",
                            to=order.email,
                        )
                    elif notify.action == "confirmed_pending":
                        """ 
                        cand action este confirmed_pending inseamna ca tranzactia este in curs de verificare
                        antifrauda. Nu facem livrare/expediere. In urma trecerii de aceasta verificare se va primi o
                        noua notificare pentru o actiune de confirmare sau anulare.
                        update DB, SET status = "pending"
                        """
                        error_message = notify.errorMessage
                    elif notify.action == "paid_pending":
                        """
                        cand action este paid_pending inseamna ca tranzactia este in curs de verificare. 
                        Nu facem livrare/expediere. In urma trecerii de aceasta verificare se va primi o noua 
                        notificare pentru o actiune de confirmare sau anulare.
                        update DB, SET status = "pending"
                        """
                        error_message = notify.errorMessage
                    elif notify.action == "paid":
                        """cand action este paid inseamna ca tranzactia este in curs de procesare.
                        Nu facem livrare/expediere. In urma trecerii de aceasta procesare se va primi o noua
                        notificare pentru o actiune de confirmare sau anulare.
                        update DB, SET status = 'open/preauthorized'"""
                        error_message = notify.errorMessage
                    elif notify.action == "canceled":
                        """cand action este canceled inseamna ca tranzactia este anulata. Nu facem livrare/expediere.
                        update DB, SET status = 'canceled'"""
                        error_message = notify.errorMessage
                    elif notify.action == "credit":
                        """
                        cand action este credit inseamna ca banii sunt returnati posesorului de card.
                        Daca s-a facut deja livrare, aceasta trebuie oprita sau facut un reverse.
                        update DB, SET status = 'refunded'
                        """
                        error_message = notify.errorMessage
                    else:
                        error_type = Request.CONFIRM_ERROR_TYPE_PERMANENT
                        error_code = Request.ERROR_CONFIRM_INVALID_ACTION
                        error_message = "mobilpay_refference_action paramaters is invalid"
                else:
                    """  # update DB, SET status = "rejected"""
                    error_message = notify.errorMessage
                    error_type = Request.CONFIRM_ERROR_TYPE_TEMPORARY
                    error_code = notify.errorCode
            except Exception as e:
                error_type = Request.CONFIRM_ERROR_TYPE_TEMPORARY
                error_message, error_code = e.args[0], e.args[1]
        else:
            error_type = Request.CONFIRM_ERROR_TYPE_PERMANENT
            error_code = Request.ERROR_CONFIRM_INVALID_POST_PARAMETERS
            error_message = "mobilpay.ro posted invalid parameters"
    else:
        error_type = Request.CONFIRM_ERROR_TYPE_PERMANENT
        error_code = Request.ERROR_CONFIRM_INVALID_POST_METHOD
        error_message = "invalid request method for payment confirmation"
    payment_response.error_code = error_code
    payment_response.error_type = error_type
    payment_response.error_message = error_message
    payment_response.save()
    crc = Crc(error_code, error_type, error_message).create_crc()
    print('*****')
    print(crc.toprettyxml(indent="\t", encoding="utf-8"))
    print('*****')
    return HttpResponse(crc.toprettyxml(indent="\t", encoding="utf-8"), content_type='text/xml')
