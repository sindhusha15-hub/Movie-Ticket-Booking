# Cineverse — Movie Ticket Booking & Community Review Portal
**Django Full-Stack Capstone Project**

[![Django](https://img.shields.io/badge/Django-6.x-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![Gunicorn](https://img.shields.io/badge/Gunicorn-21.2-499848?style=for-the-badge&logo=gunicorn&logoColor=white)](https://gunicorn.org/)
[![Render](https://img.shields.io/badge/Deploy%20on-Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)](https://render.com/)

An interactive web portal for movie showtimes, dynamic 5×8 seat selection with real-time price calculations, double-booking prevention, community star reviews, and digital ticket boarding passes.

---

## 🌟 Key Features

- **Cinema-Style Interface**: Modern dark theme with cinema gold and crimson accents, glassmorphism cards, and responsive navigation.
- **Interactive 5×8 Seat Matrix**:
  - 5 rows (Rows A to E) × 8 columns (1 to 8) = 40 cinema seats.
  - Screen arc indicator with glowing lighting effects.
  - Seat states: Available, Selected (gold glow), and Booked / Sold Out (unclickable).
  - Real-time dynamic ticket calculation (`seat count × price per seat = grand total`).
- **Server-Side Booking Validation**:
  - Validates seat numbers against the 5×8 matrix.
  - Prevents duplicate seat bookings for the same showtime.
  - Calculates and verifies total payment on the server.
- **1–5 Star Community Reviews**:
  - Interactive star rating widget with hover preview.
  - Rating breakdown bar chart and overall average rating.
  - Verified audience review comments.
- **Digital Boarding Pass & Lookup**:
  - Perforated cinema ticket receipt with unique reference code (`CINE-XXXXXX`) and simulated barcode.
  - One-click print / save ticket.
  - "My Bookings" lookup to find reservations by code or customer email.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Django 6.x, Django ORM
- **Database**: SQLite (`db.sqlite3`)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, Bootstrap Icons
- **Static Assets**: WhiteNoise
- **WSGI Server**: Gunicorn
- **Deployment**: Render (`render.yaml` Blueprint)

---

## 🚀 Quick Start (Local Setup)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sindhusha15-hub/Movie-Ticket-Booking.git
   cd Movie-Ticket-Booking
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations and seed sample data**:
   ```bash
   python manage.py migrate
   python seed_data.py
   ```
   *(This creates the admin user `admin` with password `admin123` and loads sample movies, showtimes, and reviews.)*

5. **Start the local server**:
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🧪 Running Unit Tests

Run the comprehensive test suite to verify models, duplicate booking prevention, calculations, and views:
```bash
python manage.py test
```

---

## 🌐 Deploying to Render

This project includes a standardized `render.yaml` file:

1. Push this repository to GitHub.
2. Sign in to [Render](https://render.com/).
3. Click **New +** &rarr; **Blueprint** (or **Web Service**).
4. Connect this GitHub repository.
5. Render will automatically build using:
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate && python create_superuser.py
   ```
   and start using:
   ```bash
   python manage.py migrate && python create_superuser.py && gunicorn movieportal.wsgi:application
   ```
6. Open your live `.onrender.com` application URL!

---

## 👤 Author
- **GitHub**: [@sindhusha15-hub](https://github.com/sindhusha15-hub)
