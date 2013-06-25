;(function($, window, document, undefined) {
    'use strict';

    var _ = window._;

    var SearchByLocation = function(){
        var that = this, request,
            currentSearchValue = $(".location-text-box input").val();
        this.searchList = $(".search-lists ul");
        this.searchInput = $(".location-text-box input");

        this.initLocationLinks();

        setInterval(function(){
            if(that.searchInput.val() !== currentSearchValue) {
                if(request) request.abort();

                currentSearchValue = that.searchInput.val();
                request = $.ajax({
                    url: "/events/locations?search=" + currentSearchValue,
                    success: function(data) {
                        that.refreshLocationList(data);
                    }
                });
            }
        }, 500);

        request = $.ajax({
            url: "/events/locations?search=" + currentSearchValue,
            success: function(data) {
                that.refreshLocationList(data);
            }
        });
    };

    SearchByLocation.prototype = {
        initLocationLinks: function(){
            var that=this;
            $("li a", this.searchList).each(function(){
                $(this).on("click", function(){
                    that.findByLocation(
                        $(this).data("location-id"),
                        $(this).data("location-type")
                    );
                });
            });
        },
        findByLocation: function(id, type){
            window.location = window.filters.setFilter("location", type+"|"+id).getURL();
        },

        refreshLocationList: function(data){
            $("li a", this.searchList).remove();

            _.forEach(data.locations, function(location){
                var link, li;

                link = $("<a href='javascript:void;'>").html(location.name);
                link.attr("data-location-id", location.id);
                link.attr("data-location-type", location.type);

                li = $("<li>").append(link);

                this.searchList.append(li);
            }, this);

            this.initLocationLinks();
        }
        
    };

    window.SearchByLocation = SearchByLocation;

})(jQuery, window, document);