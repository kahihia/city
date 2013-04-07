;(function($, window, document, undefined) {

    'use strict';

    var SearchByLocation = function(){
        var that = this, request,
            currentSearchValue = $(".location-text-box input").val();
        this.searchList = $(".search-lists ul");
        this.searchInput = $(".location-text-box input");

        this.initVenueLinks();

        setInterval(function(){
            if(that.searchInput.val() !== currentSearchValue) {
                request && request.abort();
                currentSearchValue = that.searchInput.val();
                request = $.ajax({
                    url: "/events/nearest_venues?search=" + currentSearchValue,
                    success: function(data) {
                        window.ajaxPopup(data, 'success');
                        that.refreshVenueList(data);
                    }
                });
            }
        }, 500);
    };

    SearchByLocation.prototype = {
        initVenueLinks: function(){
            var that=this;
            $("li a", this.searchList).each(function(){
                $(this).on("click", function(){
                    that.findByVenue($(this).data("venue-id"));
                });
            });
        },
        findByVenue: function(id){
            window.location = window.filters.setFilter("venue", id).getURL();
        },

        refreshVenueList: function(data){
            $("li a", this.searchList).remove();

            _.forEach(data.venues, function(venue){
                var link, li;

                link = $("<a href='javascript:void;'>").html(venue[1] + ", " + venue[2]);
                link.attr("data-venue-id", venue[0]);

                li = $("<li>").append(link);

                this.searchList.append(li);
            }, this);

            this.initVenueLinks();
        }
        
    };

    window.SearchByLocation = SearchByLocation;

})(jQuery, window, document);