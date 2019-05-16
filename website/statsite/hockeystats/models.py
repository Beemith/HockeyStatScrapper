# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    season = models.IntegerField()
    date = models.CharField(max_length=45)
    away_team = models.IntegerField()
    home_team = models.IntegerField()
    away_score = models.IntegerField()
    home_score = models.IntegerField()
    game_type = models.IntegerField()
    game_no = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblgame'


class GameStats(models.Model):
    gamestat_id = models.AutoField(primary_key=True)
    game_id = models.IntegerField()
    player = models.IntegerField()
    team = models.IntegerField()
    shifts = models.IntegerField()
    goals = models.IntegerField()
    assists = models.IntegerField()
    plus_minus = models.IntegerField()
    penalties = models.IntegerField()
    penalty_min = models.IntegerField()
    shots = models.IntegerField()
    ab = models.IntegerField()
    ms = models.IntegerField()
    ht = models.IntegerField()
    gv = models.IntegerField()
    tk = models.IntegerField()
    bs = models.IntegerField()
    toi_avg = models.TimeField()
    toi_pp = models.TimeField()
    toi_sh = models.TimeField()
    toi_ev = models.TimeField()
    faceoffs = models.IntegerField()
    faceoff_wins = models.IntegerField()
    corsi = models.FloatField(blank=True, null=True)
    fenwick = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblgame_stats'


class Player(models.Model):
    player_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    active = models.IntegerField()
    position = models.CharField(max_length=5, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tblplayer'


class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=45)
    active = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tblteams'
