from nhlscrapi.games.game import Game, GameKey, GameType
from nhlscrapi.games.cumstats import Score, ShotCt, Corsi, Fenwick
import mysql.connector
from mysql.connector import errorcode
import threading
import time
import queue
from datetime import date


class NhlStatScraper(object):
	"""
	This is the primary interface for interacting with the database for storing  NHL player
	statistics. There is a database schema picture in the git repository to show the setup
	of the database.
		:param sqlConfig: connection information for the sql database, DEFAULT: sql_info.config
		:param season: Season that you want to parse, marked by the end year of that season, e.g. 2018-2019
						season is represented by a value of 2019,Min Value: 2008 DEFAULT: 2019
		:param firstGame: First game to start looking at, Min Value: 1, Max Value: 1271, DEFAULT: 1
		:param lastGame: Last game to start looking at, has to be larger than firstGame, Min Value: 1, Max Value: 1271, DEFAULT: 1
	"""
	
	

	def __init__(self, sqlConfig="sql_info.config", season=2019, firstGame=1, lastGame=1):
		self.retrieved = False
		self.error = False
		self.parsed = False
		self.data_queue = queue.Queue(300)
		self.team_ids = {}
		self.player_ids = {}
		self.sqlConfig = sqlConfig
		self.config = { 'user':"", 'password':'', 'host':'',
						'database':'', 'raise_on_warnings':True }
		if season < 2008:
			self.season = 2008
		elif season > date.today().year:
			self.season = date.today().year
		else:
			self.season = season
		if firstGame < 1:
			self.firstGame = 1
		elif firstGame >1271:
			self.firstGame = 1
		else:
			self.firstGame = firstGame
		if lastGame < self.firstGame:
			self.lastGame = self.firstGame
		elif lastGame > 1271:
			self.lastGame = 1271
		else:
			self.lastGame = lastGame


	def parseConfig(self):
		"""
		Parse the provided config file for information needed to connect to the Database
		"""
		with open(self.sqlConfig,"r") as config:
			for line in config:
				if "user" in line:
					self.config['user'] = line[line.find("=") + 1:].strip()
				elif "pass" in line:
					self.config['password']= line[line.find("=") + 1:].strip()
				elif "host" in line:
					self.config['host'] = line[line.find("=") + 1:].strip()
				elif "db" in line:
					self.config['database']= line[line.find("=") + 1:].strip()
					
					
	def threadRetrieveStats(self):
		curr_game = self.firstGame
		while curr_game <= self.lastGame:
			if self.error:
				return
			if not self.RetrieveSingleGameData(self.season,curr_game):
				self.error = True
				return
			curr_game += 1
		self.retrieved = True


	def threadParseData(self):
		last_check = False
		while not self.parsed:
			try:
				data = self.data_queue.get(block=True, timeout=30)
				last_check = False
				self.ParseDataFromQueue(data)
			except queue.Empty as err:
				if self.error:
					print("Error ocurred elsewhere, stopping")
					return
				elif self.last_check:
					print("Did a final check, no more data left.")
					self.parsed = True
					return
				elif self.retrieved:
					print("First empty result: mark for last check")
					last_check = True
			except Exception as e:
				print(e)
				self.error = True
				print("Unknown error occured stopping")
				return
		return

					
	def start(self):
		print("BEGINNING OF START FUNCTION")
		fetch_thread = threading.Thread(target=self.threadRetrieveStats)
		print("AFTER FETCH THREAD")
		parse_thread = threading.Thread(target=self.threadParseData)
		parse_thread2 = threading.Thread(target=self.threadParseData)
		print("Starting Fetch Thread")
		fetch_thread.start()
		print("Starting Parse Thread")
		parse_thread.start()
		time.sleep(30)
		print("Starting Parse Thread 2")
		parse_thread2.start()
		fetch_thread.join()
		parse_thread.join()
		

	
	def newTeam(self,name):
		team_id = 0
		try:
			conn = mysql.connector.connect(**self.config)
			cursor = conn.cursor()
			comm = "INSERT INTO tblteams(name) VALUES(\""+name+"\")"
			cursor.execute(comm)
			team_id = cursor.lastrowid
			cursor.close()
			conn.commit()
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Invalid Username/Password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
			return -1
		else:
			conn.close()
			self.team_ids[name] = team_id
		return team_id


	def newPlayer(self,first_name,last_name, position):
		player_id = 0
		try:
			conn = mysql.connector.connect(**self.config)
			cursor = conn.cursor()
			comm = ("INSERT INTO tblplayer(first_name, last_name, position)" 
					"VALUES(%s,%s,%s)")
			data = (str(first_name),str(last_name),str(position))
			cursor.execute(comm,data)
			player_id = cursor.lastrowid
			cursor.close()
			conn.commit()
			self.player_ids[first_name + " " +last_name]=player_id
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Invalid Username/Password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
			return -1
		else:
			conn.close()
		return player_id

	
	def loadTeams_Players(self):
		"""
		Load the known player_ids and team_ids from the database
		"""
		try:
			conn = mysql.connector.connect(**self.config)
			cursor = conn.cursor()
			query = "SELECT team_id, name FROM tblteams where active=1"
			cursor.execute(query)
			for (team_id, name) in cursor:
				self.team_ids[name]=team_id	
			query = "SELECT player_id, first_name, last_name FROM tblplayer WHERE active=1"
			cursor.close()
			cursor = conn.cursor()
			cursor.execute(query)
			for (player_id, first_name, last_name) in cursor:
				self.player_ids[first_name + " " +last_name] = player_id
			cursor.close()
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Invalid Username/Password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
			return False
		else:
			conn.close()
		return True


	def testConnection(self):
		"""
		Test the connection to the database to ensure we have the correct information
		"""
		try:
			conn = mysql.connector.connect(**self.config)
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Invalid Username/Password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
			return False
		else:
			conn.close()
		return True


	def ParseDataFromQueue(self,data):
		"""
		Parse the provided data into data ready to be push to the database and push it to the database
		:param data: Data that needs to be parsed.
		"""
		pname = data['name']['first'] + " " + data['name']['last']
		p_id = 0
		t_id = 0
		if pname not in self.player_ids:
			p_id = self.newPlayer(data['name']['first'], data['name']['last'],data['pos'])
		else:
			p_id = self.player_ids[pname]
		if data['team'] not in self.team_ids:
			t_id = self.newTeam(data['team'])
		else:
			t_id = self.team_ids[data['team']]
		if p_id == -1 or t_id == -1:
			print("Returning here")
			return False
		toi_avg = "00:" + str(data['toi']['avg']['min'])+ ":" + str(data['toi']['avg']['sec'])
		toi_pp = "00:" + str(data['toi']['pp']['min'])+ ":" + str(data['toi']['pp']['sec'])
		toi_sh = "00:" + str(data['toi']['sh']['min'])+ ":" + str(data['toi']['sh']['sec'])
		toi_ev = "00:" + str(data['toi']['ev']['min'])+ ":" + str(data['toi']['ev']['sec'])
		query = ("INSERT INTO tblgame_stats(game_id, player_id, team_id, shifts, goals, assists, plus_minus,"
					"penalties, penalty_min, shots, ab, ms, ht, gv, tk, bs, toi_avg, toi_pp, toi_sh, toi_ev,"
					"faceoffs, faceoff_wins) VALUES( " + str(data['game_id'])+","+str(p_id)+","+str(t_id)+","+str(data['shifts']) +
					","+str(data['g'])+","+str(data['a'])+","+str(data['pm']) + ","+str(data['pn'])+"," + str(data["pim"]) +
					","+str(data['s'])+","+str(data['ab'])+","+str(data['ms'])+","+str(data['ht'])+","+str(data['gv'])+
					","+str(data['tk'])+","+str(data['bs'])+",'"+toi_avg+"','"+toi_pp+"','"+toi_sh+"','"+toi_ev+"',"+
					str(data['fo']['total'])+","+str(data['fo']['won'])+")")
		try:
			conn = mysql.connector.connect(**self.config)
			cursor = conn.cursor()
			cursor.execute(query)
			cursor.close()
			conn.commit()
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Invalid Username/Password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
			return -1
		else:
			conn.close()


	def insertGameInfo(self, season, game, matchup):
		game_id = 0
		try:
			conn = mysql.connector.connect(**self.config)
			cursor = conn.cursor()
			hteam_id = 0
			ateam_id = 0
			if str(matchup["home"]) not in self.team_ids:
				hteam_id = self.newTeam(str(matchup["home"]))
			else:
				hteam_id = self.team_ids[str(matchup["home"])]
			if str(matchup["away"]) not in self.team_ids:
				ateam_id = self.newTeam(str(matchup["away"]))
			else:
				ateam_id = self.team_ids[str(matchup["away"])]
			if ateam_id == -1 or hteam_id == -1:
				return False
			hscore =int(matchup['final']['home'])
			ascore =int(matchup['final']['away'])
			comm = ("INSERT INTO tblgame"
					"(season, date, away_team, home_team, away_score, home_score, game_type, game_no) "
					"VALUES("+str(season)+",\""+str(matchup['date'])+"\",\""+str(ateam_id)+"\",\""
					+str(hteam_id)+"\","+str(ascore)+","+str(hscore)+",2,"+str(game)+")")
			cursor.execute(comm)
			game_id = cursor.lastrowid
			cursor.close()
			conn.commit()
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
				print("Invalid Username/Password")
			elif err.errno == errorcode.ER_BAD_DB_ERROR:
				print("Database does not exist")
			else:
				print(err)
			return -1
		else:
			conn.close()
		return game_id


	def RetrieveSingleGameData(self, season, game, game_type=2):
		"""
		Retrieve Data from Specified Game
		TODO: Support pulling data from playoffs and preseason
		:param season: Season the game took place in
		:param game: number of the game to retrieve
		:param game_type: Type of game that we are attempting to grab, 1 = Preseason, 2 = Regular Season,
							3 = Playoff, DEFAULT 2
		"""
		gk = GameKey(season, game_type, game)
		g = Game(gk)
		data = g.load_all()
		if g.matchup == None:
			print("Unable to get matchup")
			return False
		game_id = self.insertGameInfo(season,game,g.matchup)
		teamName = g.matchup['home']
		self.addGameDataToQueueWithTeam(teamName, g.event_summary.home_players, game_id)
		teamName = g.matchup['away']
		self.addGameDataToQueueWithTeam(teamName, g.event_summary.away_players, game_id)
		return True


	def addGameDataToQueueWithTeam(self, teamName, teamData, game_id):
		"""
		Add Provided data to the queue while including the team name.
		:param teamName: Name of the team to be included in data
		:param teamData: Dictionary of player data for that game.
		"""
		for key in teamData.keys():
			teamData[key]['team'] = teamName
			teamData[key]['game_id'] = game_id
			self.data_queue.put(teamData[key])


def main():
	scrapper = NhlStatScraper(lastGame=1000)
	scrapper.parseConfig()
	scrapper.start()

if __name__ == "__main__":
	main()
