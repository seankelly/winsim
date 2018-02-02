class Team {
}

function init() {
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
            let teams = document.createDocumentFragment();
            for (let team of data.teams) {
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
                row.appendChild(win)
                row.appendChild(pythagenpat)
                row.appendChild(baseruns)
                teams.appendChild(row);
            }

            let teams_table = document.getElementById("teams") as HTMLTableElement;
            let teams_body = teams_table.tBodies[0];
            while (teams_body.firstChild) {
                teams_body.removeChild(teams_body.firstChild);
            }
            teams_body.appendChild(teams);
        });
}

function pick_season(ev) {
    let year = ev.target.value;
    if (!year) {
        return;
    }

    load_season(year);
}

init();
