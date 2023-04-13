from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Category, Listner, Comment, Bid

def listing(request, id):
    listingData = Listner.objects.get(pk = id)
    isListingWatchList = request.user in listingData.watchlist.all()
    allComments = Comment.objects.all()
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingWatchList": isListingWatchList,
        "Comments": allComments,
        'isOwner': isOwner
    })
def closeAuction(request,id):
    listingData = Listner.objects.get(pk=id)
    listingData.isActive = False
    listingData.save()
    isListingWatchList = request.user in listingData.watchlist.all()
    allComments = Comment.objects.all()
    isOwner = request.user.username == listingData.owner.username
    return render(request, "auctions/listing.html", {
        "listing": listingData,
        "isListingWatchList": isListingWatchList,
        "Comments": allComments,
        'isOwner': isOwner,
        "message": "Congratulations! Your auction is closed",
        "update": True,
    })
def addBid(request, id):
    newBid = request.POST['newBid']
    listingData = Listner.objects.get(pk=id)
    isListingWatchList = request.user in listingData.watchlist.all()
    allComments = Comment.objects.all()
    isOwner = request.user.username == listingData.owner.username
    if int(newBid) > listingData.price.bid:
        updatedBid = Bid(user = request.user, bid = int(newBid))
        updatedBid.save()
        listingData.price = updatedBid
        listingData.save()
        return render(request, "auctions/listing.html", {
        "listing": listingData,
        "message": "Bid was successfully updated",
        "update": True,
        "isListingWatchList": isListingWatchList,
        "Comments": allComments,
        'isOwner': isOwner
    })
    else:
        return render(request, "auctions/listing.html", {
        "listing": listingData,
        "message": "Bid was failed",
        "update": False,
        "isListingWatchList": isListingWatchList,
        "Comments": allComments,
        'isOwner': isOwner
    })
    
def addComment(request, id):
    currentUser = request.user
    listingData = Listner.objects.get(pk=id)

    message = request.POST['newComment']

    newComment = Comment(
        author = currentUser,
        listing = listingData,
        message = message
        ).save()
    
    return HttpResponseRedirect(reverse("listing", args = (id, )))

def displayWatchlist(request):
    currentUser = request.user
    listings = currentUser.listingwatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
    })

def removeWatchlist(request,id):
    listingData = Listner.objects.get(pk = id)
    currentUser = request.user
    listingData.watchlist.remove(currentUser)
    return HttpResponseRedirect(reverse("listing", args = (id, )))

def addWatchlist(request,id):
    listingData = Listner.objects.get(pk = id)
    currentUser = request.user
    listingData.watchlist.add(currentUser)
    return HttpResponseRedirect(reverse("listing", args = (id, )))

def index(request):
    activateListenings = Listner.objects.filter(isActive = True)
    allCategories = Category.objects.all()
    return render(request, "auctions/index.html",{
        "listings": activateListenings,
        "categories": allCategories 
    })

def displayCategory(request):
    if request.method == "POST":
        categoryForm = request.POST['category']
        category = Category.objects.get(categoryname = categoryForm)
        activateListenings = Listner.objects.filter(isActive = True, category = category)
        allCategories = Category.objects.all()
        return render(request, "auctions/index.html",{
            "listings": activateListenings,
            "categories": allCategories, 
        })
def createlisnter(request):
    if request.method == "GET":
        allCategories = Category.objects.all()
        return render(request, "auctions/create.html",{
            "categories": allCategories 
        })
    else:
        # get the data from the form
        title = request.POST["title"]
        description = request.POST["description"]
        image = request.POST["imageUrl"]
        price = request.POST["price"]
        category = request.POST["category"]
        # who is user
        currentUser = request.user
        # Get all cntent abut the particular categry
        categoryData = Category.objects.get(categoryname = category)
        # Create a Bid object
        bid = Bid(bid = float(price),user = currentUser).save()
        # Create a new listening object
        newListening = Listner(
            title = title,
            description = description,
            imageUrl = image,
            price = bid,
            category = categoryData,
            owner = currentUser
        )
        # Insert the object in oour database
        newListening.save()
        # Redirect to index page
        return HttpResponseRedirect(reverse(index))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
