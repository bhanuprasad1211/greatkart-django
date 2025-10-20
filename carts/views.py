from django.shortcuts import render,get_object_or_404
from store.models import Product
from carts.models import Cart,CartItem
from django.shortcuts import redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Variation
from django.contrib.auth.decorators import login_required
# Create your views here.
def _cart_id(request) :
    cart=request.session.session_key
    if not cart :
        cart=request.session.create()
    return cart


def add_cart(request,product_id) :
    current_user=request.user
    product=Product.objects.get(id=product_id) #get the product to add into cart
    if current_user.is_authenticated :
        product_variation=[]

        if request.method=='POST' :
            for item in request.POST :
                key=item
                value=request.POST[key]
                try :
                    variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                    #print(variation)
                except :
                    pass

        
        is_cart_item_exist=CartItem.objects.filter(product=product,user=current_user).exists()
        if is_cart_item_exist:
            cart_item=CartItem.objects.filter(product=product,user=current_user)
            ex_var_list=[]
            id=[]
            for item in cart_item :
                existing_variation=item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            #print(ex_var_list)
            if product_variation in ex_var_list :
                #increase quantity
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item=CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
            else :
                #create new cart item
                cart_item=CartItem.objects.create(
                quantity=1,
                user=current_user,
                product=product
                )
                if len(product_variation) > 0 :
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        else :
            cart_item=CartItem.objects.create(
                quantity=1,
                user=current_user,
                product=product
            )
            if len(product_variation) > 0 :
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        # return HttpResponse(cart_item.quantity)
        # exit()
        return redirect('cart')
    else :
        product_variation=[]

        if request.method=='POST' :
            for item in request.POST :
                key=item
                value=request.POST[key]
                try :
                    variation=Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                    product_variation.append(variation)
                    #print(variation)
                except :
                    pass

        try :
            cart=Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist :
            cart=Cart.objects.create(
                cart_id=_cart_id(request)  
            )
        cart.save()
        is_cart_item_exist=CartItem.objects.filter(product=product,cart=cart).exists()
        if is_cart_item_exist:
            cart_item=CartItem.objects.filter(product=product,cart=cart)
            ex_var_list=[]
            id=[]
            for item in cart_item :
                existing_variation=item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

            #print(ex_var_list)
            if product_variation in ex_var_list :
                #increase quantity
                index=ex_var_list.index(product_variation)
                item_id=id[index]
                item=CartItem.objects.get(product=product,id=item_id)
                item.quantity+=1
                item.save()
            else :
                #create new cart item
                cart_item=CartItem.objects.create(
                quantity=1,
                cart=cart,
                product=product
                )
                if len(product_variation) > 0 :
                    cart_item.variations.clear()
                    cart_item.variations.add(*product_variation)
                cart_item.save()
        else :
            cart_item=CartItem.objects.create(
                quantity=1,
                cart=cart,
                product=product
            )
            if len(product_variation) > 0 :
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        # return HttpResponse(cart_item.quantity)
        # exit()
        return redirect('cart')
def remove_cart(request,product_id,cart_item_id) :
    product=get_object_or_404(Product,id=product_id)
    try :
        if request.user.is_authenticated :
            cart_item=CartItem.objects.get(product=product,user=request.user,id=cart_item_id)
        else :
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_item=CartItem.objects.get(product=product,cart=cart,id=cart_item_id)
        if cart_item.quantity > 1 :
            cart_item.quantity-=1
            cart_item.save()
        else :
            cart_item.delete()
    except :
        pass
    return redirect('cart')
def remove_cart_item(request,product_id,cart_item_id) :
    product=get_object_or_404(Product,id=product_id)
    if request.user.is_authenticated :
        cart_item=CartItem.objects.get(user=request.user,product=product,id=cart_item_id)
    else :
        cart=Cart.objects.get(cart_id=_cart_id(request))
        cart_item=CartItem.objects.get(cart=cart,product=product,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')
def cart(request) :
    try :
        grand_total=0
        tax=0
        if request.user.is_authenticated :
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else :
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        total=0
        quantity=0
        for cart_item in cart_items :
            total+=(cart_item.quantity*cart_item.product.price)
            quantity+=cart_item.quantity
        tax=(total*2)/100
        grand_total=total+tax
    except ObjectDoesNotExist :
        pass
    context={'cart_items':cart_items,'total':total,'quantity':quantity,'tax':tax,'grand_total':grand_total}
    return render(request,'store/cart.html',context)
@login_required(login_url='login')
def checkout(request) :
    try :
        grand_total=0
        tax=0
        if request.user.is_authenticated :
            cart_items=CartItem.objects.filter(user=request.user,is_active=True)
        else :
            cart=Cart.objects.get(cart_id=_cart_id(request))
            cart_items=CartItem.objects.filter(cart=cart,is_active=True)
        total=0
        quantity=0
        for cart_item in cart_items :
            total+=(cart_item.quantity*cart_item.product.price)
            quantity+=cart_item.quantity
        tax=(total*2)/100
        grand_total=total+tax
    except ObjectDoesNotExist :
        pass
    context={'cart_items':cart_items,'total':total,'quantity':quantity,'tax':tax,'grand_total':grand_total}
    return render(request,'store/checkout.html',context)