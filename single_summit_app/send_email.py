import os

import sendgrid

from django.conf import settings
import json
from rest_framework import status


def send_email_sendgrid_template(from_email=settings.CONTACT_US_EMAIL, to_email="", subject="", data={}, template=""):
    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        message = sendgrid.Mail(
            from_email=from_email,
            to_emails=to_email,
            subject=subject
        )
        message.dynamic_template_data = data
        message.template_id = template
        status = sg.send(message)
        return [status]
    except Exception as e:
        return e


def send_email_request_sender_address(user):
    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        if not user.is_sendgrid_verified and not user.sendgrid_token:
            data = {
                "nickname": f'{user.name} {user.sure_name}',
                "from_email": user.email,
                "from_name": f'{user.name} {user.sure_name}',
                "reply_to": user.email,
                "reply_to_name": f'{user.name} {user.sure_name}',
                "address": "1234 Fake St",
                "city": "San Francisco",
                "country": "USA",
            }
            response = sg.client.verified_senders.post(
                request_body=data
            )
            if response.status_code == 201:
                resp = json.loads(response.body.decode("utf-8"))
                user.sendgrid_token = resp['id']
                user.save(update_fields=['sendgrid_token'])
                return True
            return False
        else:
            return True
    except Exception as e:
        print(str(e))



def verify_sender_address(user):
    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        if user.is_sendgrid_verified:
            return [
                True,
                status.HTTP_200_OK,
                "Email has already been verified."
            ]
        elif user.sendgrid_token:
            get_sendgrid_obj = sg.client.verified_senders.get(query_params={
                "id": user.sendgrid_token
            })
            if len(get_sendgrid_obj.to_dict['results']) > 0:
                if not get_sendgrid_obj.to_dict['results'][0]['verified']:
                    response = sg.client.verified_senders.resend._(user.sendgrid_token).post()
                    if response.status_code == 204:
                        return [
                            True,
                            status.HTTP_201_CREATED,
                            "Sendgrid Email Verification Resent."
                        ]
                    else:
                        return [
                            False,
                            status.HTTP_422_UNPROCESSABLE_ENTITY,
                            "Unable to send the verification email at this time."
                        ]
                else:
                    user.is_sendgrid_verified = True
                    user.save(update_fields=['is_sendgrid_verified'])

                    send_email_sendgrid_template(
                        from_email=settings.CONTACT_US_EMAIL,
                        to_email=user.email,
                        subject="Invitation for Transplant Connection",
                        template=settings.SENDGRID_VERIFY_SALES_REP_EMAIL
                    )
                    return [
                        True,
                        status.HTTP_200_OK,
                        "Email has been verified successfully."
                    ]
            else:
                return [
                    False,
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "Something went wrong please contact your admin"
                ]
        else:
            return True
    except Exception as e:
        print(str(e))


def get_and_verify_sender_address(user):
    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        if user.is_sendgrid_verified:
            return [
                True,
                status.HTTP_200_OK,
                "Email has already been verified."
            ]
        elif user.sendgrid_token:
            get_sendgrid_obj = sg.client.verified_senders.get(query_params={
                "id": user.sendgrid_token
            })
            if len(get_sendgrid_obj.to_dict['results']) > 0:
                if not get_sendgrid_obj.to_dict['results'][0]['verified']:
                    return [
                        False,
                        status.HTTP_422_UNPROCESSABLE_ENTITY,
                        "Email not verified yet. Please wait."
                        ]
                else:
                    user.is_sendgrid_verified = True
                    user.save(update_fields=['is_sendgrid_verified'])
                    send_email_sendgrid_template(
                        from_email=settings.CONTACT_US_EMAIL,
                        to_email=user.email,
                        subject="Invitation for Transplant Connection",
                        template=settings.SENDGRID_VERIFY_SALES_REP_EMAIL
                    )
                    return [
                        True,
                        status.HTTP_200_OK,
                        "Email has been verified successfully."
                    ]
            else:
                return [
                    False,
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    "Something went wrong please contact your admin"
                ]
        else:
            return [
                False,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Something went wrong please. Try to login again"
            ]

    except Exception as e:
        print(str(e))
        return False

def delete_verify_sender_address(id):
    try:
        sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.client.verified_senders._(id).delete()
    except Exception as e:
        print(str(e))

