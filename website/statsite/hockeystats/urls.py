from django.urls import path

from . import views

app_name = "hockeystats"
urlpatterns = [
	path("", views.index, name="index"),
	path("team/<int:selected_id>/",views.team, name="team"),
	path("player/<int:selected_id>/",views.player, name="player")
	]