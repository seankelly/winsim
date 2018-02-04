enum GameResult {
    Unplayed,
    AwayWin,
    HomeWin,
}

class Game {
    date: string;
    away_team: Team;
    home_team: Team;
    sim_result: GameResult;

    constructor(game_data: string[], season) {
        this.date = game_data[0];
        this.away_team = season.findTeam(game_data[1]);
        this.home_team = season.findTeam(game_data[2]);
        this.reset();
    }

    sim(): GameResult {
        // Use Log5 method to simulate the game. Include home field advantage
        // of 54% for MLB.

        let hfa = 0.54;

        let numerator = (this.away_team.win_percentage * (1 - this.home_team.win_percentage) * hfa);
        let away_win_probability = (
            numerator
            /
            (numerator + (1 - this.away_team.win_percentage) * this.home_team.win_percentage * (1 - hfa))
        );
        //console.log(this.date + ": " + this.away_team.name + " vs " + this.home_team.name + ": " + away_win_probability.toPrecision(3))

        if (Math.random() < away_win_probability) {
            this.sim_result = GameResult.AwayWin;
            this.away_team.sim_wins += 1;
            this.home_team.sim_losses += 1;
        }
        else {
            this.sim_result = GameResult.HomeWin;
            this.away_team.sim_losses += 1;
            this.home_team.sim_wins += 1;
        }
        return this.sim_result;
    }

    reset() {
        this.sim_result = GameResult.Unplayed;
    }
}

class Season {
    teams: Map<string, Team>;
    schedule: Schedule;

    constructor(teams, schedule) {
        this.createTeams(teams);
        this.schedule = new Schedule(schedule, this);
        this.reset();
    }

    createTeams(teams: any[]) {
        this.teams = new Map();
        for (let team_data of teams) {
            let team = new Team(team_data);
            this.teams.set(team.name, team);
        }
    }

    displayTeams() {
        let teams_table = [];
        for (let team of this.teams.values()) {
            teams_table.push([team.name, team.win_percentage.toPrecision(3),
                              team.pythagenpat_percentage.toPrecision(3),
                              team.baseruns_percentage.toPrecision(3)]);
        }

        createTable('teams', teams_table);
    }

    displaySchedule() {
        let games_table = [];
        for (let game of this.schedule.game) {
            games_table.push([game.date, game.home_team.name, game.away_team.name]);
        }

        createTable('schedule', games_table);
    }

    findTeam(team_name: string): Team {
        return this.teams.get(team_name);
    }

    sim(): Map<string, TeamSeason> {
        this.schedule.sim();

        let sim_results = new Map();
        for (let team of this.teams.values()) {
            sim_results.set(team.name, new TeamSeason(team.sim_wins, team.sim_losses));
        }
        return sim_results;
    }

    reset() {
        this.schedule.reset();
        for (let team of this.teams.values()) {
            team.reset();
        }
    }
}

class TeamSeason {
    wins: number;
    losses: number;

    constructor(wins, losses) {
        this.wins = wins;
        this.losses = losses;
    }
}

class Schedule {
    game: Game[];

    constructor(schedule_data: string[][], season: Season) {
        this.game = [];
        for (let game_data of schedule_data) {
            this.game.push(new Game(game_data, season));
        }
    }

    sim() {
        for (let game of this.game) {
            game.sim();
        }
    }

    reset() {
        for (let game of this.game) {
            game.reset();
        }
    }
}

class Simulation {
    iterations: number;

    constructor() {
        let iterations_input = document.getElementById('number-simulations') as HTMLInputElement;
        this.iterations = parseFloat(iterations_input.value);
    }

    run() {
        console.log("Running " + this.iterations + " simulations.");
        let seasons = [];
        for (let iteration = 0; iteration < this.iterations; iteration++) {
            let results = season.sim();
            seasons.push(results);
            season.reset();
        }
    }
}

class Team {
    name: string;
    league: string;
    win_percentage: number;
    pythagenpat_percentage: number;
    baseruns_percentage: number;
    wins: number;
    losses: number;
    sim_wins: number;
    sim_losses: number;

    constructor(team_data: any) {
        this.name = team_data.name;
        this.league = team_data.league;
        this.win_percentage = team_data.win_percentage;
        this.pythagenpat_percentage = team_data.pythagenpat_percentage;
        this.baseruns_percentage = team_data.baseruns_percentage;
        this.wins = team_data.wins;
        this.losses = team_data.losses;
        this.reset();
    }

    reset() {
        this.sim_wins = 0;
        this.sim_losses = 0;
    }
}

let season = null;
let simulation = null;

function createTable(element_id: string, rows: any[][]) {
    let table = document.getElementById(element_id) as HTMLTableElement;
    let body = table.tBodies[0];

    let new_body = document.createDocumentFragment();
    for (let row of rows) {
        let tr = document.createElement('tr');
        for (let col of row) {
            let td = document.createElement('td');
            td.innerText = col;
            tr.appendChild(td);
        }
        new_body.appendChild(tr);
    }

    clearChildren(body);
    body.appendChild(new_body);
}

function clearChildren(element: HTMLElement) {
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}

function init() {
    let start_button = document.getElementById("start-simulations");
    start_button.onclick = start_simulations;

    jQuery.getJSON('mlb.json')
        .done(function(data) {
            let season_select = document.getElementById('season-select');
            let seasons = document.createDocumentFragment();
            for (let year of data.years) {
                let option = document.createElement("option");
                option.value = year;
                option.innerText = year;
                seasons.appendChild(option);
            }
            season_select.appendChild(seasons);

            let select_text = season_select.children[0] as HTMLOptionElement;
            select_text.disabled = true;
            season_select.onchange = pick_season;
        });
}

function load_season(year) {
    let season_file = 'mlb-' + year + '.json';
    jQuery.getJSON(season_file)
        .done(function(data) {
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
