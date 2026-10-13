import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

class Movie(models.Model):
    GENRE_CHOICES = [
        ('Action', 'Action'),
        ('Sci-Fi', 'Sci-Fi'),
        ('Drama', 'Drama'),
        ('Comedy', 'Comedy'),
        ('Thriller', 'Thriller'),
        ('Animation', 'Animation'),
        ('Horror', 'Horror'),
        ('Adventure', 'Adventure'),
    ]

    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    duration = models.PositiveIntegerField(help_text="Duration in minutes (e.g. 148)")
    release_date = models.DateField()
    poster_url = models.URLField(max_length=500, help_text="Direct URL to movie poster image")
    description = models.TextField()

    class Meta:
        ordering = ['-release_date', 'title']

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg is not None else None

    @property
    def review_count(self):
        return self.reviews.count()

    @property
    def formatted_duration(self):
        hours = self.duration // 60
        mins = self.duration % 60
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    show_date = models.DateField()
    show_time = models.TimeField()
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('12.50'))
    screen_number = models.CharField(max_length=50, help_text="e.g. Screen 1 - IMAX, Screen 2 - Dolby Cinema")

    class Meta:
        ordering = ['show_date', 'show_time']

    def __str__(self):
        return f"{self.movie.title} | {self.show_date} {self.show_time.strftime('%I:%M %p')} ({self.screen_number})"

    def get_booked_seats_list(self):
        """Returns a set/list of all seat numbers already booked for this showtime."""
        booked_seats = set()
        for booking in self.bookings.all():
            for seat in booking.get_seats_as_list():
                booked_seats.add(seat.strip().upper())
        return sorted(list(booked_seats))

    @property
    def formatted_time(self):
        return self.show_time.strftime('%I:%M %p')


class SeatBooking(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='bookings')
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)
    selected_seats = models.CharField(
        max_length=255,
        help_text="Comma-separated seat IDs (e.g. A1, A2, B3)"
    )
    total_paid = models.DecimalField(max_digits=8, decimal_places=2)
    booking_reference = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate a stylish cinema booking reference code like CINE-8F3B91
            ref = f"CINE-{uuid.uuid4().hex[:6].upper()}"
            while SeatBooking.objects.filter(booking_reference=ref).exists():
                ref = f"CINE-{uuid.uuid4().hex[:6].upper()}"
            self.booking_reference = ref
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking_reference} - {self.customer_name} ({self.selected_seats})"

    def get_seats_as_list(self):
        if not self.selected_seats:
            return []
        return [s.strip().upper() for s in self.selected_seats.split(',') if s.strip()]

    @property
    def seat_count(self):
        return len(self.get_seats_as_list())


class MovieReview(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=150)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f"{self.reviewer_name} ({self.rating}★) - {self.movie.title}"
