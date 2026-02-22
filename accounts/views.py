from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import RegistrationForm
from .models import Accounts
from carts.models import Cart,CartItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages,auth
from carts.views import _cart_id
#Verification email
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator 
from django.core.mail import EmailMessage

import requests 

# Create your views here.
def register(request) :
    if request.method=='POST' :
        form = RegistrationForm(request.POST)
        if form.is_valid() :
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            phone_number=form.cleaned_data['phone_number']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            username=email.split('@')[0]
            if Accounts.objects.filter(email=email).exists():
                form.add_error('email', 'This email address is already registered.')
            else:
                # if Accounts.objects.filter(username=username).exists():
                #     username = username + str(Accounts.objects.count() + 1)
                user=Accounts.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
                user.phone_number=phone_number
            
                user.save()

                #activate user
                current_site=get_current_site(request)
                mail_subject="Please verify your account"
                message=render_to_string('accounts/account_verification_email.html',{
                    'user':user,
                    'domain':current_site,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':default_token_generator.make_token(user),
                })
                to_email=email
                send_email = EmailMessage(
                    mail_subject,
                    message,
                    to=[to_email],
                )
                #send_email.content_subtype = "html"  # optional, but good practice
                send_email.send(fail_silently=False)


                #messages.success(request,'Registration successful')
                return redirect('/accounts/login/?command=verification&email='+email)
    else :
        form = RegistrationForm()
    context={'form':form}
    return render(request,'accounts/register.html',context)
def login(request) :
    if request.method=='POST' :
        email=request.POST['email']
        password=request.POST['password']
        user=auth.authenticate(request,email=email,password=password)
        if user is not None :
            try:
                cart=Cart.objects.get(cart_id=_cart_id(request))

                is_cart_item_exist=CartItem.objects.filter(cart=cart).exists()

                if is_cart_item_exist :
                    cart_item=CartItem.objects.filter(cart=cart)
                    
                    product_variation=[]
                    for item in cart_item :
                        variation=item.variations.all()
                        product_variation.append(list(variation))

                    cart_item=CartItem.objects.filter(user=user)
                    ex_var_list=[]
                    id=[]
                    for item in cart_item :
                        existing_variation=item.variations.all()
                        ex_var_list.append(list(existing_variation))#Query set
                        id.append(item.id)

                    for pr in product_variation :
                        if pr in ex_var_list :
                            index=ex_var_list.index(pr)
                            item_id=id[index]
                            item=CartItem.objects.get(id=item_id)
                            item.quantity+=1
                            item.user=user
                            item.save()
                        else :
                            cart_item=CartItem.objects.filter(cart=cart)

                            for item in cart_item :
                                item.user=user
                                item.save()
            except :
                pass
            auth.login(request,user)
            messages.success(request,'You are logged in')
            url=request.META.get('HTTP_REFERER')
            try :
                query=requests.utils.urlparse(url).query

                params=dict(x.split('=') for x in query.split('&'))

                if 'next' in params :
                    nextPage=params['next']
                    return redirect(nextPage)
                return redirect('dashboard')
            except:
                return redirect('dashboard')
        else :
            messages.error(request,'Invalid login credentials')
            return redirect('login')
        
    return render(request,'accounts/login.html')


@login_required(login_url='login')
def logout(request) :
    auth.logout(request)
    messages.success(request,"You are logged out")
    return redirect('login')
def activate(request,uidb64,token) :
    try :
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Accounts._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Accounts.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active=True
        user.save()
        messages.success(request,'Congratulations! Your account is activated')
        return redirect('login')
    else :
        messages.error(request,'Invalid activation link')
        return redirect('register') 
    

@login_required(login_url='login')
def dashboard(request) :
    return render(request,'accounts/dashboard.html')

def forgetpassword(request) :
    if request.method == 'POST' :
        email=request.POST['email']
        if Accounts.objects.filter(email=email).exists() :
                user=Accounts.objects.get(email__iexact=email)

                current_site=get_current_site(request)
                mail_subject="Reset your password"
                message=render_to_string('accounts/reset_password_email.html',{
                    'user':user,
                    'domain':current_site,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':default_token_generator.make_token(user),
                })
                to_email=email
                send_email = EmailMessage(
                    mail_subject,
                    message,
                    to=[to_email],
                )
                #send_email.content_subtype = "html"  # optional, but good practice
                send_email.send(fail_silently=False)
                messages.success(request,'Password reset email has been sent to your email address')
                return redirect('login')
        
        else :
            messages.error('Account does not exists')
            return redirect('forgetpassword')
    return render(request,'accounts/forgetpassword.html')
def resetpassword_validate(request,uidb64,token) :
    try :
        uid=urlsafe_base64_decode(uidb64).decode()
        user=Accounts._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Accounts.DoesNotExist):
        user=None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'Please reset your password')
        return redirect('resetpassword')
    else :
        messages.error(request,"this link has been expired")
        return redirect('login')  
    
def resetpassword(request) :
    if request.method == 'POST' :
        password=request.POST['password']
        confirm_password=request.POST['confirm_password']
        if password==confirm_password :
            uid=request.session.get('uid')
            user=Accounts.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset successfully')
            return redirect('login')
        else :
            messages.error(request,"Password do not match")
            return redirect('resetpassword')
    else :
        return render(request,'accounts/resetpassword.html')

