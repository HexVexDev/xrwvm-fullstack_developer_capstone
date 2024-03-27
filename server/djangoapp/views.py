import json
import logging
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from datetime import datetime
from .models import CarMake, CarModel
from .populate import initiate
from django.views.decorators.csrf import csrf_exempt
from .restapis import get_request, analyze_review_sentiments, post_review

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({"userName": username, "status": "Authenticated"})
    return JsonResponse({"userName": "", "status": "Authentication failed"})

# Create a `logout_request` view to handle sign out request
def logout_request(request): 
    logout(request)
    return JsonResponse({"userName": ""})

def get_cars(request):
    count = CarMake.objects.count()
    print(count)
    initiate()  
    car_models = CarModel.objects.select_related('make')
    cars = [{"CarModel": car_model.name, "CarMake": car_model.make.name} for car_model in car_models]
    return JsonResponse({"CarModels": cars})

# Create a `registration` view to handle sign up request
@csrf_exempt
def registration(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        first_name = data.get('firstName')
        last_name = data.get('lastName')
        email = data.get('email')
        if username and password and first_name and last_name and email:
            if User.objects.filter(username=username).exists():
                return JsonResponse({"userName": username, "error": "Already Registered"})
            else:
                user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                                password=password, email=email)
                login(request, user)
                return JsonResponse({"userName": username, "status": "Authenticated"})
    return JsonResponse({"userName": "", "status": "Registration failed"})

# Update the `get_dealerships` view to render list of dealerships
def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers"
    if state != "All":
        endpoint = f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})

def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchReviews/dealer/{dealer_id}"
        reviews = get_request(endpoint)
        for review_detail in reviews:
            response = analyze_review_sentiments(review_detail['review'])
            review_detail['sentiment'] = response.get('sentiment', 'Unknown')
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})

def add_review(request):
    if not request.user.is_anonymous:
        if request.method == 'POST':
            data = json.loads(request.body)
            try:
                response = post_review(data)
                return JsonResponse({"status": 200})
            except Exception as e:
                return JsonResponse({"status": 401, "message": f"Error in posting review: {e}"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})
