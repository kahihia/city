;(function($, window, document, undefined) {
    'use strict';

    var VenuesPage = function(){
        this.initFeaturedEventsViewer();        
    };

    VenuesPage.prototype = {
        initFeaturedEventsViewer: function(){
            this.featuredEventsViewer = new FeaturedEventsViewer();
        }
    };

    $(document).on("ready page:load", function(){
        window.venuesPage = new VenuesPage();
    });

})(jQuery, window, document);