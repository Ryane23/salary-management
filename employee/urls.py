from django.urls import path, include

from . import views
urlpatterns = [
    path('list', views.profile, name='employee_profile'), ]  # Dashboard home view 