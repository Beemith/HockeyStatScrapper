CREATE TABLE IF NOT EXISTS tblteams(
    team_id INT(11) NOT NULL AUTO_INCREMENT,
    name VARCHAR(45) NOT NULL,
    active INT(11) NOT NULL DEFAULT '1',
    PRIMARY KEY(team_id),
    UNIQUE INDEX team_id_UNIQUE(team_id ASC)
); CREATE TABLE IF NOT EXISTS tblgame(
    game_id INT(11) NOT NULL AUTO_INCREMENT,
    season INT(11) NOT NULL,
    date VARCHAR(45) NOT NULL,
    away_team INT(11) NOT NULL,
    home_team INT(11) NOT NULL,
    away_score INT(11) NOT NULL,
    home_score INT(11) NOT NULL,
    game_type INT(11) NOT NULL,
    game_no INT(11) NOT NULL,
    PRIMARY KEY(game_id),
    UNIQUE INDEX game_id_UNIQUE(game_id ASC),
    INDEX away_team_idx(away_team ASC),
    INDEX home_team_idx(home_team ASC),
    CONSTRAINT away_team FOREIGN KEY(away_team) REFERENCES playerstatistics.tblteams(team_id),
    CONSTRAINT home_team FOREIGN KEY(home_team) REFERENCES playerstatistics.tblteams(team_id)
); CREATE TABLE IF NOT EXISTS tblplayer(
    player_id INT(11) NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(45) NOT NULL,
    last_name VARCHAR(45) NOT NULL,
    active INT(11) NOT NULL DEFAULT '1',
    position VARCHAR(5) NULL DEFAULT NULL,
    PRIMARY KEY(player_id),
    UNIQUE INDEX pinfo_pk_UNIQUE(player_id ASC)
); CREATE TABLE IF NOT EXISTS tblgame_stats(
    gamestat_id INT(11) NOT NULL AUTO_INCREMENT,
    game_id INT(11) NOT NULL,
    player_id INT(11) NOT NULL,
    team_id INT(11) NOT NULL,
    shifts INT(11) NOT NULL,
    goals INT(11) NOT NULL,
    assists INT(11) NOT NULL,
    plus_minus INT(11) NOT NULL,
    penalties INT(11) NOT NULL,
    penalty_min INT(11) NOT NULL,
    shots INT(11) NOT NULL,
    ab INT(11) NOT NULL,
    ms INT(11) NOT NULL,
    ht INT(11) NOT NULL,
    gv INT(11) NOT NULL,
    tk INT(11) NOT NULL,
    bs INT(11) NOT NULL,
    toi_avg TIME NOT NULL,
    toi_pp TIME NOT NULL,
    toi_sh TIME NOT NULL,
    toi_ev TIME NOT NULL,
    faceoffs INT(11) NOT NULL,
    faceoff_wins INT(11) NOT NULL,
    corsi FLOAT NULL DEFAULT NULL,
    fenwick FLOAT NULL DEFAULT NULL,
    PRIMARY KEY(gamestat_id),
    INDEX player_idx(player_id ASC),
    INDEX team_idx(team_id ASC),
    CONSTRAINT player FOREIGN KEY(player_id) REFERENCES tblplayer(player_id),
    CONSTRAINT team FOREIGN KEY(team_id) REFERENCES tblteams(team_id)
); DELIMITER
    $$
CREATE FUNCTION GAMES_PLAYED(id INT, season INT) RETURNS INT(11) READS SQL DATA BEGIN
    DECLARE
        games INT ;
    SELECT
        COUNT(game_id)
    INTO games
FROM
    tblgame
WHERE
    (away_team = id OR home_team = id) AND season = season ; RETURN games ;
END $$
DELIMITER
    ;
DELIMITER
    $$
CREATE PROCEDURE GET_ALL_GAME_STATS(player INT, season INT)
BEGIN
    SELECT
        game.game_id,
        team_id,
        goals,
        assists,
        plus_minus,
        penalties,
        penalty_min,
        shots,
        ab,
        ms,
        ht,
        gv,
        tk,
        bs,
        shifts,
        ADDTIME(toi_pp, ADDTIME(toi_sh, toi_ev)) AS total,
        toi_avg,
        toi_pp,
        toi_sh,
        toi_ev,
        faceoffs,
        faceoff_wins
    FROM
        tblgame_stats AS stats
    INNER JOIN tblgame AS game
    ON
        stats.game_id = game.game_id
    WHERE
        player_id = player AND game.season = season ;
END $$
DELIMITER
    ;
    -- -----------------------------------------------------
    -- procedure GET_PLAYER_LIST
    -- -----------------------------------------------------
DELIMITER
    $$
CREATE PROCEDURE GET_PLAYER_LIST(team INT)
BEGIN
    SELECT DISTINCT
        player_id
    FROM
        tblgame_stats
    WHERE
        team_id = team ;
END $$
DELIMITER
    ;
    -- -----------------------------------------------------
    -- procedure GET_PLAYER_STATS
    -- -----------------------------------------------------
DELIMITER
    $$
CREATE PROCEDURE GET_PLAYER_STATS(player INT, season INT)
BEGIN
    SELECT
        PLAYER_POINTS(player, season) AS points,
        SUM(goals) AS goals,
        SUM(assists) AS assists,
        SUM(plus_minus) AS plus_minus,
        SUM(penalties) AS penalties,
        SUM(penalty_min) AS penalty_min,
        SUM(shots) AS shots,
        SUM(ab) AS ab,
        SUM(ms) AS ms,
        SUM(ht) AS ht,
        SUM(gv) AS gv,
        SUM(tk) AS tk,
        SUM(bs) AS bs
    FROM
        tblgame_stats AS stats
    INNER JOIN tblgame AS game
    ON
        stats.game_id = game.game_id
    WHERE
        player_id = player AND game.season = season ;
END $$
DELIMITER
    ;
    -- -----------------------------------------------------
    -- procedure GET_TEAM_STATS
    -- -----------------------------------------------------
DELIMITER
    $$
CREATE PROCEDURE GET_TEAM_STATS(id INT, season INT)
BEGIN
    SELECT
        GAMES_PLAYED(id, season) AS games,
        WINS(id, season) AS win,
        LOSSES(id, season) AS losses,
        _TIES(id, season) AS _ties ;
END $$
DELIMITER
    ;
    -- -----------------------------------------------------
    -- function LOSSES
    -- -----------------------------------------------------
DELIMITER
    $$
CREATE FUNCTION LOSSES(id INT, season INT) RETURNS INT(11) READS SQL DATA BEGIN
    DECLARE
        games INT ;
    SELECT
        COUNT(game_id)
    INTO games
FROM
    tblgame
WHERE
    season = season AND(
        (
            away_team = id AND away_score < home_score
        ) OR(
            home_team = id AND home_score < away_score
        )
    ) ; RETURN games ;
END $$
DELIMITER
    ;
    -- -----------------------------------------------------
    -- function PLAYER_POINTS
    -- -----------------------------------------------------
DELIMITER
    $$
CREATE FUNCTION PLAYER_POINTS(player INT, season INT) RETURNS INT(11) READS SQL DATA BEGIN
    DECLARE
        points INT ;
    SELECT
        SUM(goals + assists)
    INTO points
FROM
    tblgame_stats stat
INNER JOIN tblgame AS game
ON
    game.game_id = stat.game_id
WHERE
    stat.player_id = player AND game.season = season ; RETURN points ;
END $$
DELIMITER
    ;
    -- -----------------------------------------------------
    -- function WINS
    -- -----------------------------------------------------
DELIMITER
    $$
CREATE FUNCTION WINS(id INT, season INT) RETURNS INT(11) READS SQL DATA BEGIN
    DECLARE
        games INT ;
    SELECT
        COUNT(game_id)
    INTO games
FROM
    tblgame
WHERE
    season = season AND(
        (
            away_team = id AND away_score > home_score
        ) OR(
            home_team = id AND home_score > away_score
        )
    ) ; RETURN games ;
END $$
DELIMITER
    ;
    -- -----------------------------------------------------
    -- function _TIES
    -- -----------------------------------------------------
DELIMITER
    $$
CREATE FUNCTION _TIES(id INT, season INT) RETURNS INT(11) READS SQL DATA BEGIN
    DECLARE
        games INT ;
    SELECT
        COUNT(game_id)
    INTO games
FROM
    tblgame
WHERE
    season = season AND(
        (
            away_team = id AND away_score = home_score
        ) OR(
            home_team = id AND home_score = away_score
        )
    ) ; RETURN games ;
END $$
DELIMITER
    ;