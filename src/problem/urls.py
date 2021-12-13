from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.problems_view),
    path("salut/", views.test),
    path("<str:problem_id>", views.problem_view, name="problem")
]
