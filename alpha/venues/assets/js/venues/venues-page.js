;(function($, window, document, undefined) {
    'use strict';

    var VenuesPage = function(){
        this.initFeaturedEventsViewer();
        this.initVenueTypeFilter();
    };

    VenuesPage.prototype = {
        initFeaturedEventsViewer: function(){
            this.featuredEventsViewer = new FeaturedEventsViewer();
        },
        initVenueTypeFilter: function(){
            new Dropdown($(".venue-type-dropdown")[0], {
                onChange: function(value, text){
                    if(value=="all") {
                        window.location = window.filters.removeFilter("venue_type").getURL();
                    } else {
                        window.location = window.filters.removeFilter("venue_type").setFilter("venue_type", value).getURL();
                    }
                }
            });
        }        
    };

    $(document).on("ready page:load", function(){
        window.venuesPage = new VenuesPage();
    });

})(jQuery, window, document);