;(function($, window, document, undefined) {
    'use strict';

    var google = window.google;

    function SuggestForm(){
        this.initFormButtons();
        this.initSuggestMap();
        this.embedSuggestVenueButtonIntoGoogleAutocomplete();
        
        if(typeof(SuggestCityfusionVenue) !== "undefined") {
            this.suggestCityfusionVenue = new SuggestCityfusionVenue(this, this.onCityfusionVenueChoose.bind(this));
        }
    }

    SuggestForm.prototype = {
        initFormButtons: function(){
            var that = this;
            $(".suggest .reset-button").on("click", this.resetForm.bind(this));
            $(".suggest .cancel-button").on("click", this.cancelForm.bind(this));
            $(".suggest .submit-button").on("click", this.saveForm.bind(this));
        },
        resetForm: function(){
            $(".suggest .error").hide();
            $("#id_venue_name").val("");
            $("#id_street").val("");
            $("#id_city_0").val("");
        },
        cancelForm: function(){
            this.resetForm();
            $.fancybox.close();
        },
        saveForm: function(){
            var venue, street, city, suggest_values;
            venue = $("#id_venue_name").val();
            street = $("#id_street").val();
            city = $("#id_city_0").val();

            if(!venue || !city){
                $(".suggest .error").show();
                return;
            }

            suggest_values = [venue, street, city];
            $("#id_place").val(suggest_values.join(", "));
            $("#id_linking_venue_mode").val("SUGGEST");

            if($("#id_tags__tagautosuggest").length !== 0) {
                $("#id_tags__tagautosuggest")[0].tagspopup.loadTagsForCityByCity();
            }

            $.fancybox.close();
        },
        initSuggestMap: function(){
            this.suggestMap = new window.SuggestMap();
        },
        embedSuggestVenueButtonIntoGoogleAutocomplete: function(){
            var $pacContainer = $(".pac-container"),
                that = this;

            if($pacContainer.length === 0){
                setTimeout(function(){
                    that.embedSuggestVenueButtonIntoGoogleAutocomplete();
                },100);
            } else {
                var suggestNewVenueButton = $("<div>").addClass("new-venue").html("Not found? Suggest a new Venue!");

                $(".pac-container").prepend(suggestNewVenueButton);

                $(suggestNewVenueButton).on("mousedown", this.showSuggestPopup.bind(this));

                setInterval(function(){
                    $(".pac-container").addClass("suggest-new");
                }, 10);
            }
        },
        showSuggestPopup: function(){
            var that = this,
                map = this.suggestMap.map,
                marker = this.suggestMap.marker;

            $(".location-map-wrapper").append(
                $(".location_map").show()
            );

            $.fancybox($(".suggest"), {
                autoSize: true,
                closeBtn: true,
                hideOnOverlayClick: false,
                afterShow: function(){
                    google.maps.event.trigger(map, 'resize');
                    that.suggestMap.setLocation(window.userLocationLat, window.userLocationLng);
                    that.suggestMap.infowindow.open(map, marker);
                }
            });

            $("#id_venue_name").val($("#id_place").val());
        },
        onCityfusionVenueChoose: function(venue){
            setTimeout(function(){
                $("#id_place").val(venue.full_name);
            }, 10);

            $("#id_venue_identifier").val(venue.id);
            this.suggestMap.setLocation(parseFloat(venue.lat), parseFloat(venue.lng));

            if($("#id_tags__tagautosuggest").length !== 0) {
                $("#id_tags__tagautosuggest")[0].tagspopup.loadTagsForCityByVenue();
            }


            $("#id_linking_venue_mode").val("EXIST");
        }
    };

    window.SuggestForm = SuggestForm;

})(jQuery, window, document);