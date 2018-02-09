#!/usr/bin/env python3

import csv
import io
import json
import os.path
import sys
import zipfile

import attr


@attr.s
class BaseRuns():
    # Components of BaseRuns
    bb = attr.ib(default=0)
    cs = attr.ib(default=0)
    gdp = attr.ib(default=0)
    h = attr.ib(default=0)
    hbp = attr.ib(default=0)
    hr = attr.ib(default=0)
    ibb = attr.ib(default=0)
    pa = attr.ib(default=0)
    sb = attr.ib(default=0)
    sf = attr.ib(default=0)
    sh = attr.ib(default=0)
    tb = attr.ib(default=0)

    def raw(self):
        # From FanGraphs library page on BaseRuns.
        a = self.h + self.bb + self.hbp - 0.5*self.ibb - self.hr
        b = 1.1 * (1.4*self.tb - 0.6*self.h - 3*self.hr +
                   0.1*(self.bb + self.hbp - self.ibb) +
                   0.9*(self.sb - self.cs - self.gdp))
        c = self.pa - self.bb - self.sf - self.sh - self.hbp - self.h + self.cs + self.gdp
        d = self.hr
        return (a*b / (b+c)) + d


class Team():
    def __init__(self, name, league):
        self.league = league
        self.name = name
        self.wins = 0
        self.losses = 0
        self.games = 0
        self.runs_scored = 0
        self.runs_allowed = 0
        self.baseruns_offense = BaseRuns()
        self.baseruns_defense = BaseRuns()

    def summary(self):
        return {
            'name': self.name,
            'league': self.league.name,
            'win_percentage': self.win_percentage(),
            'pythagenpat_percentage': self.pythagenpat_percentage(),
            'baseruns_percentage': self.baseruns_percentage(),
            'wins': self.wins,
            'losses': self.losses,
            'games': self.games,
        }

    def win_percentage(self):
        return self.wins / (self.wins + self.losses)

    def pythagenpat_percentage(self):
        return self.calculate_pythagenpat(self.runs_scored, self.runs_allowed, self.games)

    def baseruns_percentage(self):
        runs_scored = self.baseruns_scored()
        runs_allowed = self.baseruns_allowed()
        #print(self.name, "RS/G", runs_scored / self.games, "RA/G", runs_allowed / self.games)
        return self.calculate_pythagenpat(runs_scored, runs_allowed, self.games)

    @staticmethod
    def calculate_pythagenpat(runs_scored, runs_allowed, games):
        exponent = ((runs_scored + runs_allowed) / games) ** 0.287
        return 1 / (1 + (runs_allowed / runs_scored) ** exponent)

    def scored(self, runs):
        self.runs_scored += runs
        self.league.runs_scored += runs

    def allowed(self, runs):
        self.runs_allowed += runs
        self.league.runs_allowed += runs

    def _add_baseruns(self, attribute, fields):
        baseruns = getattr(self, attribute)
        baseruns.h += fields[1]
        baseruns.hr += fields[4]
        baseruns.sh += fields[6]
        baseruns.sf += fields[7]
        baseruns.hbp += fields[8]
        baseruns.bb += fields[9]
        baseruns.ibb += fields[10]
        baseruns.sb += fields[12]
        baseruns.cs += fields[13]
        baseruns.gdp += fields[14]

        # Fields that aren't in the data and must be calculated.
        baseruns.pa += (fields[0] + fields[6] + fields[7] + fields[8] + fields[9])
        # The fields are hits, doubles, triples, and home runs.
        baseruns.tb += (fields[1] + fields[2] + fields[3]*2 + fields[4]*3)

    def add_baseruns_offense(self, offense):
        self._add_baseruns('baseruns_offense', offense)
        self.league._add_baseruns('baseruns_offense', offense)

    def add_baseruns_defense(self, defense):
        self._add_baseruns('baseruns_defense', defense)
        self.league._add_baseruns('baseruns_defense', defense)

    def baseruns_scored(self):
        league_adjust = self.league.runs_scored / self.league.baseruns_offense.raw()
        return self.baseruns_offense.raw() * league_adjust

    def baseruns_allowed(self):
        league_adjust = self.league.runs_allowed / self.league.baseruns_defense.raw()
        return self.baseruns_defense.raw() * league_adjust


class League(Team):
    def __init__(self, name):
        super().__init__(name, None)

class Game():
    # Useful offsets for each game log row.
    VISITOR_TEAM = 3
    VISITOR_LEAGUE = 4
    HOME_TEAM = 6
    HOME_LEAGUE = 7
    VISITOR_SCORE = 9
    HOME_SCORE = 10

    VISITOR_OFFENSE = (21, 38)
    HOME_OFFENSE = (49, 66)

    def __init__(self, game):
        self.visitor = game[self.VISITOR_TEAM]
        self.visitor_league = game[self.VISITOR_LEAGUE]
        self.home = game[self.HOME_TEAM]
        self.home_league = game[self.HOME_LEAGUE]
        self.visitor_score = int(game[self.VISITOR_SCORE])
        self.home_score = int(game[self.HOME_SCORE])
        self.visitor_offense = self.intify(game[self.VISITOR_OFFENSE[0]:self.VISITOR_OFFENSE[1]])
        self.home_offense = self.intify(game[self.HOME_OFFENSE[0]:self.HOME_OFFENSE[1]])

    @staticmethod
    def intify(fields):
        values = []
        for field in fields:
            if field:
                values.append(int(field))
            else:
                values.append(0)
        return values

    def winner(self):
        if self.visitor_score > self.home_score:
            return 'visitor'
        elif self.home_score > self.visitor_score:
            return 'home'
        return 'tie'


class Season():
    def __init__(self):
        self.teams = {}
        self.leagues = {}

    def add_game(self, game):
        game = Game(game)

        visitor_league = self.get_league(game.visitor_league)
        visitor = self.get_team(game.visitor, visitor_league)
        home_league = self.get_league(game.home_league)
        home = self.get_team(game.home, home_league)

        winner = game.winner()
        home.games += 1
        visitor.games += 1
        if winner == 'home':
            home.wins += 1
            visitor.losses += 1
        elif winner == 'visitor':
            home.losses += 1
            visitor.wins += 1

        visitor.scored(game.visitor_score)
        visitor.allowed(game.home_score)
        home.scored(game.home_score)
        home.allowed(game.visitor_score)

        visitor.add_baseruns_offense(game.visitor_offense)
        visitor.add_baseruns_defense(game.home_offense)
        home.add_baseruns_offense(game.home_offense)
        home.add_baseruns_defense(game.visitor_offense)

    def get_team(self, team_id, team_league):
        if team_id not in self.teams:
            team = self.teams[team_id] = Team(team_id, team_league)
        else:
            team = self.teams[team_id]
        return team

    def get_league(self, league_id):
        if league_id in self.leagues:
            league = self.leagues[league_id]
        else:
            league = self.leagues[league_id] = League(league_id)
        return league


class Schedule():
    def __init__(self):
        self.schedule = []

    def add_game(self, game):
        if game['visitor'] is None or game['home'] is None:
            return
        self.schedule.append(
            (game['date'], game['visitor'], game['home'])
        )

    def summary(self):
        return self.schedule


def read_zip_file(zip_file, fieldnames=None):
    """Retrosheet schedule and game log zip files contain a single file within
    them. Return a CSV reader for that file."""
    with zipfile.ZipFile(zip_file, 'r') as zip:
        first_file = zip.namelist()[0]
        with zip.open(first_file) as file_csv:
            file_contents = io.StringIO(file_csv.read().decode())
            if fieldnames:
                return csv.DictReader(file_contents, fieldnames)
            else:
                return csv.reader(file_contents)


def check_year(schedule_zip, gamelogs_zip):
    schedule_zip_file = os.path.basename(schedule_zip)
    gamelogs_zip_file = os.path.basename(gamelogs_zip)
    schedule_year = schedule_zip_file[:4]
    gamelogs_year = gamelogs_zip_file[2:6]

    if schedule_year != gamelogs_year:
        print("Year for the schedule ({}) does not match game logs year ({})".format(
            schedule_year, gamelogs_year), file=sys.stderr)
        sys.exit(1)
    return schedule_year

def main(argv):
    try:
        _argv0, schedule_zip, gamelogs_zip = argv
    except ValueError as exc:
        print(argv)
        print("Takes two arguments: schedule.zip and gamelogs.zip", file=sys.stderr)
        sys.exit(1)

    year = check_year(schedule_zip, gamelogs_zip)
    schedule = Schedule()
    schedule_fields = (
        'date', 'game_number', 'day', 'visitor', 'visitor_league',
        'visitor_game', 'home', 'home_league', 'home_game', 'game_time',
        'postponement', 'makeup_date'
    )
    for schedule_game in read_zip_file(schedule_zip, fieldnames=schedule_fields):
        schedule.add_game(schedule_game)

    season = Season()
    # There are 160 fields for each line of the game logs. That is far too many
    # fields that will end up unused.
    for game_log in read_zip_file(gamelogs_zip):
        season.add_game(game_log)

    teams = sorted([team.summary() for team in season.teams.values()],
                   key=lambda team: team['name'])
    summary = {
        'schedule': schedule.summary(),
        'teams': teams,
    }

    with open('mlb-{}.json'.format(year), 'w') as summary_json:
        summary_json.write(json.dumps(summary))


if __name__ == '__main__':
    main(sys.argv)
