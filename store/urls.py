from django.urls import path
from . import views

urlpatterns = [
    path('', views.store , name="store"),
    path('product/<int:pk>', views.productDetail , name="productDetail"),
    path('product/<int:pk>/add-comment', views.add_comment , name="add-comment"),
    path('product/<int:pk>/delete-comment', views.delete_comment , name="delete-comment"),
    path('search/', views.searchBar, name="search"),
    path('register/',views.registerPage,name="register"),
    path('logout/',views.logoutUser,name="logout"),
    path('login/',views.loginPage,name="login"),
    path('cart/', views.cart , name="cart"),
    path('checkout/', views.checkout , name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
]

