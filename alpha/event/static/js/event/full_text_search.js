;(function($, window, document, undefined) {

    'use strict';

    var FullTextSearch = function(){
        this.searchInput = $("input.search");
        this.searchButton = $(".search-submission");
        this.searchButton.on("click", this.search.bind(this));
    };

    FullTextSearch.prototype = {
        search: function(){
            window.location = window.filters.setFilter("search", this.searchInput.val()).getURL();
        }
    };

    window.FullTextSearch = FullTextSearch;

})(jQuery, window, document);