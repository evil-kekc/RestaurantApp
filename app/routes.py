import base64
import os

from fastapi import Request
from starlette import status
from starlette.responses import RedirectResponse

from database.db_middleware import get_all_values
from database.models import Product
from sending_email import send_email


async def get_home(request: Request):
    """Home page

    :param request:
    :return:
    """
    from app.main import templates

    products = get_all_values(Product)
    available_products = []
    for product in products:
        if product.is_available:
            image_data = product.image_data

            image_base64 = base64.b64encode(image_data).decode('utf-8')

            available_products.append({
                'photo_base64': image_base64,
                'name': product.name,
                'price': product.price,
            })

    response = templates.TemplateResponse("index.html", {
        "request": request,
        "available_products": available_products
    })
    return response


async def contact(request: Request):
    """

    :param request:
    :return:
    """
    form_data = await request.form()
    name = form_data.get("name")
    email = form_data.get("email")
    message = form_data.get("message")

    admin_email = os.getenv('ADMIN_EMAIL')

    sender_email = os.getenv('ADMIN_EMAIL')
    sender_password = os.getenv('ADMIN_EMAIL_PASSWORD')
    receiver_email = admin_email
    subject = message
    message = f'Сообщение от пользователя {name} <{email}>: {message}'

    send_email(sender_email, sender_password, receiver_email, subject, message)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
