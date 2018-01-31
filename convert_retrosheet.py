#!/usr/bin/env python3

import csv
import io
import json
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


class Team():
    def __init__(self, name):
        self.wins = 0
        self.losses = 0
        self.runs_scored = 0
        self.runs_allowed = 0
        self.baseruns_offense = BaseRuns()
        self.baseruns_defense = BaseRuns()

    def scored(self, runs):
        self.runs_scored += runs

    def allowed(self, runs):
        self.runs_allowed += runs

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

    def add_baseruns_defense(self, defense):
        self._add_baseruns('baseruns_defense', defense)


class Game():
    # Useful offsets for each game log row.
    VISITOR_TEAM = 3
    VISITOR_LEAGUE = 4
    HOME_TEAM = 6
    HOME_LEAGUE = 7
    VISITOR_SCORE = 9
    HOME_SCORE = 10

    VISITOR_OFFENSE = (21, 38)
    VISITOR_PITCHING = (38, 43)
    HOME_OFFENSE = (49, 66)
    HOME_PITCHING = (66, 70)

    def __init__(self, game):
        self.visitor = game[self.VISITOR_TEAM]
        self.visitor_league = game[self.VISITOR_LEAGUE]
        self.home = game[self.HOME_TEAM]
        self.home_league = game[self.HOME_LEAGUE]
        self.visitor_score = int(game[self.VISITOR_SCORE])
        self.home_score = int(game[self.HOME_SCORE])
        self.visitor_offense = self.intify(game[self.VISITOR_OFFENSE[0]:self.VISITOR_OFFENSE[1]])
        self.visitor_pitching = self.intify(game[self.VISITOR_PITCHING[0]:self.VISITOR_PITCHING[1]])
        self.home_offense = self.intify(game[self.HOME_OFFENSE[0]:self.HOME_OFFENSE[1]])
        self.home_pitching = self.intify(game[self.HOME_PITCHING[0]:self.HOME_PITCHING[1]])

    @staticmethod
    def intify(fields):
        return [int(field) for field in fields]

    def winner(self):
        if self.visitor_score > self.home_score:
            return 'visitor'
        elif self.home_score < self.visitor_score:
            return 'home'
        return 'tie'


class Season():
    def __init__(self):
        self.teams = {}

    def add_game(self, game):
        game = Game(game)

        visitor = game.visitor
        if visitor not in self.teams:
            visitor = self.teams[visitor] = Team(visitor)
        else:
            visitor = self.teams[visitor]

        home = game.home
        if home not in self.teams:
            home = self.teams[home] = Team(home)
        else:
            home = self.teams[home]

        visitor.scored(game.visitor_score)
        visitor.allowed(game.home_score)
        home.scored(game.home_score)
        home.allowed(game.visitor_score)

        visitor.add_baseruns_offense(game.visitor_offense)
        visitor.add_baseruns_defense(game.home_offense)
        home.add_baseruns_offense(game.home_offense)
        home.add_baseruns_defense(game.visitor_offense)


class Schedule():
    def __init__(self):
        self.schedule = []

    def add_game(self, game):
        self.schedule.append(
            (game['date'], game['visitor'], game['home'])
        )

    def to_json(self):
        json.dumps(self.schedule)


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


def main(argv):
    try:
        _argv0, schedule_zip, gamelogs_zip = argv
    except ValueError as exc:
        print(argv)
        print("Takes two arguments: schedule.zip and gamelogs.zip", file=sys.stderr)
        sys.exit(1)

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


if __name__ == '__main__':
    main(sys.argv)
