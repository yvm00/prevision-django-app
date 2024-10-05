from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [

    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('edit/', views.editProfile, name='edit'),

]
