;(function($, window, document, undefined) {

    'use strict';

    var SearchBar = function(){
        this.searchInput = $("<input type='text' class='search-input'>");
        // $(".searchTags").append(this.searchInput);        
    };

    SearchBar.prototype = {
        
    };

    window.SearchBar = SearchBar;


})(jQuery, window, document);