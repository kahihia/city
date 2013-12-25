;(function($, window, document, undefined) {

    'use strict';

    var FullTextSearch = function(){
        var that = this;
        this.searchInput = $("input.search");
        this.searchButton = $(".search-submission");
        this.searchButton.on("click", this.search.bind(this));
        this.searchInput.keyup(function(event){
            if(event.keyCode == 13){
                that.search();
            }
        });
    };

    FullTextSearch.prototype = {
        search: function(){
            window.location = window.filters.removeFilter("page").setFilter("search", this.searchInput.val()).getURL("/events/");
        }
    };

    window.FullTextSearch = FullTextSearch;

})(jQuery, window, document);