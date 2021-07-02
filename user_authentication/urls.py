
from django.urls import path
from . import views


urlpatterns = [
    path('',views.loginpage,name="loginpage"),    
    path('login/',views.loginpage,name="loginpage"),
    path('register/',views.registerpage,name="registerpage"),
    path('logout/',views.logoutpage,name='logoutpage'),
    path('settings/',views.settingspage,name='settings'),
]
