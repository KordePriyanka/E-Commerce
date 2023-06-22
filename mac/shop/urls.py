from django.urls import path
from . import views

urlpatterns = [
    # from mac.urls comes to views , from views for " " goes to views.index
    
    # New Users path
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUS"),
    path("tracker/", views.tracker, name="Tracking Status"),
    path("search/", views.search, name="Search"),
    path("products/id=<int:myid>", views.productView, name="ProductView"),
    
    # Registered User path
    path("checkout/", views.checkout, name="CheckOut"),
    path("success/", views.success, name="Success"),
    path("trackerResponse/", views.trackerResponse, name="trackerResponse"),
    path("checkoutOrders/", views.checkoutOrders, name="checkoutOrders"),
    # For Payment
    path("handlerequest/",views.handlerequest, name='HandleRequest'),
    
    # API for Authetication of the users
    path("register/", views.register, name="Register"),
    path("login/", views.login, name="Login"),
    path("logout/", views.logout, name="Logout"),
    path("forgotPassword/", views.forgotPassword, name="forgotPassword"),
    
    
    # Profile Pages
    path("profileInfo/",views.profileInfo, name='profileInfo'),
    path("ordersHistory/",views.ordersHistory, name='ordersHistory'),
    path("home/",views.home, name='home'),
    
    # for rendering Products categories wise
    path("electronicsProd/",views.electronicsProd, name='electronicsProd'),
    path("FashionProd/",views.FashionProd, name='FashionProd'),
    path("booksProd/",views.booksProd, name='booksProd'),
    path("homeProd/",views.homeProd, name='homeProd'),
]
