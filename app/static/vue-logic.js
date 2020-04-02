// console.log("READ SELECTED_GAMES START", document.selected_games)

// matches
const grid_columns = [
    "nick",
    "k",
    "a",
    "d",
    "m",
    "h",
    "s",
    "kdr",
    "kadr",
]

const display_columns = {
    nick: "nick",
    k: "K",
    a: "A",
    d: "D",
    m: "MVP",
    h: "HS",
    s: "S",
    kdr: "KD",
    kadr: "KAD",
}
const help_team_columns = {
    nick: "Player name",
    k: "Kills",
    a: "Assists",
    d: "Deaths",
    m: "MVPs (Most Valuable Player)",
    mvp: "MVPs (Most Valuable Player)",
    h: "Headshot Percentage",
    hs: "Headshot Percentage",
    s: "Score",
    kdr: "Kill/Death Ratio",
    kadr: "Kill+Assit/Death Ratio",
    wr: "Win Rate (Wins / Total)",
    wlr: "Win Rate (Wins / Wins+Loses - Ignoring Ties)",
}

// stats from filtered
const stats_columns = [
    "nick",
    "games",
    "wins",
    "ties",
    "loses",
    "k",
    "a",
    "d",
    "kdr",
    "kadr",
    "mvp",
    "hs",
    "score",
    "wr",
    "wlr",
]
const stats_display_columns = {
    games: "P",
    wins: "W",
    ties: "T",
    loses: "L",
}


function gameIdToDate(id) {
    const date = new Date(id);
    const options = { weekday: 'long', year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric' };
    return date.toLocaleDateString('en-GB', options)
}

Vue.component('game', {
    props: ['game'],
    data() {
        return {
            counter: 0,
            idteam1: this.game._id + "T1",
            idteam2: this.game._id + "T2",
            team1: this.game.players_team1,
            team2: this.game.players_team2,
            id: this.game._id,
            date: gameIdToDate(this.game._id),
            gridColumns: grid_columns,
        }
    },
    methods: {
        determineCardColor(result) {
            var cls = {
                W: "card-win",
                T: "card-tie",
                L: "card-lose",
            }
            return cls[result]
        },
        determineColor(result) {
            var cls = {
                W: "soft-win",
                T: "soft-tie",
                L: "soft-lose",
            }
            return cls[result]
        },
    },
    filters: {
        pretty(time_string) {
            let time = time_string.split(':')
            let result = Number(time[0]) ? Number(time[0])*60 : 0
            result = result + Number(time[1]) + ' mins'
            return result
        }
    },
    template: `
        <div class="card" v-bind:class="determineCardColor(game.local_result)">
          <div class="card-heading">
            <div class="row text-center" :id="game._id">
            <div class="col-sm-5"><p>{{date}}</p></div>
            <div class="col-sm-2 score" v-bind:class="determineColor(game.local_result)" ><h1>{{game.score_team1}} : {{game.score_team2}}</h1></div>
            <div class="col-sm-3"><h1>{{game.map}}</h1></div>
            <div class="col-sm-2"><p>{{game.duration | pretty}}</p></div>
                
            </div>
          </div>
          <div class="card-body">
            <div class="row">
                <div class="col-sm-6">
                    <team class="table table-striped"
                        :heroes="team1"
                        :columns="gridColumns"
                        :id="game._id+'T1'">
                    </team>
                </div>
                <div class="col-sm-6">
                    <team class="table table-striped"
                        :heroes="team2"
                        :columns="gridColumns"
                        :id="game._id+'T2'">
                    </team>
                </div>
            </div>
        </div>
    </div>
    `

});


// table th con arrow icon.
//<th v-for="key in columns"
//    @click="sortBy(key)"
//    :class="{ active: sortKey == key }">
//    <% key | display %>
//    <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'">
//    </span>
//</th>

// register the grid component
Vue.component('team', {
    template: `
      <table class="fit">
        <thead>
          <tr>
            <th v-for="key in columns"
              @click="sortBy(key)"
              v-bind:title = "key | descriptions"
              :class="{ active: sortKey == key }">
              <% key | display %>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in filteredHeroes" v-bind:title = "'Full name: ' + entry.nick">
            <td v-for="key in columns">
              <% entry[key] | slice %>
            </td>
          </tr>
        </tbody>
      </table>
  `,
    props: {
        heroes: Array,
        columns: Array,
    },
    delimiters: ["<%", "%>"],
    data: function () {
        var sortOrders = {}
        this.columns.forEach(function (key) {
            sortOrders[key] = 1
        })
        return {
            sortKey: '',
            sortOrders: sortOrders
        }
    },
    computed: {
        filteredHeroes: function () {
            var sortKey = this.sortKey
            var order = this.sortOrders[sortKey] || 1
            var heroes = this.heroes
            if (sortKey) {
                heroes = heroes.slice().sort(function (a, b) {
                    let a_  = parseFloat(a[sortKey])
                    let b_ = parseFloat(b[sortKey])
                    return (a_ == b_ ? 0 : a_ > b_ ? 1 : -1) * order
                })
            }
            return heroes
        }
    },
    filters: {
        capitalize: function (str) {
            return str.charAt(0).toUpperCase() + str.slice(1)
        },
        display: function (str) {
            if (str in display_columns) {
                return display_columns[str]
            } else {
                return this.capitalize(str)
            }
        },
        descriptions: function (str) {
            if (str in help_team_columns) {
                return help_team_columns[str]
            } else {
                return this.capitalize(str)
            }
        },
        slice: function(value) {
            if (typeof(value) == "string") {
                if (value.length >= 15) {
                    return value.slice(0,12) + '...'
                } else {
                    return value
                }
            } else {
                return value
            }
        },
    },
    methods: {
        sortBy: function (key) {
            this.sortKey = key
            this.sortOrders[key] = this.sortOrders[key] * -1
        }
    }
})

Vue.component('stats', {
    props: ['games', 'players'],
    data() {
        return {
            gridColumns: stats_columns,
        }
    },
    computed: {
        heroes: function () {
            // console.log(this.games)

            var aggs_players = {}
            for (var id of this.players) {

            }

            for (var game of this.games) {
                // console.log("GAME", game)
                var game_players = [...game.players_team1, ...game.players_team2];
                for (var player of game_players) {
                    // console.log("chekin player", player)
                    var id = player.steam_id
                    // console.log("player", id, player.nick)

                    // sums
                    if (this.players.includes(player.steam_id)) {
                        // console.log("Found!", player)
                        if (!(id in aggs_players)) {
                            aggs_players[id] = {
                                nick: player.nick,
                                games: 0,
                                wins: 0,
                                loses: 0,
                                ties: 0,
                            }
                        }
                        aggs_players[id].k = aggs_players[id].k + player.k || player.k
                        aggs_players[id].a = aggs_players[id].a + player.a || player.a
                        aggs_players[id].d = aggs_players[id].d + player.d || player.d
                        aggs_players[id].mvp = aggs_players[id].mvp + player.m || player.m
                        aggs_players[id].hs = aggs_players[id].hs + parseFloat(player.h) || parseFloat(player.h)
                        aggs_players[id].score = aggs_players[id].score + player.s || player.s

                        ++aggs_players[id].games
                        game.local_result == "W" && ++aggs_players[id].wins
                        game.local_result == "L" && ++aggs_players[id].loses
                        game.local_result == "T" && ++aggs_players[id].ties

                        // console.log("actual aggs...", aggs_players)
                    }
                }
            }

            // means and ratios
            var totals = Object.keys(aggs_players).map((key) => aggs_players[key])
            for (var player of totals) {
                // means
                player.k = player.k / player.games
                player.a = player.a / player.games
                player.d = player.d / player.games
                player.mvp = player.mvp / player.games
                player.hs = player.hs / player.games
                player.score = player.score / player.games

                // global ratios
                player.kdr = player.k / player.d
                player.kadr = (player.k + player.a) / player.d
                player.wr = player.wins / player.games
                player.wlr = player.wins / (player.wins + player.loses)
            }
            // console.log("PRE FORMAT", totals)

            // format
            for (var player of totals) {
                player.k = Number(player.k).toFixed(2)
                player.a = Number(player.a).toFixed(2)
                player.d = Number(player.d).toFixed(2)
                player.mvp = Number(player.mvp).toFixed(2)
                player.hs = Number(player.hs * 100).toFixed(1)
                player.score = Number(player.score).toFixed(2)
                player.kdr = Number(player.kdr).toFixed(2)
                player.kadr = Number(player.kadr).toFixed(2)
                player.wr = Number(player.wr * 100).toFixed(1)
                player.wlr = Number(player.wlr * 100).toFixed(1)
            }

            // console.log("RESULT", totals)
            return totals
        }
    },
    filters: {
        capitalize: function (str) {
            return str.charAt(0).toUpperCase() + str.slice(1)
        },
        display: function (str) {
            if (str in stats_display_columns) {
                return stats_display_columns[str]
            } else {
                return this.capitalize(str)
            }
        },
    },
    template: `
        <div>
            <team class="table table-striped fit"
                :heroes="heroes"
                :columns="gridColumns">
            </team>
        </div>
    `
});


Vue.component('history', {
    props: ['games'],
    data() {
        var columns = ["Map", "Datetime", "Duration", "Score", "Result"]
        return {
            // date: gameIdToDate(this.game._id),
            cols: columns,
        }
    },
    filters: {
        capitalize: function (str) {
            return str.charAt(0).toUpperCase() + str.slice(1)
        },
    },
    methods: {
        idToDate: function(id) {
            const date = new Date(id);
            const options = { year: 'numeric', month: 'numeric', day: 'numeric', hour: 'numeric', minute: 'numeric' };
            return date.toLocaleDateString('en-GB', options)
        },
        sortBy: function (key) {
            this.sortKey = key
            this.sortOrders[key] = this.sortOrders[key] * -1
        },
        determineColor(result) {
            var cls = {
                W: "card-win",
                T: "card-tie",
                L: "card-lose",
            }
            return cls[result]
        },
        showGame: function(game) {
            vm.individual_game = game
            vm.showGame = true
        }
    },
    computed: {
        sorted_games: function () {
            var games = this.games.sort(function (a, b) {
                return (a._id == b._id ? 0 : a._id > b._id ? 1 : -1) * -1
            })
            return games
        }
    },
    // delimiters: ["<%", "%>"],
    template: `
      <table class="table">
        <thead>
          <tr>
            <th v-for="key in cols">
                {{ key }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr :class="determineColor(game.local_result)" @click="showGame(game)" v-for="game in sorted_games">
            <td>{{ game.map }}</td>
            <td>{{ idToDate(game._id) }}</td>
            <td>{{ game.duration }}</td>
            <td>{{ game.score_team1 }} : {{ game.score_team2 }}</td>
            <td>{{ game.local_result }}</td>
          </tr>
        </tbody>
      </table>
    `,
});

//<th>Map</th>
//<th>Date</th>
//<th>Time</th>
//<th>Duration</th>
//<th>Score</th>
//<th>Result</th>

var vm = new Vue({
    el: "#root",
    delimiters: ["<%", "%>"],
    data: {
        games: [],
        individual_game: null,
        selected_players: [],
        all_players: [],
        showModal: false,  // matches
        showCharts: true,
        showHelp: false,
        showLog: false,
        showIds: false,
        showGame: false,
    },
    methods: {
        update_games: function (e) {
            //            console.log("Detail Evento", e.detail.games)
            //            console.log("Detail Evento (Players)", e.detail.players)
            this.games = e.detail.games
            this.selected_players = e.detail.selected_players
        },
        update_mode: function (e) {
            this.set_mode(e.control)
        },
        set_mode: function(mode) {
            // let current_mode = this.get_mode()
            // if (current_mode != mode) {
            //     save_config()
            //     window.location.href = generate_url_with_config()
            // }
            if (mode == "matches") {
                this.showCharts = false
                this.showHelp = false
                this.showModal = true
            } else if (mode =="help") {
                this.showModal = false
                this.showCharts = false
                this.showHelp = true
            } else {  // mode charts
                this.showCharts = true
                this.showModal = false
                this.showHelp = false
            }
        },
        close_stuff() {
            // console.log("PARERRADO")
            this.showLog = false
            this.showIds = false
            this.showGame = false
        },
        get_mode: function() {
            if (this.showModal == true) {
                return "matches" 
            } else if (this.showHelp == true) {
                return "help"
            } else {
                return "charts"
            }
        }
    },
    mounted() {
        document.addEventListener('changes', this.update_games);
        // document.addEventListener('mode', this.update_mode);
        this.all_players = document.players;
        //        document.addEventListener('createtables', this.populate_datatables);
    },
})


