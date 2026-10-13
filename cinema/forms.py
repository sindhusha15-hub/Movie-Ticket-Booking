import re
from decimal import Decimal
from django import forms
from .models import SeatBooking, MovieReview, Showtime

# Valid seats for a 5x8 matrix: Rows A to E, Columns 1 to 8
VALID_ROWS = ['A', 'B', 'C', 'D', 'E']
VALID_COLS = [str(i) for i in range(1, 9)]
ALL_VALID_SEATS = {f"{r}{c}" for r in VALID_ROWS for c in VALID_COLS}

class SeatBookingForm(forms.ModelForm):
    class Meta:
        model = SeatBooking
        fields = ['customer_name', 'customer_email', 'customer_phone', 'selected_seats']
        widgets = {
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your full name',
                'required': True,
                'id': 'customerName'
            }),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
                'required': True,
                'id': 'customerEmail'
            }),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 000-1234',
                'required': True,
                'id': 'customerPhone'
            }),
            'selected_seats': forms.HiddenInput(attrs={
                'id': 'selectedSeatsInput'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.showtime = kwargs.pop('showtime', None)
        super().__init__(*args, **kwargs)

    def clean_selected_seats(self):
        seats_str = self.cleaned_data.get('selected_seats', '')
        if not seats_str:
            raise forms.ValidationError("Please select at least one seat before proceeding to booking.")

        # Split and sanitize
        raw_seats = [s.strip().upper() for s in seats_str.split(',') if s.strip()]
        if not raw_seats:
            raise forms.ValidationError("Please select at least one seat before proceeding to booking.")

        # Check uniqueness within the selection itself
        if len(raw_seats) != len(set(raw_seats)):
            raise forms.ValidationError("Duplicate seat numbers were detected in your selection.")

        # Validate against the 5x8 grid matrix
        invalid_seats = [s for s in raw_seats if s not in ALL_VALID_SEATS]
        if invalid_seats:
            raise forms.ValidationError(f"Invalid seat code(s): {', '.join(invalid_seats)}. Seats must be from the 5x8 grid (A1-E8).")

        # Crucial Requirement: Prevent double-booking for the same showtime!
        if self.showtime:
            already_booked = set(self.showtime.get_booked_seats_list())
            conflicts = [s for s in raw_seats if s in already_booked]
            if conflicts:
                raise forms.ValidationError(
                    f"Seats already booked for this showtime: {', '.join(conflicts)}. Please choose other available seats."
                )

        return ', '.join(sorted(raw_seats))

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.showtime:
            instance.showtime = self.showtime
            seat_count = instance.seat_count
            instance.total_paid = Decimal(seat_count) * self.showtime.ticket_price
        if commit:
            instance.save()
        return instance


class MovieReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(attrs={'id': 'reviewRatingInput', 'value': '5'})
    )

    class Meta:
        model = MovieReview
        fields = ['reviewer_name', 'rating', 'comment']
        widgets = {
            'reviewer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name or Nickname',
                'required': True,
                'id': 'reviewerName'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your thoughts about the movie, acting, visuals, or soundtrack...',
                'required': True,
                'id': 'reviewComment'
            }),
        }

    def clean_comment(self):
        comment = self.cleaned_data.get('comment', '').strip()
        if len(comment) < 5:
            raise forms.ValidationError("Review comment must be at least 5 characters long.")
        return comment
