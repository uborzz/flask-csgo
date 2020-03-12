console.log("READ SELECTED_GAMES START", document.selected_games)

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
    m: "mvp",
    h: "HS",
    s: "S",
    kdr: "KD",
    kadr: "KAD",
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
    const options = { weekday: 'long', year: 'numeric', month: 'numeric', day: 'numeric' };
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
        determineColor(result) {
            var cls = {
                W: "bg-success",
                T: "bg-secondary",
                L: "bg-danger",
            }
            return cls[result]
        },
    },
    template: `
        <div class="card">
          <div class="card-heading">
            <div class="row text-center" :id="game._id">
                <div class="col-sm-2"><h1>{{game.map}}</h1></div>
                <div class="col-sm-3">
                </div>
                <div class="col-sm-2"  v-bind:class="determineColor(game.local_result)" ><h1>{{game.score_team1}} : {{game.score_team2}}</h1></div>
                <div class="col-sm-3"><p>{{date}}</p></div>
                <div class="col-sm-2"><p>Duration: {{game.duration}}</p></div>
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

// register the grid component
Vue.component('team', {
    template: `
      <table>
        <thead>
          <tr>
            <th v-for="key in columns"
              @click="sortBy(key)"
              :class="{ active: sortKey == key }">
              <% key | display %>
              <span class="arrow" :class="sortOrders[key] > 0 ? 'asc' : 'dsc'">
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="entry in filteredHeroes">
            <td v-for="key in columns">
              <%entry[key]%>
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
                    a = a[sortKey]
                    b = b[sortKey]
                    return (a === b ? 0 : a > b ? 1 : -1) * order
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
            console.log(this.games)

            var aggs_players = {}
            for (var id of this.players) {

            }

            for (var game of this.games) {
                console.log("GAME", game)
                var game_players = [...game.players_team1, ...game.players_team2];
                for (var player of game_players) {
                    console.log("chekin player", player)
                    var id = player.steam_id
                    console.log("player", id, player.nick)

                    // sums
                    if (this.players.includes(player.steam_id)) {
                        console.log("Found!", player)
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

                        console.log("actual aggs...", aggs_players)
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
            console.log("PRE FORMAT", totals)

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

            console.log("RESULT", totals)
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
            <team class="table table-striped"
                :heroes="heroes"
                :columns="gridColumns">
            </team>
        </div>
    `
});
new Vue({
    el: "#root",
    delimiters: ["<%", "%>"],
    data: {
        games: [],
        selected_players: [],
        all_players: [],
        showModal: false,
        showCharts: true,
        showMatches: false,
        showHelp: false,
        showLog: false,
        showIds: false,
    },
    methods: {
        update_games: function (e) {
            //            console.log("Detail Evento", e.detail.games)
            //            console.log("Detail Evento (Players)", e.detail.players)
            this.games = e.detail.games
            this.selected_players = e.detail.selected_players
        }
    },
    mounted() {
        document.addEventListener('changes', this.update_games);
        this.all_players = document.players;
        //        document.addEventListener('createtables', this.populate_datatables);
    },
})


