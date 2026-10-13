from decimal import Decimal
from datetime import date, time
from django.test import TestCase, Client
from django.urls import reverse
from .models import Movie, Showtime, SeatBooking, MovieReview
from .forms import SeatBookingForm, MovieReviewForm

class CinemaModelAndWorkflowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.movie = Movie.objects.create(
            title="Inception",
            genre="Sci-Fi",
            duration=148,
            release_date=date(2010, 7, 16),
            poster_url="https://image.tmdb.org/t/p/w600_and_h900_bestv2/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg",
            description="A thief who steals corporate secrets through dream-sharing technology."
        )
        self.showtime = Showtime.objects.create(
            movie=self.movie,
            show_date=date.today(),
            show_time=time(19, 0),
            ticket_price=Decimal("15.00"),
            screen_number="Screen 1 - IMAX"
        )

    def test_movie_properties(self):
        self.assertEqual(self.movie.formatted_duration, "2h 28m")
        self.assertIsNone(self.movie.average_rating)
        self.assertEqual(self.movie.review_count, 0)

        # Add reviews
        MovieReview.objects.create(movie=self.movie, reviewer_name="Alice", rating=5, comment="Incredible mind-bending movie.")
        MovieReview.objects.create(movie=self.movie, reviewer_name="Bob", rating=3, comment="A bit confusing but good.")

        self.assertEqual(self.movie.review_count, 2)
        self.assertEqual(self.movie.average_rating, 4.0)

    def test_seat_booking_workflow_and_total_calculation(self):
        form_data = {
            'customer_name': 'John Doe',
            'customer_email': 'john@example.com',
            'customer_phone': '123-456-7890',
            'selected_seats': 'A1, A2'
        }
        form = SeatBookingForm(data=form_data, showtime=self.showtime)
        self.assertTrue(form.is_valid(), form.errors)
        booking = form.save()

        self.assertEqual(booking.seat_count, 2)
        self.assertEqual(booking.total_paid, Decimal("30.00")) # 2 * 15.00
        self.assertTrue(booking.booking_reference.startswith("CINE-"))
        self.assertIn("A1", self.showtime.get_booked_seats_list())
        self.assertIn("A2", self.showtime.get_booked_seats_list())

    def test_duplicate_seat_booking_prevention(self):
        # Book A1 first
        SeatBooking.objects.create(
            showtime=self.showtime,
            customer_name="Existing User",
            customer_email="existing@example.com",
            customer_phone="000-000-0000",
            selected_seats="A1, A2",
            total_paid=Decimal("30.00")
        )

        # Attempt to book overlapping seats: A2 and A3
        conflict_form_data = {
            'customer_name': 'New User',
            'customer_email': 'new@example.com',
            'customer_phone': '111-222-3333',
            'selected_seats': 'A2, A3'
        }
        conflict_form = SeatBookingForm(data=conflict_form_data, showtime=self.showtime)
        self.assertFalse(conflict_form.is_valid())
        self.assertIn("already booked", str(conflict_form.errors['selected_seats']))

    def test_invalid_seat_code_validation(self):
        # F1 is outside the 5x8 grid (Rows A-E, Cols 1-8)
        invalid_form_data = {
            'customer_name': 'User',
            'customer_email': 'user@example.com',
            'customer_phone': '111-222-3333',
            'selected_seats': 'F1, Z9'
        }
        form = SeatBookingForm(data=invalid_form_data, showtime=self.showtime)
        self.assertFalse(form.is_valid())
        self.assertIn("Invalid seat code", str(form.errors['selected_seats']))

    def test_review_rating_validation(self):
        valid_form = MovieReviewForm(data={'reviewer_name': 'Charlie', 'rating': 5, 'comment': 'Loved it!'})
        self.assertTrue(valid_form.is_valid())

        invalid_form_high = MovieReviewForm(data={'reviewer_name': 'Charlie', 'rating': 6, 'comment': 'Too high!'})
        self.assertFalse(invalid_form_high.is_valid())

        invalid_form_low = MovieReviewForm(data={'reviewer_name': 'Charlie', 'rating': 0, 'comment': 'Too low!'})
        self.assertFalse(invalid_form_low.is_valid())

    def test_views_response_codes(self):
        # Movie list
        res = self.client.get(reverse('movie_list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Inception")

        # Movie detail
        res = self.client.get(reverse('movie_detail', args=[self.movie.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Screen 1 - IMAX")

        # Seat booking page
        res = self.client.get(reverse('seat_booking', args=[self.showtime.id]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Interactive Seat Matrix")

        # Seat booking POST submission
        res = self.client.post(reverse('seat_booking', args=[self.showtime.id]), {
            'customer_name': 'Sarah Connor',
            'customer_email': 'sarah@resistance.com',
            'customer_phone': '555-1234',
            'selected_seats': 'B1, B2'
        })
        self.assertEqual(res.status_code, 302) # Redirect to confirmation
        new_booking = SeatBooking.objects.get(customer_email='sarah@resistance.com')
        self.assertEqual(new_booking.selected_seats, 'B1, B2')

        # Confirmation view
        res = self.client.get(reverse('booking_confirmation', args=[new_booking.booking_reference]))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Official E-Ticket")
        self.assertContains(res, new_booking.booking_reference)

        # Booking lookup view
        res = self.client.get(reverse('booking_lookup') + f'?query={new_booking.booking_reference}')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, new_booking.booking_reference)

        # Showtime API
        res = self.client.get(reverse('showtime_seats_api', args=[self.showtime.id]))
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn('B1', data['booked_seats'])
        self.assertIn('B2', data['booked_seats'])
