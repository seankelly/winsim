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
            // TODO: Clear body.
            let body = document.createElement("tbody");
            teams.appendChild(body);
            for (let team of data.teams) {
                let row = document.createElement("tr");
                let name = document.createElement("td");
                name.innerText = team.name;
                let win = document.createElement("td");
                win.innerText = team.win_percentage;
                let pythagenpat = document.createElement("td");
                pythagenpat.innerText = team.pythagenpat_percentage;
                let baseruns = document.createElement("td");
                baseruns.innerText = team.baseruns_percentage;

                row.appendChild(name);
                row.appendChild(win)
                row.appendChild(pythagenpat)
                row.appendChild(baseruns)
                body.appendChild(row);
            }
            teams.appendChild(body);
            document.getElementById("teams").appendChild(teams);
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
