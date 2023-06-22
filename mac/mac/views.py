from django.shortcuts import render
from django.http import HttpResponse
from shop.models import Product
from math import ceil
# from .models import Product, Contact , Orders , OrderUpdate , Register , User

def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds}

    # For checking sessions created or not
    # print(request.session.get('customer_id'))
    return render(request, 'index.html', params)