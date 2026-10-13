import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movieportal.settings')
django.setup()

from django.contrib.auth import get_user_model
from cinema.models import Movie, Showtime, SeatBooking, MovieReview
from datetime import date, time, timedelta
from decimal import Decimal

User = get_user_model()

def create_admin():
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@cineverse.local')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser '{username}'...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created successfully.")
    else:
        print(f"Superuser '{username}' already exists.")

def seed_database():
    if Movie.objects.count() > 0:
        print(f"Database already contains {Movie.objects.count()} movies. Skipping sample seed.")
        return

    print("Seeding sample movies, showtimes, reviews, and bookings...")

    sample_movies = [
        {
            'title': 'Dune: Part Two',
            'genre': 'Sci-Fi',
            'duration': 166,
            'release_date': date(2024, 3, 1),
            'poster_url': 'https://image.tmdb.org/t/p/w600_and_h900_bestv2/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg',
            'description': 'Paul Atreides unites with Chani and the Fremen while seeking revenge against the conspirators who destroyed his family. Facing a choice between the love of his life and the fate of the universe, he endeavors to prevent a terrible future only he can foresee.'
        },
        {
            'title': 'Oppenheimer',
            'genre': 'Drama',
            'duration': 180,
            'release_date': date(2023, 7, 21),
            'poster_url': 'https://image.tmdb.org/t/p/w600_and_h900_bestv2/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg',
            'description': 'The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II, exploring the moral complexity and seismic historical impact of his genius.'
        },
        {
            'title': 'Spider-Man: Across the Spider-Verse',
            'genre': 'Animation',
            'duration': 140,
            'release_date': date(2023, 6, 2),
            'poster_url': 'https://image.tmdb.org/t/p/w600_and_h900_bestv2/8Vt6mWEReuy4Of61Lnj5Xj704m8.jpg',
            'description': 'Miles Morales catapults across the Multiverse, where he encounters a team of Spider-People charged with protecting its very existence. When the heroes clash on how to handle a new threat, Miles must redefine what it means to be a hero.'
        },
        {
            'title': 'The Batman',
            'genre': 'Action',
            'duration': 176,
            'release_date': date(2022, 3, 4),
            'poster_url': 'https://image.tmdb.org/t/p/w600_and_h900_bestv2/74xTEgt7R36Fpooo50r9T25onhq.jpg',
            'description': 'In his second year of fighting crime, Batman uncovers corruption in Gotham City that connects to his own family while facing a serial killer known as the Riddler who targets Gotham’s elite.'
        },
        {
            'title': 'Interstellar',
            'genre': 'Sci-Fi',
            'duration': 169,
            'release_date': date(2014, 11, 7),
            'poster_url': 'https://image.tmdb.org/t/p/w600_and_h900_bestv2/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
            'description': 'When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot, Joseph Cooper, is tasked to pilot a spacecraft along with a team of researchers to find a new planet for humans.'
        },
        {
            'title': 'A Quiet Place: Day One',
            'genre': 'Horror',
            'duration': 100,
            'release_date': date(2024, 6, 28),
            'poster_url': 'https://image.tmdb.org/t/p/w600_and_h900_bestv2/yrpPYK2qm0699ZPxAb5GxtMkHEW.jpg',
            'description': 'Experience the day the world went quiet in this terrifying continuation. A young woman named Sam must navigate the chaotic first hours of an alien invasion in bustling New York City.'
        }
    ]

    today = date.today()

    for m_data in sample_movies:
        movie = Movie.objects.create(**m_data)

        # Create multiple showtimes across today and upcoming days
        st1 = Showtime.objects.create(
            movie=movie,
            show_date=today,
            show_time=time(14, 30),
            ticket_price=Decimal('14.00'),
            screen_number='Screen 1 - IMAX Laser'
        )
        st2 = Showtime.objects.create(
            movie=movie,
            show_date=today,
            show_time=time(18, 0),
            ticket_price=Decimal('16.50'),
            screen_number='Screen 2 - Dolby Cinema'
        )
        st3 = Showtime.objects.create(
            movie=movie,
            show_date=today + timedelta(days=1),
            show_time=time(20, 15),
            ticket_price=Decimal('14.00'),
            screen_number='Screen 1 - IMAX Laser'
        )

        # Pre-seed some reviews
        MovieReview.objects.create(
            movie=movie,
            reviewer_name='Eleanor Vance',
            rating=5,
            comment=f"An absolute masterpiece on the big screen! The sound design and visuals in {movie.title} were breathtaking."
        )
        MovieReview.objects.create(
            movie=movie,
            reviewer_name='Marcus Brody',
            rating=4,
            comment=f"Terrific cinematic experience. Great pacing and exceptional performances all around. Highly recommended!"
        )

        # Pre-seed an existing booking on st1 so some seats (e.g. C4, C5) are already booked for duplicate prevention testing!
        SeatBooking.objects.create(
            showtime=st1,
            customer_name='Jordan Reed',
            customer_email='jordan.reed@example.com',
            customer_phone='+1 (555) 234-5678',
            selected_seats='C4, C5',
            total_paid=Decimal('28.00')
        )

    print("Sample data populated successfully!")

if __name__ == '__main__':
    create_admin()
    seed_database()
