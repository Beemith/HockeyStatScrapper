from django import forms
import mysql.connector
from .models import Team, Game

config={'user':'websiteaccess', 'password':'Django3!!2', 'host':'127.0.0.1',
		'database':'playerstatistics','raise_on_warnings':True}

class TeamsForm(forms.Form):
	data = []
	game_list= Game.objects.all()
	for game in game_list:
		home = Team.objects.filter(team_id=game.home_team)[0].name
		away = Team.objects.filter(team_id=game.away_team)[0].name
		data.append((game.game_id, home+ " vs " + away))
	team = forms.CharField(label="Team",widget=forms.Select(choices=data))