#!/usr/bin/env python3

import argparse
import csv
import io
import json
import logging
import os
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

    def json_summary(self):
        pythag_win_perc, _ = self.pythagenpat_percentage()
        baseruns_win_perc, _, __, ___ = self.baseruns_percentage()
        return {
            'name': self.name,
            'league': self.league.name,
            'win_percentage': self.win_percentage(),
            'pythagenpat_percentage': pythag_win_perc,
            'baseruns_percentage': baseruns_win_perc,
            'wins': self.wins,
            'losses': self.losses,
            'games': self.games,
        }

    def csv_summary(self):
        pythag_win_perc, pythag_exponent = self.pythagenpat_percentage()
        baseruns_win_perc, _, __, ___ = self.baseruns_percentage()
        summary = ([self.name, self.league.name, self.wins, self.losses,
                    self.games, self.win_percentage()]
                   + list(self.pythagenpat_percentage())
                   + list(self.baseruns_percentage())
                  )

        def to_precision(field):
            if isinstance(field, float):
                return '{:.3}'.format(field)
            return field
        summary = [to_precision(field) for field in summary]
        return summary

    def win_percentage(self):
        return self.wins / self.games

    def pythagenpat_percentage(self):
        return self.calculate_pythagenpat(self.runs_scored, self.runs_allowed, self.games)

    def baseruns_percentage(self):
        runs_scored = self.baseruns_scored()
        runs_allowed = self.baseruns_allowed()
        #print(self.name, "RS/G", runs_scored / self.games, "RA/G", runs_allowed / self.games)
        baseruns_win_perc, exponent = self.calculate_pythagenpat(
            runs_scored, runs_allowed, self.games)
        runs_scored_game = runs_scored / self.games
        runs_allowed_game = runs_allowed / self.games
        return baseruns_win_perc, exponent, runs_scored_game, runs_allowed_game

    @staticmethod
    def calculate_pythagenpat(runs_scored, runs_allowed, games):
        exponent = ((runs_scored + runs_allowed) / games) ** 0.287
        win_perc = 1 / (1 + (runs_allowed / runs_scored) ** exponent)
        return win_perc, exponent

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

    def json_summary(self):
        return self.schedule


def options():
    parser = argparse.ArgumentParser(
        description="Process Retrosheet schedule and gamelog files.")
    parser.add_argument('--format', '-f', choices=('json', 'csv'),
                        help="Output format.")
    parser.add_argument('--verbose', '-v', action='count',
                        help="Increase output verbosity.")
    parser.add_argument('years', nargs='+', help="The years to process.")
    args = parser.parse_args()
    return args


def collect_files(year):
    files = os.listdir()
    # Try to find the schedule file.
    schedule_file = None
    for check_file in ('%sSKED.ZIP', '%sSKED.TXT'):
        file_name = check_file % year
        if os.path.exists(file_name):
            schedule_file = file_name
            break

    # Now try to find the game log file.
    gamelog_file = None
    for check_file in ('gl%s.zip', 'GL%s.TXT'):
        file_name = check_file % year
        if os.path.exists(file_name):
            gamelog_file = file_name
            break

    if schedule_file and gamelog_file:
        return schedule_file, gamelog_file

def open_maybe_zip(file_path, fieldnames=None):
    """Check if a file is a zip file and open it using zipfile."""
    if file_path.endswith('.zip') or file_path.endswith('.ZIP'):
        with zipfile.ZipFile(file_path, 'r') as zip:
            first_file = zip.namelist()[0]
            with zip.open(first_file) as file_csv:
                file_contents = io.StringIO(file_csv.read().decode())
    else:
        with open(file_path, 'r') as fd:
            file_contents = fd.read().decode()
    if fieldnames:
        return csv.DictReader(file_contents, fieldnames)
    else:
        return csv.reader(file_contents)


def main(argv):
    args = options()
    log_level = logging.WARNING
    if args.verbose is None:
        pass
    elif args.verbose >= 2:
        log_level = logging.DEBUG
    elif args.verbose >= 1:
        log_level = logging.INFO

    logging.basicConfig(stream=sys.stdout, level=log_level,
                        format='%(asctime)s %(levelname)s - %(message)s')

    if args.format == 'json':
        logging.debug("In JSON output mode.")
    elif args.format == 'csv':
        logging.debug("In CSV output mode.")
        fields = ('year', 'name', 'league', 'wins', 'losses', 'games',
                  'win_percentage', 'pythagenpat_percentage', 'pythagenpat_exponent',
                  'baseruns_percentage', 'baseruns_exponent',
                  'baseruns_runs_scored', 'baseruns_runs_allowed')
        mlb_history = open('mlb-history.csv', 'w')
        csv_mlb = csv.writer(mlb_history)
        csv_mlb.writerow(fields)

    for year in args.years:
        logging.debug("Processing year %s", year)
        retrosheet_files = collect_files(year)
        if not retrosheet_files:
            logging.warn("Could not find any files for year %s", year)
            continue
        schedule_file, gamelog_file = retrosheet_files
        schedule = Schedule()
        schedule_fields = (
            'date', 'game_number', 'day', 'visitor', 'visitor_league',
            'visitor_game', 'home', 'home_league', 'home_game', 'game_time',
            'postponement', 'makeup_date'
        )
        for schedule_game in open_maybe_zip(schedule_file, fieldnames=schedule_fields):
            schedule.add_game(schedule_game)

        season = Season()
        # There are 160 fields for each line of the game logs. That is far too many
        # fields that will end up unused.
        for game_log in open_maybe_zip(gamelog_file):
            season.add_game(game_log)

        if args.format == 'json':
            teams = sorted([team.json_summary() for team in season.teams.values()],
                           key=lambda team: team['name'])
            summary = {
                'schedule': schedule.json_summary(),
                'teams': teams,
            }
            with open('mlb-{}.json'.format(year), 'w') as summary_json:
                summary_json.write(json.dumps(summary))
        elif args.format == 'csv':
            rows = sorted([[year] + team.csv_summary()
                           for team in season.teams.values()],
                          key=lambda team: team[1])
            csv_mlb.writerows(rows)


if __name__ == '__main__':
    main(sys.argv)
