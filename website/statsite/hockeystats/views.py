from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from .forms import TeamsForm
from django_tables2 import RequestConfig
import mysql.connector
from .models import Team, Player, Game
from .tables import TeamStatTable, PlayersStatTable, GameStatTable

config={'user':'websiteaccess', 'password':'Django3!!2', 'host':'127.0.0.1',
		'database':'playerstatistics','raise_on_warnings':True}

# Create your views here.
def index(request):
	team_stats = []
	form = TeamsForm()
	teams = Team.objects.all()
	conn = mysql.connector.connect(**config)
	for team in teams:
		team_id = team.team_id
		name = team.name
		cursor = conn.cursor()
		cursor.callproc('GET_TEAM_STATS',(team_id,2019))
		for buff in cursor.stored_results():
			result = buff.fetchall()
			games = result[0][0]
			wins = result[0][1]
			losses = result[0][2]
		team_stats.append({'team_id':team_id,'Name':name,'Games':games,'Wins':wins,'Losses':losses})
		cursor.close
	conn.close()
	table = TeamStatTable(team_stats)
	RequestConfig(request, paginate={'per_page':len(team_stats)}).configure(table)
	return render(request, 'hockeystats/index.html', {'form':form, 'people':table})
	
def team(request, selected_id):
	if request.method == 'POST':
		team_id = request.POST['team']
		print(team_id)
		return HttpResponseRedirect(reverse('hockeystats:team',args=(team_id,)))
	else:
		player_stats = []
		player_ids = []
		team = Team.objects.get(team_id=selected_id)
		team_name = team.name.lower().capitalize()
		conn = mysql.connector.connect(**config)
		form_info = TeamsForm()
		_id = team.team_id
		cursor = conn.cursor()
		cursor.callproc('GET_PLAYER_LIST',(selected_id,))
		for buff in cursor.stored_results():
			result = buff.fetchall()
			for id in result:
				player_ids.append(id[0])
		for id in player_ids:
			player = Player.objects.get(player_id=id)
			name = player.first_name + " " + player.last_name
			cursor.close()
			cursor = conn.cursor()
			cursor.callproc('GET_PLAYER_STATS',(id,2019))
			for buff in cursor.stored_results():
				result = buff.fetchall()
				points = result[0][0]
				goals = result[0][1]
				assists = result[0][2]
				p_m = result[0][3]
				pen = result[0][4]
				pen_min = result[0][5]
				shots = result[0][6]
				ab = result[0][7]
				ms = result[0][8]
				ht = result[0][9]
				gv = result[0][10]
				tk = result[0][11]
				bs = result[0][12]
				player_stats.append({'player_id':id, 'Name':name, 'Points':points, 'Goals':goals, "Assists":assists, "Plus_Minus":p_m,
									"Penalties":pen, 'Penalty_Min':pen_min, 'Shots':shots, 'AB':ab, 'MS':ms, 'HT':ht, 'GV':gv, 
									'TK':tk, 'BS':bs})
		cursor.close()
		conn.close()
		table = PlayersStatTable(player_stats)
		RequestConfig(request, paginate={'per_page':len(player_stats)}).configure(table)
		return render(request, 'hockeystats/team.html', {'team_id':_id, 'form':form_info,'team_name':team_name,'players':table})

def player(request, selected_id):
	game_stats=[]
	team_id = -1;
	conn = mysql.connector.connect(**config)
	cursor = conn.cursor()
	cursor.callproc("GET_ALL_GAME_STATS",(selected_id,2019))
	player = Player.objects.get(player_id=selected_id)
	name = player.first_name.lower().capitalize() + " " + player.last_name.lower().capitalize()
	print(name)
	for buff in cursor.stored_results():
		results = buff.fetchall()
		for result in results:
			team_name = ""
			if team_id == -1:
				team_id = result[1]
			game = Game.objects.get(game_id=result[0])
			if game.home_team == team_id:
				team = Team.objects.get(team_id=game.away_team)
				team_name = team.name
			else:
				team = Team.objects.get(team_id=game.home_team)
				team_name = team.name
			goals = result[2]
			assists = result[3]
			points = goals + assists
			p_m = result[4]
			pen = result[5]
			pen_min = result[6]
			shots = result[7]
			ab = result[8]
			ms = result[9]
			ht = result[10]
			gv = result[11]
			tk = result[12]
			bs = result[13]
			shifts = result[14]
			total = result[15]
			avg = result[16]
			pp = result[17]
			sh = result[18]
			ev = result[19]
			face = result[20]
			face_win = result[21]
			game_stats.append({'team':team_name, 'Points':points, 'Goals':goals, 'Assists':assists, 'p_m':p_m, 'Penalties':pen, 'Penalty_Min':pen_min,
								'Shots':shots, 'AB':ab, 'MS':ms, 'HT':ht, 'GV':gv, 'TK':tk, 'BS':bs, 'Shifts':shifts, 'total':total, 'avg':avg,
								'ev':ev, 'pp':pp, 'sh':sh, 'face':face, 'face_wins':face_win})
	cursor.close()
	conn.close()
	table = GameStatTable(game_stats)
	RequestConfig(request, paginate={'per_page':len(game_stats)}).configure(table)
	return render(request, 'hockeystats/player.html', {'player_name':name, 'games':table})

