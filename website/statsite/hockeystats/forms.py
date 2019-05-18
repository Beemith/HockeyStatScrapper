from django import forms
import mysql.connector
from .models import Team, Game

config={'user':'websiteaccess', 'password':'Django3!!2', 'host':'127.0.0.1',
		'database':'playerstatistics','raise_on_warnings':True}

class TeamsForm(forms.Form):
	data = []
	team_list = Team.objects.all()
	for team in team_list:
		data.append((team.team_id,team.name))
	team = forms.CharField(label="Select a Team",widget=forms.Select(choices=data))
