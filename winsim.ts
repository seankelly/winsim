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

function pick_season(ev) {
    let year = ev.target.value;
    if (!year) {
        return;
    }
}

init();
