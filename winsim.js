var Game = /** @class */ (function () {
    function Game(game_data) {
        this.date = game_data[0];
        this.away_team = game_data[1];
        this.home_team = game_data[2];
    }
    return Game;
}());
var Season = /** @class */ (function () {
    function Season(teams, schedule) {
        this.teams = this.createTeams(teams);
        this.schedule = new Schedule(schedule);
    }
    Season.prototype.createTeams = function (teams) {
        var _teams = [];
        for (var _i = 0, teams_1 = teams; _i < teams_1.length; _i++) {
            var team_data = teams_1[_i];
            var team = new Team(team_data);
            _teams.push(team);
        }
        return _teams;
    };
    Season.prototype.displayTeams = function () {
        var teams = document.createDocumentFragment();
        for (var _i = 0, _a = this.teams; _i < _a.length; _i++) {
            var team = _a[_i];
            var row = document.createElement("tr");
            var name_1 = document.createElement("td");
            name_1.innerText = team.name;
            var win = document.createElement("td");
            win.innerText = team.win_percentage.toPrecision(3);
            var pythagenpat = document.createElement("td");
            pythagenpat.innerText = team.pythagenpat_percentage.toPrecision(3);
            var baseruns = document.createElement("td");
            baseruns.innerText = team.baseruns_percentage.toPrecision(3);
            row.appendChild(name_1);
            row.appendChild(win);
            row.appendChild(pythagenpat);
            row.appendChild(baseruns);
            teams.appendChild(row);
        }
        var teams_table = document.getElementById("teams");
        var teams_body = teams_table.tBodies[0];
        while (teams_body.firstChild) {
            teams_body.removeChild(teams_body.firstChild);
        }
        teams_body.appendChild(teams);
    };
    Season.prototype.displaySchedule = function () {
        var schedule_dom = document.createDocumentFragment();
        for (var _i = 0, _a = this.schedule.game; _i < _a.length; _i++) {
            var game = _a[_i];
            var row = document.createElement("tr");
            var date = document.createElement("td");
            date.innerText = game.date;
            var home = document.createElement("td");
            home.innerText = game.home_team;
            var away = document.createElement("td");
            away.innerText = game.away_team;
            row.appendChild(date);
            row.appendChild(home);
            row.appendChild(away);
            schedule_dom.appendChild(row);
        }
        var schedule_table = document.getElementById("schedule");
        var schedule_body = schedule_table.tBodies[0];
        while (schedule_body.firstChild) {
            schedule_body.removeChild(schedule_body.firstChild);
        }
        schedule_body.appendChild(schedule_dom);
    };
    return Season;
}());
var Schedule = /** @class */ (function () {
    function Schedule(schedule_data) {
        this.game = [];
        for (var _i = 0, schedule_data_1 = schedule_data; _i < schedule_data_1.length; _i++) {
            var game_data = schedule_data_1[_i];
            this.game.push(new Game(game_data));
        }
    }
    return Schedule;
}());
var Team = /** @class */ (function () {
    function Team(team_data) {
        this.name = team_data.name;
        this.league = team_data.league;
        this.win_percentage = team_data.win_percentage;
        this.pythagenpat_percentage = team_data.pythagenpat_percentage;
        this.baseruns_percentage = team_data.baseruns_percentage;
        this.wins = team_data.wins;
        this.losses = team_data.losses;
    }
    return Team;
}());
var season = null;
function init() {
    jQuery.getJSON('mlb.json')
        .done(function (data) {
        var season_select = document.getElementById('season-select');
        var seasons = document.createDocumentFragment();
        for (var _i = 0, _a = data.years; _i < _a.length; _i++) {
            var year = _a[_i];
            var option = document.createElement("option");
            option.value = year;
            option.innerText = year;
            seasons.appendChild(option);
        }
        season_select.appendChild(seasons);
        var select_text = season_select.children[0];
        select_text.disabled = true;
        season_select.onchange = pick_season;
    });
}
function load_season(year) {
    var season_file = 'mlb-' + year + '.json';
    jQuery.getJSON(season_file)
        .done(function (data) {
        season = new Season(data.teams, data.schedule);
        season.displayTeams();
        season.displaySchedule();
    });
}
function pick_season(ev) {
    var year = ev.target.value;
    if (!year) {
        return;
    }
    load_season(year);
}
init();
