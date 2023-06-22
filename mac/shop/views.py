from django.shortcuts import render , redirect , HttpResponseRedirect
from django.http import HttpResponse
from .models import Product, Contact , Orders , OrderUpdate , Register , User
from django.contrib import messages
from math import ceil
from django.views.decorators.csrf import csrf_exempt
from PayTm import Checksum
# from PayTm import generate_checksum, verify_checksum
import datetime
import json
from passlib.hash import sha256_crypt
from django.contrib.auth.hashers import make_password ,check_password
from django.contrib import messages
from shop.middlewares.auth import auth_middleware
import json

MERCHANT_KEY = 'Enter Your merchant Key'


# HTML Pages
def index(request):
    # username = request.session['username']
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
    # print(request.session.get('email'))
    return render(request, 'shop/index.html', params)

def home(request):
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
    # print(request.session.get('email'))
    return render(request, 'shop/index.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        msg_date= datetime.datetime.now()
        contact = Contact(name=name, email=email, phone=phone, desc=desc, msg_date= msg_date)
        contact.save()
        messages.success(request, 'Your messsage have been sended.Our Team will contact you Soon')
    return render(request, 'shop/contact.html')



# Search function
def searchMatch(query, item):
    ''' return true only if uery matchs the item '''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower() or query in item.subcategory.lower():
        return True
    else:
        return False

def search(request):
    '''Searching the products'''
    query = request.GET.get('search').lower()
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]
        if len(prod) != 0:
            n = len(prod)
            nSlides = n // 4 + ceil((n / 4) - (n // 4))
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds}
    return render(request, 'shop/search.html', params)

def productView(request , myid):
    # Fetch the products using id giving name myid
    # since django create primary key by itself ie. id
    product = Product.objects.filter(id = myid)
    # product passed for productView Page we wish to access : product here views.py name
    params = {'product':product[0], 'product_id':myid}
    return render(request, 'shop/prodView.html', params)

def checkoutOrders(request):
    return render(request, 'shop/checkoutOrders.html')

@auth_middleware
def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        productsName = request.POST.get('productsName', '')
        amount = request.POST.get('amount', 0)
        name = request.POST.get('name', '')
        email = request.session.get('email')
        phone = request.POST.get('phone', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        order = Orders(items_json = items_json, productsName=productsName, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        thank = True
        update = OrderUpdate(order_id = order.order_id, update_desc = "The order has been Placed")
        update.save()
        id = order.order_id

        return render(request, 'shop/success.html', {'thank': thank , 'id' : id})
        # Request paytm to transfer the amount to your account after payment by user

        param_dict={

            'MID': 'WorldP64425807474247',
            'ORDER_ID': str(order.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

        }
        
        # paytmChecksum = Checksum.generateSignature(param_dict, MERCHANT_KEY)

        paytm_params = dict(param_dict)
        # print(paytm_params)
        checksum = Checksum.generateSignature(paytm_params, MERCHANT_KEY)
        # print(checksum)

        paytm_params['CHECKSUMHASH'] = checksum
        # print('SENT: ', checksum)

        return  render(request, 'shop/paytm.html', {'param_dict': param_dict})
    return render(request, 'shop/checkout.html')

def success(request):
    # May be this code is redundant
    return render(request, 'shop/success.html')
    # return HttpResponse("Search of Shop Page!!")



# Authentication API's
def register(request):
    '''for perdefined emails are not allowed to added to databases'''
    if request.method == "POST":
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        phone = request.POST.get('phone','')
        securityQuestion = request.POST.get('securityQuestion','')
        securityAnswer = request.POST.get('securityAnswer','')
        isCustomerExists = Register.isExists(email)
        if not isCustomerExists:
            if password == confirm_password:
                hash_password = make_password(password)
                register = Register(username=username, email=email, password=hash_password, phone=phone, securityQuestion=securityQuestion,securityAnswer=securityAnswer)
                register.save()
                request.session['email'] = email
                request.session['username'] = username
                messages.success(request, f'{username} you have successfully registered.Happy Shopping!')
                return redirect('/shop/')
            else:
                # Password not matched
                messages.success(request, f'{username} check password!')
                return render(request, 'shop/register.html') # right now return register page
        else:
            messages.info(request, f'This email already exists in our Database! so you can Login.')
            return render(request, 'shop/register.html')
    return render(request, 'shop/register.html')

def login(request):
    '''This is working for both success email and unsuccessful emails '''
    if request.method == "GET":
        login.returnUrl = request.GET.get('return_url')
        return render(request, 'shop/login.html')

    if request.method == "POST":
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        customer = Register.get_customer_by_email(email)
        if customer:
            # Customer Exists
            flag = check_password(password, customer.password)
            if flag:
                # session created and storing email, name , customer_id in the session
                request.session['customer_id'] = customer.register_id
                request.session['username'] = customer.username
                request.session['email'] = customer.email
                username = customer.username
                if login.returnUrl:
                    return HttpResponseRedirect(login.returnUrl)
                else:
                    messages.success(request, f'{username} you have successfully Logged In.Happy Shopping!')
                    login.returnUrl = None
                    return redirect('/shop/home')
            else:
                # Customer Exists but made password incorrect
                messages.warning(request, f'Invalid Password!')
                return render(request, 'shop/login.html')
        else:
            messages.warning(request, f'Invalid Email!')
            return render(request, 'shop/login.html')
    return render(request, 'shop/login.html')

def logout(request):
    request.session.clear()
    return redirect('/')

def forgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email', '')
        securityQuestion = request.POST.get('securityQuestion','')
        securityAnswer = request.POST.get('securityAnswer','')
        customer = Register.get_customer_by_email(email)
        if customer:
            # Customer Exists
            if(securityQuestion == customer.securityQuestion):
                if(securityAnswer == customer.securityAnswer):
                    request.session['customer_id'] = customer.register_id
                    request.session['username'] = customer.username
                    request.session['email'] = customer.email
                    username = customer.username
                    messages.success(request, f'{username} you have successfully Logged In.Happy Shopping!')
                    return redirect('/shop/')
                    
                else:
                     # security answer is worng
                    messages.warning(request, f'Incorrect security Answer!')
                    return render(request, 'shop/forgotPassword.html')
            else:
                # security question is wrong
                messages.warning(request, f'Incorrect security Question!')
                return render(request, 'shop/forgotPassword.html')
        else:
             # not registered user
            messages.warning(request, f'Not Regsitered User! Sign Up')
            return render(request, 'shop/Register.html')
    return render(request, 'shop/forgotPassword.html')


# Payment Handle Request
@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    # since it will post request so we have to remove csrf
    # csrf_exempt is decorator which changes the function functionality for sometime
    return HttpResponse("Done")



# User Profile Apis
def profileInfo(request):
    '''all the form informating is coming if you want to store in the tables can be stored or else connect with foreign key'''
    email = request.session['email']
    if not User.get_user_by_email(email):
        if request.method == "POST":
            username = request.session.get('username')
            firstName = request.POST.get('firstName', '') 
            lastName =  request.POST.get('lastName', '')
            gender = request.POST.get('gender','')
            email = request.session.get('email')
            phone = request.POST.get('phone', '')
            user = User(username=username,firstName=firstName,lastName=lastName,gender=gender,email=email,phone=phone)
            user.save()
            messages.success(request, f'Your Profile has been successfully updated!')
    else:
        user = User.objects.filter(email=email)
        params = {'user':user[0]}
        return render(request, 'shop/profileInfo.html', params)
    
    return render(request, 'shop/profileInfo.html')
    
def ordersHistory(request):
    customer = request.session.get('customer_id')
    email = request.session.get('email')
    # customer = Register.get_customer_by_email(email)
    if customer:
        allOrders = []
        allOrdersEmail = Orders.objects.filter(email = email)
        for order in allOrdersEmail:
            allOrders.append(order)
        params = {'allOrders': allOrders}
    return render(request, 'shop/ordersHistory.html', params)

def tracker(request):
    return render(request, 'shop/tracker.html')

def trackerResponse(request):
    if request.method == "POST":
        orderId = request.POST.get('orderId', '')
        email = request.session.get('email')
        try:
            order = Orders.objects.filter(order_id = orderId, email= email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id = orderId)
                updates = []
                for item in update:
                    updates.append({'text':item.update_desc, 'time': item.timestamp})
                    response = json.dumps(updates, default=str)
                    params = {'response': response}
                return render(request, 'shop/trackerResponse.html', params)
            else:
                return HttpResponse('Please enter Correct Order Id...')
        except :
            return HttpResponse('Please enter Correct Order Id...')  
    return render(request, 'shop/trackerResponse.html')



# Category wise Products Pages
def electronicsProd(request):
    allProds = []
    category = 'Electronics'
    request.session['category'] = category
    prod = Product.objects.filter(category=category)
    allProds.append(prod)
    params = {'allProds': allProds}
    return render(request, 'shop/productsPage.html', params)

def FashionProd(request):
    allProds = []
    category = 'Fashion'
    request.session['category'] = category
    prod = Product.objects.filter(category=category)
    n = len(prod)
    allProds.append(prod)
    params = {'allProds': allProds}
    return render(request, 'shop/productsPage.html', params)

def homeProd(request):
    allProds = []
    category = 'home Kitchen'
    request.session['category'] = category
    prod = Product.objects.filter(category=category)
    allProds.append(prod)
    params = {'allProds': allProds}
    return render(request, 'shop/productsPage.html', params)

def booksProd(request):
    allProds = []
    category = 'Books'
    request.session['category'] = category
    prod = Product.objects.filter(category=category)
    allProds.append(prod)
    params = {'allProds': allProds}
    return render(request, 'shop/productsPage.html', params)

