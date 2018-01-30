#!/usr/bin/env python3

import csv
import io
import json
import sys
import zipfile


class Team():
    def __init__(self, name):
        self.wins = 0
        self.losses = 0
        self.runs_scored = 0
        self.runs_allowed = 0


class Game():
    def __init__(self, date, home, away):
        pass


class Schedule():
    def __init__(self):
        self.schedule = []

    def add_game(self, game):
        self.schedule.append(
            (game['date'], game['visitor'], game['home'])
        )

    def to_json(self):
        json.dumps(self.schedule)


def read_zip_file(zip_file, **csv_kwargs):
    """Retrosheet schedule and game log zip files contain a single file within
    them. Return a CSV reader for that file."""
    with zipfile.ZipFile(zip_file, 'r') as zip:
        first_file = zip.namelist()[0]
        with zip.open(first_file) as file_csv:
            file_contents = io.StringIO(file_csv.read().decode())
            return csv.DictReader(file_contents, **csv_kwargs)


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


if __name__ == '__main__':
    main(sys.argv)