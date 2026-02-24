from django.shortcuts import render
from django.urls import path,include
from store.models import ReviewRating
from store.models import Product

def home(request) :
    products=Product.objects.all().filter(is_available=True).order_by('-created_date')
    try :
        for product in products :
            product_reviews=ReviewRating.objects.filter(product_id=product.id,status=True)
    except :
        product_reviews=None
    context={'products':products,'product_reviews':product_reviews}
    return render(request,'home.html',context)