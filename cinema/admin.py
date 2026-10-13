from django.contrib import admin
from .models import Movie, Showtime, SeatBooking, MovieReview

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration_display', 'release_date', 'avg_rating_display', 'review_count_display')
    list_filter = ('genre', 'release_date')
    search_fields = ('title', 'description')
    ordering = ('-release_date',)

    def duration_display(self, obj):
        return obj.formatted_duration
    duration_display.short_description = 'Duration'

    def avg_rating_display(self, obj):
        avg = obj.average_rating
        return f"{avg} ★" if avg else "No ratings"
    avg_rating_display.short_description = 'Avg Rating'

    def review_count_display(self, obj):
        return obj.review_count
    review_count_display.short_description = 'Reviews'


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'show_date', 'show_time_display', 'screen_number', 'ticket_price', 'booked_seats_count')
    list_filter = ('show_date', 'screen_number', 'movie')
    search_fields = ('movie__title', 'screen_number')
    ordering = ('show_date', 'show_time')

    def show_time_display(self, obj):
        return obj.formatted_time
    show_time_display.short_description = 'Time'

    def booked_seats_count(self, obj):
        return len(obj.get_booked_seats_list())
    booked_seats_count.short_description = 'Booked Seats'


@admin.register(SeatBooking)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_reference', 'movie_title', 'customer_name', 'customer_email', 'selected_seats', 'total_paid', 'created_at')
    list_filter = ('showtime__show_date', 'showtime__movie')
    search_fields = ('booking_reference', 'customer_name', 'customer_email', 'customer_phone', 'selected_seats')
    readonly_fields = ('booking_reference', 'created_at')
    ordering = ('-created_at',)

    def movie_title(self, obj):
        return obj.showtime.movie.title
    movie_title.short_description = 'Movie'


@admin.register(MovieReview)
class MovieReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'reviewer_name', 'rating_stars', 'created_date')
    list_filter = ('rating', 'created_date', 'movie')
    search_fields = ('movie__title', 'reviewer_name', 'comment')
    ordering = ('-created_date',)

    def rating_stars(self, obj):
        return f"{'★' * obj.rating}{'☆' * (5 - obj.rating)}"
    rating_stars.short_description = 'Rating'
