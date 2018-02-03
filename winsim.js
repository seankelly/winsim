var Team = /** @class */ (function () {
    function Team() {
    }
    return Team;
}());
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
        var teams = document.createDocumentFragment();
        for (var _i = 0, _a = data.teams; _i < _a.length; _i++) {
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
