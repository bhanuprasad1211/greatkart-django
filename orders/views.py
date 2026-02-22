from django.shortcuts import render
from django.shortcuts import HttpResponse,redirect
from carts.views import CartItem
from .forms import OrderForm
from .models import Order
import datetime
from django.db.models import F

#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator 
from django.core.mail import EmailMessage

# Create your views here.

import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import Order


from carts.models import CartItem
from .models import Payment, OrderProduct

def payment_success(request):
    
    session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == "paid":
        order_number = session.metadata.get("order_number")
        order = Order.objects.get(order_number=order_number)

        if order.is_ordered:
            return redirect('store')

        #Create payment 
        payment = Payment.objects.create(
            user=order.user,
            payment_id=session.payment_intent,
            payment_method="Stripe",
            amount_paid=order.order_total,
            status="Completed"
        )

        #Attach payment to order
        order.payment = payment
        order.is_ordered = True
        order.status = "Accepted"
        order.save()

        #Move cart items to OrderProduct
        cart_items = CartItem.objects.filter(user=order.user)

        for item in cart_items:
            #Create OrderProduct WITHOUT variations first
            order_product = OrderProduct.objects.create(
                order=order,
                payment=payment,
                user=order.user,
                product=item.product,
                quantity=item.quantity,
                product_price=item.product.price,
                ordered=True,
            )

            item.product.stock = F('stock') - item.quantity
            item.product.save()

            #Copy all cart variations to OrderProduct
            variations = item.variations.all()
            order_product.variations.set(variations)

        cart_items.delete()

        current_site=get_current_site(request)
        mail_subject="Please verify your account"
        message=render_to_string('orders/order_received_email.html',{
                    'user':request.user,
                    'order':order,
                    
                })
        to_email=request.user.email
        send_email = EmailMessage(
            mail_subject,
            message,
            to=[to_email],
            )
        send_email.send(fail_silently=False)



        context = {
            'order_number': order.order_number,
            'order_total': order.order_total,
            'payment_id': payment.payment_id,
            'status': payment.status
        }

        return render(request, 'orders/order_complete.html', context)

    return redirect('store')


stripe.api_key = settings.STRIPE_SECRET_KEY

def payments(request):
    order_number = request.GET.get('order_number')
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'Order {order.order_number}',
                },
                'unit_amount': int(order.order_total * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/orders/payment-success/') + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri('/orders/payment-cancel/'),
        metadata={
            "order_number": order.order_number
        }
    )

    return redirect(session.url, code=303)

def place_order(request,total=0,quantity=0) :
    current_user=request.user

    cart_items=CartItem.objects.filter(user=current_user)
    cart_count=cart_items.count()
    if cart_count <=0 :
        return redirect('store')
    
    grand_total=0
    tax=0
    for cart_item in cart_items :
        total+=(cart_item.product.price * cart_item.quantity)
        quantity+=cart_item.quantity
    tax=(2 * total)/100
    grand_total=total+tax
    if request.method=='POST' :
        form=OrderForm(request.POST) 
        if form.is_valid() :
            data=Order()
            data.user=current_user
            data.first_name=form.cleaned_data['first_name']
            data.last_name=form.cleaned_data['last_name']
            data.phone=form.cleaned_data['phone']
            data.email=form.cleaned_data['email']
            data.address_line_1=form.cleaned_data['address_line_1']
            data.address_line_2=form.cleaned_data['address_line_2']
            data.country=form.cleaned_data['country']
            data.state=form.cleaned_data['state']
            data.city=form.cleaned_data['city']
            data.order_note=form.cleaned_data['order_note']
            data.order_total=grand_total
            data.tax=tax
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()
            yr=int(datetime.date.today().strftime('%Y'))
            dt=int(datetime.date.today().strftime('%d'))
            mt=int(datetime.date.today().strftime('%m'))
            d=datetime.date(yr,mt,dt)
            current_date=d.strftime('%Y%m%d')
            order_number=current_date+ str(data.id)
            data.order_number=order_number
            data.save()

            order=Order.objects.get(user=current_user,is_ordered=False,order_number=order_number)
            context={
                'order':order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                'grand_total':grand_total,
            }
            return redirect(f'/orders/payments/?order_number={order.order_number}')
    else :
        return redirect('checkout')

        