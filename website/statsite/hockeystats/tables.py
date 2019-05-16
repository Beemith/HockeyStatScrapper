import django_tables2 as tables

class TeamStatTable(tables.Table):
	team_id= tables.Column(visible=False)
	Name = tables.Column(linkify=("hockeystats:team",{'selected_id':tables.A("team_id")}))
	Games = tables.Column()
	Wins = tables.Column()
	Losses = tables.Column()
	
	class Meta:
		template_name = 'django_tables2/semantic.html'
		
class PlayersStatTable(tables.Table):
	player_id = tables.Column(visible=False)
	Name = tables.Column(linkify=("hockeystats:player",{"selected_id":tables.A("player_id")}))
	Points = tables.Column()
	Goals = tables.Column()
	Assists = tables.Column()
	Plus_Minus = tables.Column(verbose_name="Plus/Minus")
	Penalties = tables.Column()
	Penalty_Min = tables.Column(verbose_name="Penalty Minutes")
	Shots = tables.Column()
	AB = tables.Column()
	MS = tables.Column()
	HT = tables.Column()
	GV = tables.Column()
	TK = tables.Column()
	BS = tables.Column()
	
	class Meta:
		template_name = 'django_tables2/semantic.html'
		
class GameStatTable(tables.Table):
	team = tables.Column(verbose_name="Opposing Team")
	Points = tables.Column()
	Goals = tables.Column()
	Assists = tables.Column()
	p_m = tables.Column(verbose_name="Plus/Minus")
	Penalties = tables.Column()
	Penalty_Min = tables.Column(verbose_name="Penalty Mintues")
	Shots = tables.Column()
	AB = tables.Column()
	MS = tables.Column()
	HT = tables.Column()
	GV = tables.Column()
	TK = tables.Column()
	BS = tables.Column()
	Shifts = tables.Column()
	total = tables.Column(verbose_name="Total TOI")
	avg = tables.Column(verbose_name="Avg TOI")
	ev = tables.Column(verbose_name="TOI EVEN")
	pp = tables.Column(verbose_name="TOI PP")
	sh = tables.Column(verbose_name="TOI PK")
	face = tables.Column(verbose_name="Faceoffs")
	face_wins = tables.Column(verbose_name="Faceoff Wins")

	class Meta:
		template_name = 'django_tables2/semantic.html'
