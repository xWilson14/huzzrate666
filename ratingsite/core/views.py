from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Avg, Count
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import HttpResponse
from .models import Item, Token, Rating
from .forms import TokenLoginForm, RateForm


# Simple homepage view - ADD THIS FUNCTION
def simple_home(request):
    """Simple homepage that shows the app is working"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>HuzzRate - Rating App</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }
            .container { text-align: center; }
            .btn { display: inline-block; padding: 12px 24px; margin: 10px; background: #007bff; 
                   color: white; text-decoration: none; border-radius: 5px; }
            .btn-admin { background: #28a745; }
            .btn-login { background: #ffc107; color: black; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎯 HuzzRate - Rating App</h1>
            <p>Your app is running successfully! 🚀</p>
            
            <div style="margin: 30px 0;">
                <a href="/login/" class="btn btn-login">🔐 Login with Token</a><br>
                <a href="/admin/" class="btn btn-admin">⚙️ Admin Panel</a><br>
                <a href="/leaderboard/" class="btn">📊 View Leaderboard</a>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3>Quick Info:</h3>
                <p><strong>Admin:</strong> admin / admin123</p>
                <p><strong>Tokens:</strong> Use tokens from seed data to login and rate items</p>
                <p><strong>Features:</strong> Rate items, view leaderboard, token-based authentication</p>
            </div>
        </div>
    </body>
    </html>
    """)


# Login required decorator
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        token = __get_token_from_session(request)
        if not token:
            messages.error(request, "Please log in with a token to access this page.")
            return redirect('core:login')
        return view_func(request, *args, **kwargs)
    return wrapper


def __get_token_from_session(request):
    val = request.session.get("token_value")
    if not val:
        return None
    try:
        return Token.objects.get(value=val, active=True)
    except Token.DoesNotExist:
        return None


def login_view(request):
    if request.method == "POST":
        form = TokenLoginForm(request.POST)
        if form.is_valid():
            val = form.cleaned_data["token"].strip()
            try:
                token = Token.objects.get(value=val, active=True)
                request.session["token_value"] = token.value
                messages.success(request, "Logged in with token.")
                return redirect("core:index")
            except Token.DoesNotExist:
                messages.error(request, "Invalid token.")
    else:
        form = TokenLoginForm()
    return render(request, "core/login.html", {"form": form})


def logout_view(request):
    request.session.pop("token_value", None)
    messages.info(request, "Logged out.")
    return redirect("core:login")


@login_required
def index(request):
    token = __get_token_from_session(request)
    items = Item.objects.order_by("-created_at")
    rated_item_ids = set()
    all_rated = False

    if token:
        rated_item_ids = set(token.ratings.values_list("item_id", flat=True))
        all_rated = (len(rated_item_ids) >= items.count())

    # Annotate items with ratings data
    items = items.annotate(
        avg_appearance=Avg("ratings__appearance_score"),
        avg_personality=Avg("ratings__personality_score"),
        ratings_count=Count("ratings")
    )

    # Calculate total average for each item
    for item in items:
        item.avg_total = round(((item.avg_appearance or 0) + (item.avg_personality or 0)) / 2, 2)

    return render(request, "core/index.html", {
        "items": items,
        "token": token,
        "rated_item_ids": rated_item_ids,
        "all_rated": all_rated,
    })

@require_POST
@login_required
def rate_item(request):
    token = __get_token_from_session(request)
    if not token:
        messages.error(request, "You must log in with a token to rate.")
        return redirect("core:login")

    item_id = request.POST.get("item_id")
    appearance_score = request.POST.get("appearance_score")
    personality_score = request.POST.get("personality_score")

    if not item_id or not appearance_score or not personality_score:
        messages.error(request, "Invalid rating data.")
        return redirect("core:index")

    try:
        appearance_score = int(appearance_score)
        personality_score = int(personality_score)
        if not (1 <= appearance_score <= 10) or not (1 <= personality_score <= 10):
            raise ValueError("Scores must be between 1-10")
    except (ValueError, TypeError):
        messages.error(request, "Scores must be numbers between 1-10.")
        return redirect("core:index")

    item = get_object_or_404(Item, id=item_id)
    existing = Rating.objects.filter(token=token, item=item).first()

    if existing:
        messages.error(request, "You already rated this item.")
    else:
        Rating.objects.create(
            token=token,
            item=item,
            appearance_score=appearance_score,
            personality_score=personality_score
        )
        messages.success(request, f"Rated {item.name} - A:{appearance_score} P:{personality_score} 🎯")

        # Check if this was the last item to rate
        rated_count = token.ratings.count()
        total_items = Item.objects.count()
        if rated_count >= total_items:
            request.session['show_leaderboard_popup'] = True

    return redirect("core:index")


@login_required
def leaderboard(request):
    token = __get_token_from_session(request)
    sort_by = request.GET.get('sort', 'total')

    items = Item.objects.annotate(
        avg_appearance=Avg("ratings__appearance_score"),
        avg_personality=Avg("ratings__personality_score"),
        cnt=Count("ratings")
    )

    # Calculate total average for each item
    for item in items:
        item.avg_total = round(((item.avg_appearance or 0) + (item.avg_personality or 0)) / 2, 2)
        item.avg_appearance = round(item.avg_appearance or 0, 2)
        item.avg_personality = round(item.avg_personality or 0, 2)

    # Sort based on user selection
    if sort_by == 'appearance':
        items = sorted(items, key=lambda x: x.avg_appearance, reverse=True)
    elif sort_by == 'personality':
        items = sorted(items, key=lambda x: x.avg_personality, reverse=True)
    else:  # total
        items = sorted(items, key=lambda x: x.avg_total, reverse=True)

    # Check if user has rated all items
    all_rated = False
    if token:
        rated_count = token.ratings.count()
        all_rated = (rated_count >= Item.objects.count())

    return render(request, "core/leaderboard.html", {
        "items": items,
        "current_sort": sort_by,
        "all_rated": all_rated,
    })


@require_POST
@login_required
def reset_ratings(request):
    token = __get_token_from_session(request)
    if not token:
        messages.error(request, "No active token in session.")
        return redirect("core:index")
    Rating.objects.filter(token=token).delete()
    messages.success(request, "Your ratings were reset.")
    return redirect("core:index")
