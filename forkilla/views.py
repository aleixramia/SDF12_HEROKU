import decimal

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect

from forkilla.forms import ReservationForm, ReviewForm
from forkilla.models import Restaurant, ViewedRestaurants, Reservation, Review
from django.urls import reverse

from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User, Group
from rest_framework import viewsets
from .serializers import RestaurantSerializer
from rest_framework import permissions



def index(request):
    restaurants = Restaurant.objects.filter(is_promot="True")
    promoted = True
    context = {
        'restaurants': restaurants,
        'promoted': promoted,
        'viewedrestaurants': _check_session(request)

    }
    return render(request, 'forkilla/index.html', context)

def details(request, restaurant_number=0):

    try:
        select_restaurant = Restaurant.objects.get(restaurant_number__exact=restaurant_number)
    except Restaurant.DoesNotExist:
        return render(request, 'forkilla/error.html')


    context = {
        'restaurant': select_restaurant,
        'viewedrestaurants': _check_session(request),
    }
    return render(request,'forkilla/details.html',context)

def restaurants(request, city="", category = ""):
    promoted = False
    print("CITY:")
    print(city)
    print("CATEGORY:")
    print(category)
    if city:
        if category:
            restaurants_by_city=Restaurant.objects.filter(category__iexact=category, city__iexact=city)
        else:
            restaurants_by_city = Restaurant.objects.filter(city__iexact=city)
    else:
        if category:
            restaurants_by_city = Restaurant.objects.filter(category__iexact=category)
        restaurants_by_city = Restaurant.objects.filter(is_promot="True")
        promoted = True
    context = {
        'city': city,
        'restaurants': restaurants_by_city,
        'promoted': promoted,
        'category': category,
        'viewedrestaurants': _check_session(request)

    }

    return render(request, 'forkilla/restaurants.html', context)

def error(request):
    return render(request,'forkilla/error.html')

@login_required
def reservation(request):
    viewedrestaurants = _check_session(request)
    try:
        if request.method == "POST":
            form = ReservationForm(request.POST)
            if form.is_valid():
                    resv = form.save(commit=False)
                    restaurant_number = request.session["reserved_restaurant"]
                    resv.restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
                    resv.user = request.user
                    reservations = Reservation.objects.filter(restaurant=resv.restaurant,
                                                              time_slot=request.POST['time_slot'],
                                                              day=request.POST['day'])
                    num_people = 0
                    for reservation in reservations:
                        num_people += reservation.num_people

                    if  int(request.POST['num_people']) + int(num_people) <= int(Restaurant.objects.get(restaurant_number=restaurant_number).restaurant_capacity):

                        resv.save()
                        request.session["reservation"] = resv.id
                        request.session["result"] = "OK"

                    else:
                        request.session["result"] = "Error"

            else:
                  request.session["result"] = form.errors
            return HttpResponseRedirect(reverse('checkout'))

        elif request.method == "GET":
            restaurant_number = request.GET["reservation"]
            restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
            request.session["reserved_restaurant"] = restaurant_number

            form = ReservationForm()
            context = {
                'restaurant': restaurant,
                'viewedrestaurants': viewedrestaurants,
                'form': form
            }
    except Restaurant.DoesNotExist:
        return HttpResponse("Restaurant Does not exists")
    return render(request, 'forkilla/reservation.html', context)

def _check_session(request):

    if "viewedrestaurants" not in request.session:
        viewedrestaurants = ViewedRestaurants()
        viewedrestaurants.save()
        request.session["viewedrestaurants"] = viewedrestaurants.id_vr
    else:
        viewedrestaurants = ViewedRestaurants.objects.get(id_vr=request.session["viewedrestaurants"])
    return viewedrestaurants


def details(request,restaurant_number=""):
    viewedrestaurants = _check_session(request)
    restaurant = 	Restaurant.objects.get(restaurant_number=restaurant_number)
    viewedrestaurants.restaurant.add(restaurant)
    request.restaurant = restaurant
    context = {
        'restaurant': restaurant,
        'viewedrestaurants': _check_session(request)

    }
    return render(request, 'forkilla/details.html', context)


def checkout(request):
    #viewedrestaurants = _check_session(request)
    #restaurant = 	Restaurant.objects.get(restaurant_number=restaurant_number)
    #viewedrestaurants.restaurant.add(restaurant)

    reservation = request.session['result']

    context = {
        'reservation':reservation,
        #'restaurant': restaurant,
        'viewedrestaurants': _check_session(request)

    }
    return render(request, 'forkilla/checkout.html', context)

def search(request):
    if request.POST["q"]:
        #message = 'You searched for: %r' % request.POST["q"]
        city = request.POST["q"]
        return restaurants(request, city)
    else:
        message = 'You submitted an empty form.'
    return HttpResponse(message)

@login_required
def review(request):
    viewedrestaurants = _check_session(request)
    try:
        if request.method == "POST":
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                restaurant_number = request.session["restaurant"]
                review.restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
                review.user = request.user
                review.save()
                #request.session["type"]=review
                request.session["review"] = review.id
                request.session["result"]="OK"

                reviews = Review.objects.filter(restaurant=review.restaurant)
                num_reviews = len(reviews)
                sum = 0
                for rev in reviews:
                    sum += int(rev.rating)
                rating = sum/num_reviews
                Restaurant.objects.get(restaurant_number=restaurant_number).rate = decimal.Decimal(rating)
            else:
                request.session["result"] = form.errors
            return HttpResponseRedirect(reverse('index'))

        elif request.method == "GET":

            restaurant_number = request.GET["review"]
            restaurant = Restaurant.objects.get(restaurant_number=restaurant_number)
            request.session["restaurant"] = restaurant_number

            form = ReviewForm()
            context = {
                'restaurant': restaurant,
                'viewedrestaurants': viewedrestaurants,
                'form': form
            }
    except Restaurant.DoesNotExist:
        return HttpResponse("Restaurant Does not exists")
    return render(request, 'forkilla/review.html', context)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })

@login_required
def profile(request):
    return render(request,'forkilla/profile.html')


class RestaurantViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    """
    API endpoint that allows Restaurants to be viewed or edited.
    """
    queryset = Restaurant.objects.all().order_by('category')
    serializer_class = RestaurantSerializer
