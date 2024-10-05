from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('make_forecast/', views.make_forecast, name='make_forecast'),
    path('add_to_profile/<int:pk>/', views.add_to_profile, name='add_to_profile'),

]
