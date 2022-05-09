from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path("", views.problems_view),
    path("concursuri/", views.contests_view, name="contest_archive"),
    path("concursuri/<int:sub_contest_id>", views.sub_contest_view, name="sub_contest"),
    path("adauga/", views.add_problem_view, name="add_problem"),
    path("adauga/<str:title_id>", views.edit_problem_view, name="edit_problem"),
    path("enunt/<str:problem_id>", views.problem_view, name="problem"),
]
