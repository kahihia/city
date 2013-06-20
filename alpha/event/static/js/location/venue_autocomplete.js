;(function($, window, document, undefined) {
    'use strict';
    var google = window.google;

    function VenueAutocomplete(){
        var that = this,
            location_name_input = $('#id_city_0'),
            location_point_input = $('#id_city_1'),
            map_container = $('.location_map');

        if (window.navigator.geolocation){
            window.navigator.geolocation.getCurrentPosition(function(position){
                window.user_lat = position.coords.latitude;
                window.user_lng = position.coords.longitude;
            });
        }

        this.initSuggestForm();
        this.initGeocomplete(location_name_input, location_point_input, map_container);

        $("#id_place").on("blur", function() {
            $(".pac-container").removeClass("show");
            // window.setTimeout(that.setVenueText.bind(that), 10);
        });

        $("#id_place").on("focus", function() {
            $(".pac-container").addClass("show");
        });
    }

    VenueAutocomplete.prototype = {
        initSuggestForm: function(){
            this.suggestForm = new window.SuggestForm();
        },
        initGeocomplete: function(location_name_input, location_point_input, map_container){
            var latlng,
                that = this;
            $(location_name_input).on("autocompletechange", function(event, ui){
                if ($(location_point_input).val()) {
                    var point = $(location_point_input).val().split(','), identifier;
                    
                    $("#id_city_identifier").val(point[0]);
                    
                    latlng = new google.maps.LatLng(parseFloat(point[2]), parseFloat(point[1]));

                    that.suggestForm.suggestMap.setLocationFromMap(latlng);
                } else {
                    var lng = $("#id_location_lng").val(),
                        lat = $("#id_location_lat").val();

                    latlng = new google.maps.LatLng(parseFloat(lat), parseFloat(lng));
                    that.suggestForm.suggestMap.setLocationFromMap(latlng);
                }
            });

            $("#id_place").geocomplete({
                details: ".geo-details",
                detailsAttribute: "data-geo",
                types: ['geocode', 'establishment'],
                componentRestrictions: {
                    country: 'ca'
                }
            }).bind("geocode:result", function(event, result) {
                $("#id_venue_name").val("");
                $("#id_street").val("");
                $("#id_city_0").val("");
                $("#id_tags__tagautosuggest")[0].tagspopup.forCity($("#id_geo_city").val());

                window.user_lat = result.geometry.location.lat();
                window.user_lng = result.geometry.location.lng();

                that.suggestForm.suggestMap.setLocation(window.user_lat, window.user_lng);

                window.setTimeout(that.setVenueText.bind(that));
            });
        },
        setVenueText: function(){
            var address = $("#id_geo_address").val(),
                venue = $("#id_geo_venue").val();
            if(address.indexOf(venue)===-1){
                $("#id_place").val(
                    $("#id_geo_venue").val()+", "+$("#id_geo_address").val()
                );
            }
        }
    };

    window.VenueAutocomplete = VenueAutocomplete;

})(jQuery, window, document);