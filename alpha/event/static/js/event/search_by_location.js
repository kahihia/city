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

        if(Cityfusion.isCanada){
            this.setupTrip();
        }
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

            link = $("<a href='javascript:void(0);'>").html(data.name);
            link.attr("data-location-id", data.id);
            link.attr("data-location-type", data.type);

            li = $("<li>").append(link);
            return li;
        },
        setupTrip: function(){
            var that=this;
            this.updateTrip();           

            if (navigator.geolocation){
                navigator.geolocation.getCurrentPosition(function(position){
                    $.ajax("/events/set-browser-location", {
                        type: "GET",
                        dataType: "json",
                        data: { 
                            latitude: position.coords.latitude, 
                            longitude: position.coords.longitude 
                        }
                    }).done(function(data){
                        Cityfusion.userLocationCityId = data.city_id;
                        Cityfusion.userLocationCityName = data.city_name;
                        Cityfusion.userLocationRegionId = data.region_id;
                        Cityfusion.userLocationRegionName = data.region_name;
                        that.updateTrip();
                    });
                });
            }

            $(".location-text-box .location").on("click", function(){
                that.trip && that.trip.start();
            });

            $(".location-text-box .location").on("keypress blur", function(){
                that.trip.stop();
            });
        },
        updateTrip: function(){
            var that=this;
            if(Cityfusion.userLocationCityId || Cityfusion.userLocationRegionId){
                var content =  'Please, choose your current location (city or region). <br/>Suggestions: <span class="suggest-city" data-suggest-city-id="'+Cityfusion.userLocationCityId+'">'+Cityfusion.userLocationCityName+'</span>';

                if(Cityfusion.userLocationRegionId) {
                    content += ', <span class="suggest-region" data-suggest-region-id="'+Cityfusion.userLocationRegionId+'">'+Cityfusion.userLocationRegionName+'</span>';
                }

                this.trip = new Trip([
                    { 
                        sel: $('.location'),
                        content: content,
                        delay: -1
                    }
                ]);
            }


            $("body").on("click", ".suggest-city", function(){
                var link=this;
                that.trip.stop();
                window.location = window.filters.setFilter("location", "city|"+$(link).data("suggest-city-id")).getURL();
            });

            $("body").on("click", ".suggest-region", function(){
                var link=this;
                that.trip.stop();
                window.location = window.filters.setFilter("location", "region|"+$(link).data("suggest-region-id")).getURL();
            });           
        }
    };

    window.SearchByLocation = SearchByLocation;

})(jQuery, window, document);