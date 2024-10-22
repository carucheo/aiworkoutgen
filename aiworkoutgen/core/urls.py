from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), #  Root URL for the 'home' view
    path('login', views.user_login, name='login'),    
    path('signup', views.user_signup, name='signup'),
    path('workout', views.user_workout, name='workout'),

]
