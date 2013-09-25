;(function($, window, document, undefined) {
    'use strict';

    var _ = window._,
        Cityfusion = window.Cityfusion;

    var SearchByLocation = function(){
        var that = this, request,
            currentSearchValue = $(".location-text-box input").val();
        this.searchList = $(".search-lists ul");
        this.searchInput = $(".location-text-box input");

        this.searchUrl = "/events/locations?search=";

        this.initLocationLinks();

        setInterval(function(){
            if(that.searchInput.val() !== currentSearchValue) {
                if(request) request.abort();

                currentSearchValue = that.searchInput.val();
                request = $.ajax({
                    url: that.searchUrl + currentSearchValue,
                    success: function(data) {
                        that.refreshLocationList(data);
                    }
                });
            }
        }, 500);

        request = $.ajax({
            url: that.searchUrl + currentSearchValue,
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
        findByLocation: function(id, type, text){
            window.location = window.filters.setFilter("location", type+"|"+id).getURL();
        },

        refreshLocationList: function(data){
            $("li a", this.searchList).remove();

            _.forEach(data.locations, function(location) {
                this.searchList.append(this.appendLink(location));
            }, this);

            this.initLocationLinks();
        },

        appendLink: function(data) {
            var link, li;

            link = $("<a href='javascript:void(0);'></a>").html(data.name);
            link.attr("data-location-id", data.id);
            link.attr("data-location-type", data.type);

            li = $("<li />").append(link);
            return li;
        }
    };

    window.SearchByLocation = SearchByLocation;

})(jQuery, window, document);