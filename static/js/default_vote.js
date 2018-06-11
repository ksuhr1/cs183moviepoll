// This is the js for the default/index.html view.

var app = function() {

    var self = {};
    Vue.config.silent = false; // show all warnings

    // Extends an array
    self.extend = function(a, b) {
        for (var i = 0; i < b.length; i++) {
            a.push(b[i]);
        }
    };
    

    //Vote polls
    self.vote_poll = function(movieId) {
        console.log("Movie Id", movieId);
        $.post(vote_poll_url,

            {
                movie_id: movieId,
                vote: self.vue.vote,
            },
            function (data) {
             self.vue.vote = data.vote;
            }
        )
    };

    self.vote = function (movieId) {
        var movie = self.vue.poll.movies.find( movie => movie.id === movieId);
        var inCart = self.vue.cart.indexOf(movie);
        console.log("cart",inCart);
        //add to the cart
        if (inCart === -1) {
            self.vue.cart.push(movie);
        //take out of cart
        } else {
            self.vue.cart.splice(inCart, 1);
        }
        console.log(self.vue.cart);
    };




    // ##############################################################
    // Get polls
    function get_polls_url(start_idx, end_idx) {
        var pp = {
            start_idx: start_idx,
            end_idx: end_idx
        };
        return polls_url + "?" + $.param(pp);
    }

    self.get_polls = function () {
        var poll_len = self.vue.polls.length;
        $.getJSON(get_polls_url(poll_len, poll_len+4), function (data) {
            self.vue.polls = data.polls;
            self.vue.has_more = data.has_more;
            self.vue.logged_in = data.logged_in;
        })
    };


    // $('.movie-results').on('click', function(event) {
    //  alert('You clicked the Bootstrap Card');
    // });


    // ##############################################################
    // Get single poll based on poll id
    self.get_poll = function (pollId) {
        $.getJSON(poll_url,
            {
                poll_id: pollId,
            },
            function (data) {
                console.log("here is your poll: ");
                console.log(data);
                self.vue.poll = data.poll;
                self.vue.logged_in = data.logged_in;
            }
        )
    };


    self.vue = new Vue({
        el: "#vue-div",
        delimiters: ['${', '}'],
        unsafeDelimiters: ['!{', '}'],
        data: {
            movies: [],
            showtimes:[],
            cinemas:[],

            poll: {},
            polls: [],
            cart: [],
            vote: 0,
        },
        methods: {
            get_polls: self.get_polls,
            get_poll: self.get_poll,
            vote_poll: self.vote_poll,
            vote: self.vote,
        }


    });

    // self.get_polls();
    self.get_poll(poll_id);
    $("#vue-div").show();
    return self;
};

var APP = null;

// This will make everything accessible from the js console;
// for instance, self.x above would be accessible as APP.x
jQuery(function(){APP = app();});




