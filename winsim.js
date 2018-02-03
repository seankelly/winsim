var GameResult;
(function (GameResult) {
    GameResult[GameResult["Unplayed"] = 0] = "Unplayed";
    GameResult[GameResult["AwayWin"] = 1] = "AwayWin";
    GameResult[GameResult["HomeWin"] = 2] = "HomeWin";
})(GameResult || (GameResult = {}));
class Game {
    constructor(game_data) {
        this.date = game_data[0];
        this.away_team = game_data[1];
        this.home_team = game_data[2];
        this.reset();
    }
    reset() {
        this.sim_result = GameResult.Unplayed;
    }
}
class Season {
    constructor(teams, schedule) {
        this.createTeams(teams);
        this.schedule = new Schedule(schedule);
        this.reset();
    }
    createTeams(teams) {
        for (let team_data of teams) {
            let team = new Team(team_data);
            this.teams[team.name] = team;
        }
    }
    displayTeams() {
        let teams = document.createDocumentFragment();
        for (let team of this.teams.values()) {
            let row = document.createElement("tr");
            let name = document.createElement("td");
            name.innerText = team.name;
            let win = document.createElement("td");
            win.innerText = team.win_percentage.toPrecision(3);
            let pythagenpat = document.createElement("td");
            pythagenpat.innerText = team.pythagenpat_percentage.toPrecision(3);
            let baseruns = document.createElement("td");
            baseruns.innerText = team.baseruns_percentage.toPrecision(3);
            row.appendChild(name);
            row.appendChild(win);
            row.appendChild(pythagenpat);
            row.appendChild(baseruns);
            teams.appendChild(row);
        }
        let teams_table = document.getElementById("teams");
        let teams_body = teams_table.tBodies[0];
        while (teams_body.firstChild) {
            teams_body.removeChild(teams_body.firstChild);
        }
        teams_body.appendChild(teams);
    }
    displaySchedule() {
        let schedule_dom = document.createDocumentFragment();
        for (let game of this.schedule.game) {
            let row = document.createElement("tr");
            let date = document.createElement("td");
            date.innerText = game.date;
            let home = document.createElement("td");
            home.innerText = game.home_team;
            let away = document.createElement("td");
            away.innerText = game.away_team;
            row.appendChild(date);
            row.appendChild(home);
            row.appendChild(away);
            schedule_dom.appendChild(row);
        }
        let schedule_table = document.getElementById("schedule");
        let schedule_body = schedule_table.tBodies[0];
        while (schedule_body.firstChild) {
            schedule_body.removeChild(schedule_body.firstChild);
        }
        schedule_body.appendChild(schedule_dom);
    }
    findTeam(team_name) {
        return this.teams.get(team_name);
    }
    reset() {
        this.schedule.reset();
    }
}
class Schedule {
    constructor(schedule_data) {
        this.game = [];
        for (let game_data of schedule_data) {
            this.game.push(new Game(game_data));
        }
    }
    reset() {
        for (let game of this.game) {
            game.reset();
        }
    }
}
class Simulation {
    constructor() {
        let iterations_input = document.getElementById('number-simulations');
        this.iterations = parseFloat(iterations_input.value);
    }
    run() {
        console.log("Running " + this.iterations + " simulations.");
        for (let iteration = 0; iteration < this.iterations; iteration++) {
            season.reset();
        }
    }
}
class Team {
    constructor(team_data) {
        this.name = team_data.name;
        this.league = team_data.league;
        this.win_percentage = team_data.win_percentage;
        this.pythagenpat_percentage = team_data.pythagenpat_percentage;
        this.baseruns_percentage = team_data.baseruns_percentage;
        this.wins = team_data.wins;
        this.losses = team_data.losses;
    }
}
let season = null;
let simulation = null;
function init() {
    let start_button = document.getElementById("start-simulations");
    start_button.onclick = start_simulations;
    jQuery.getJSON('mlb.json')
        .done(function (data) {
        let season_select = document.getElementById('season-select');
        let seasons = document.createDocumentFragment();
        for (let year of data.years) {
            let option = document.createElement("option");
            option.value = year;
            option.innerText = year;
            seasons.appendChild(option);
        }
        season_select.appendChild(seasons);
        let select_text = season_select.children[0];
        select_text.disabled = true;
        season_select.onchange = pick_season;
    });
}
function load_season(year) {
    let season_file = 'mlb-' + year + '.json';
    jQuery.getJSON(season_file)
        .done(function (data) {
        season = new Season(data.teams, data.schedule);
        season.displayTeams();
        season.displaySchedule();
    });
}
function pick_season(ev) {
    let year = ev.target.value;
    if (!year) {
        return;
    }
    load_season(year);
}
function start_simulations(ev) {
    if (season === null) {
        console.log("No season loaded.");
        return;
    }
    simulation = new Simulation();
    simulation.run();
}
init();
