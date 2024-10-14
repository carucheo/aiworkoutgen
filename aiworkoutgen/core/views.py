from django.shortcuts import render

# Create your views here.
# from django.http import HttpResponse

def home(request):
    return render(request, 'core/home.html')


def user_login(request):
    return render(request, 'core/login.html')


def user_signup(request):
      return render(request, 'core/signup.html')