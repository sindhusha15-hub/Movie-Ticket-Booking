from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_id>/review/', views.add_review, name='add_review'),
    path('booking/<int:showtime_id>/', views.seat_booking, name='seat_booking'),
    path('booking/confirmation/<str:reference>/', views.booking_confirmation, name='booking_confirmation'),
    path('booking/lookup/', views.booking_lookup, name='booking_lookup'),
    path('api/showtime/<int:showtime_id>/seats/', views.showtime_seats_api, name='showtime_seats_api'),
]
