import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import Movie, Showtime, SeatBooking, MovieReview
from .forms import SeatBookingForm, MovieReviewForm

def movie_list(request):
    """Movie list view with genre filter, search, and average rating."""
    query = request.GET.get('q', '').strip()
    selected_genre = request.GET.get('genre', '').strip()
    sort_by = request.GET.get('sort', '-release_date')

    movies = Movie.objects.all()

    if query:
        movies = movies.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(genre__icontains=query)
        )

    if selected_genre:
        movies = movies.filter(genre__iexact=selected_genre)

    # Sort options
    if sort_by == 'title':
        movies = movies.order_by('title')
    elif sort_by == 'rating':
        movies = movies.annotate(avg_r=Avg('reviews__rating')).order_by('-avg_r', '-release_date')
    else:
        movies = movies.order_by('-release_date')

    # Available genres for filter pills
    all_genres = Movie.GENRE_CHOICES

    # Featured movie (for hero banner)
    featured_movie = Movie.objects.first()

    context = {
        'movies': movies,
        'query': query,
        'selected_genre': selected_genre,
        'sort_by': sort_by,
        'all_genres': all_genres,
        'featured_movie': featured_movie,
        'total_count': movies.count(),
    }
    return render(request, 'cinema/movie_list.html', context)


def movie_detail(request, movie_id):
    """Movie detail page with showtimes, reviews list, and review form."""
    movie = get_object_or_404(Movie, id=movie_id)
    showtimes = movie.showtimes.all().order_by('show_date', 'show_time')
    reviews = movie.reviews.all().order_by('-created_date')
    review_form = MovieReviewForm()

    # Calculate rating breakdown (count of 5-star, 4-star, etc.)
    rating_breakdown = {i: 0 for i in range(1, 6)}
    for r in reviews:
        if 1 <= r.rating <= 5:
            rating_breakdown[r.rating] += 1

    context = {
        'movie': movie,
        'showtimes': showtimes,
        'reviews': reviews,
        'review_form': review_form,
        'rating_breakdown': rating_breakdown,
    }
    return render(request, 'cinema/movie_detail.html', context)


def add_review(request, movie_id):
    """Process review submission."""
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.save()
            messages.success(request, f"Thank you, {review.reviewer_name}! Your {review.rating}-star review for '{movie.title}' was posted successfully.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Review error: {error}")
    return redirect('movie_detail', movie_id=movie.id)


def seat_booking(request, showtime_id):
    """Seat booking workflow: 5x8 seat matrix, calculation, duplicate check."""
    showtime = get_object_or_404(Showtime, id=showtime_id)
    movie = showtime.movie
    other_showtimes = movie.showtimes.exclude(id=showtime.id).order_by('show_date', 'show_time')

    booked_seats = showtime.get_booked_seats_list()

    if request.method == 'POST':
        form = SeatBookingForm(request.POST, showtime=showtime)
        if form.is_valid():
            booking = form.save()
            messages.success(request, f"Booking confirmed! Reference: {booking.booking_reference}")
            return redirect('booking_confirmation', reference=booking.booking_reference)
        else:
            for error in form.non_field_errors():
                messages.error(request, error)
            for field, errors in form.errors.items():
                if field != '__all__':
                    for error in errors:
                        messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = SeatBookingForm(showtime=showtime)

    # 5x8 Grid definition: Rows A to E, Columns 1 to 8
    rows = ['A', 'B', 'C', 'D', 'E']
    cols = list(range(1, 9))

    context = {
        'showtime': showtime,
        'movie': movie,
        'other_showtimes': other_showtimes,
        'form': form,
        'booked_seats': booked_seats,
        'booked_seats_json': json.dumps(booked_seats),
        'rows': rows,
        'cols': cols,
        'ticket_price': float(showtime.ticket_price),
    }
    return render(request, 'cinema/seat_booking.html', context)


def showtime_seats_api(request, showtime_id):
    """API endpoint to get booked seats and price for real-time updates."""
    showtime = get_object_or_404(Showtime, id=showtime_id)
    return JsonResponse({
        'showtime_id': showtime.id,
        'movie_title': showtime.movie.title,
        'show_date': showtime.show_date.strftime('%b %d, %Y'),
        'show_time': showtime.formatted_time,
        'screen_number': showtime.screen_number,
        'ticket_price': float(showtime.ticket_price),
        'booked_seats': showtime.get_booked_seats_list(),
    })


def booking_confirmation(request, reference):
    """Booking confirmation ticket receipt."""
    booking = get_object_or_404(SeatBooking, booking_reference=reference)
    return render(request, 'cinema/booking_confirmation.html', {'booking': booking})


def booking_lookup(request):
    """Lookup existing bookings by reference code or customer email."""
    query = request.GET.get('query', '').strip()
    bookings = []
    has_searched = False

    if query:
        has_searched = True
        bookings = SeatBooking.objects.filter(
            Q(booking_reference__iexact=query) |
            Q(customer_email__iexact=query)
        ).order_by('-created_at')

    context = {
        'query': query,
        'bookings': bookings,
        'has_searched': has_searched,
    }
    return render(request, 'cinema/booking_lookup.html', context)
