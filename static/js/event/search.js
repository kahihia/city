;(function($, window, document, undefined) {

    'use strict';

    var SearchMenu = function(){
        this.searchByLocation = new window.SearchByLocation();
        this.fullTextSearch = new window.FullTextSearch();
    };

    SearchMenu.prototype = {
        
    };

    $(document).on("ready page:load", function(){
        window.eventPage = new SearchMenu();
    });

})(jQuery, window, document);