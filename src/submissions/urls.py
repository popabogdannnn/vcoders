from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.view_all_submissions, name="all_submissions"),
    path("problema/<str:problem_id>", views.view_problem_submissions),
    path("send/", views.send_submission, name="send-submission"),
    path("<int:submission_id>", views.view_submission, name="submission_at_id")
]
