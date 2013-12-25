;(function($, window, document, undefined) {
    'use strict';

    function SuggestCityfusionVenue(suggestForm, onChoose){
        var that=this, request, currentSearchValue;
        this.searchInput = $("#id_place");
        this.searchUrl = "/events/suggest-cityfusion-venue/?search=";
        this.suggestForm = suggestForm;
        this.onChoose = onChoose;

        currentSearchValue = this.searchInput.val();

        setInterval(function(){
            if(that.searchInput.val() !== currentSearchValue) {
                if(request) request.abort();

                currentSearchValue = that.searchInput.val();
                request = $.ajax({
                    url: that.searchUrl + currentSearchValue,
                    success: function(data) {
                        that.updateDropdownList(data);
                    }
                });
            }
        }, 500);

        this.embedVenueDropdownIntoGoogleAutocomplete();        
    }

    SuggestCityfusionVenue.prototype = {
        embedVenueDropdownIntoGoogleAutocomplete: function(){
            var $pacContainer = $(".pac-container"),
                that = this;

            if($pacContainer.length === 0){
                setTimeout(function(){
                    that.embedVenueDropdownIntoGoogleAutocomplete();
                },100);
            } else {
                that.cityfusionVenuesWrapper = $("<div>").addClass("fusion-venues");

                $(".pac-container").append(that.cityfusionVenuesWrapper);
            }
        },
        updateDropdownList: function(data){
            var that=this;
            this.cityfusionVenuesWrapper.html("");
            _.each(data.venues, function(venue){
                var $item = $("<div class='pac-item cf-pac-item'>").html(venue.full_name);
                $item.attr("data-venue-id", venue.id);
                $item.attr("data-venue-lat", venue.lat);
                $item.attr("data-venue-lng", venue.lng);
                $item.attr("data-venue-full-name", venue.full_name);
                $item.attr("data-venue-name", venue.name);
                $item.attr("data-venue-street", venue.street);
                $item.attr("data-venue-city-id", venue.city_id);
                $item.attr("data-venue-city-name", venue.city_name);

                this.cityfusionVenuesWrapper.append($item);

                $item.on("mousedown", function(){
                    that.chooseVenue({
                        id: $(this).data("venue-id"),
                        full_name: $(this).html(),
                        lat: $(this).data("venue-lat"),
                        lng: $(this).data("venue-lng"),
                        name: $(this).data("venue-name"),
                        street: $(this).data("venue-street"),
                        city_id: $(this).data("venue-city-id"),
                        city_name: $(this).data("venue-city-name"),
                    })
                });
            }, this);
        },
        chooseVenue: function(venue){
            this.onChoose && this.onChoose(venue);
        }
    };

    window.SuggestCityfusionVenue = SuggestCityfusionVenue;
})(jQuery, window, document);