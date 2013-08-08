;(function($, window, document, undefined) {
    'use strict';

    function SuggestCityfusionVenue(suggestForm){
        var that=this, request, currentSearchValue;
        this.searchInput = $("#id_place");
        this.searchUrl = "/events/suggest-cityfusion-venue/?search=";
        this.suggestForm = suggestForm;

        currentSearchValue = this.searchInput.val();

        setInterval(function(){
            if(that.searchInput.val() !== currentSearchValue) {
                $("#id_venue_identifier").val("");
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
                var $item = $("<div class='pac-item cf-pac-item'>").html(venue.name);
                $item.attr("data-venue-id", venue.id);
                $item.attr("data-venue-lat", venue.lat);
                $item.attr("data-venue-lng", venue.lng);
                this.cityfusionVenuesWrapper.append($item);

                $item.on("mousedown", function(){
                    that.chooseVenueId({
                        id: $(this).data("venue-id"),
                        name: $(this).html(),
                        lat: $(this).data("venue-lat"),
                        lng: $(this).data("venue-lng")
                    })
                });
            }, this);
        },
        chooseVenueId: function(venue){
            setTimeout(function(){
                $("#id_place").val(venue.name);
            }, 10);

            $("#id_venue_identifier").val(venue.id);
            
            this.suggestForm.suggestMap.setLocation(parseFloat(venue.lat), parseFloat(venue.lng));
        }
    };

    window.SuggestCityfusionVenue = SuggestCityfusionVenue;
})(jQuery, window, document);