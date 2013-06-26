;(function($, window, document, undefined) {
    'use strict';
    var google = window.google;

    function CreateVenuePage(){
        this.initVenueAutocomplete();

    }

    CreateVenuePage.prototype = {
        initVenueAutocomplete: function(){
            var locationNameField = this.locationNameField = $('#id_city_0'),
                locationPointField = this.locationPointField = $('#id_city_1'),
                locationMap = this.locationMap = $('.location_map'),
                that = this, latlng;

            if (window.navigator.geolocation){
                window.navigator.geolocation.getCurrentPosition(function(position){
                    window.user_lat = position.coords.latitude;
                    window.user_lng = position.coords.longitude;
                });
            }

            $("#id_place").on("blur", function() {
                $(".pac-container").removeClass("show");
                // window.setTimeout(that.setVenueText.bind(that), 10);
            });

            $("#id_place").on("focus", function() {
                $(this).val('');
                $(".pac-container").addClass("show");
            });


            $(locationNameField).on("autocompletechange", function(event, ui){
                if ($(locationPointField).val()) {
                    var point = $(locationPointField).val().split(','), identifier;
                    
                    $("#id_city_identifier").val(point[0]);
                    
                    latlng = new google.maps.LatLng(parseFloat(point[2]), parseFloat(point[1]));

                    that.setLocationFromMap(latlng);
                } else {
                    var lng = $("#id_location_lng").val(),
                        lat = $("#id_location_lat").val();

                    latlng = new google.maps.LatLng(parseFloat(lat), parseFloat(lng));
                    that.setLocationFromMap(latlng);
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

                window.user_lat = result.geometry.location.lat();
                window.user_lng = result.geometry.location.lng();

                that.setLocation(window.user_lat, window.user_lng);

                // window.setTimeout(that.setVenueText.bind(that));
            });

            this.initGoogleMap();
        },
        initGoogleMap: function(){
            var point, options, marker, map,
                that = this;
            
            point = new google.maps.LatLng(window.user_lat , window.user_lng);

            options = {
                zoom: 14,
                center: point,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            
            this.map = new google.maps.Map(document.getElementById("map_location"), options);

            this.marker = new google.maps.Marker({
                map: this.map,
                position: point,
                // draggable: true
            });

            // google.maps.event.addListener(this.marker, 'dragend', function(mouseEvent) {
            //     that.setLocationFromMap(mouseEvent.latLng);
            // });
            
            // google.maps.event.addListener(this.map, 'click', function(mouseEvent){
            //     that.marker.setPosition(mouseEvent.latLng);
            //     that.setLocationFromMap(mouseEvent.latLng);
            // });

            $(".show-map").on("click", function(){
                $.fancybox($(".location_map"), {
                    autoSize: true,
                    closeBtn: true,
                    hideOnOverlayClick: false
                });

                google.maps.event.trigger(that.map, 'resize');

                window.setTimeout(function(){
                    that.setLocation(
                        +(document.getElementById("id_location_lat").value) || window.user_lat,
                        +(document.getElementById("id_location_lng").value) || window.user_lng
                    );
                },100);

            });
        },
        setLocationFromMap: function(point){
            var lng = point.lng(),
                lat = point.lat();

            $("#id_location_lng").val(lng);
            $("#id_location_lat").val(lat);

            this.marker.setPosition(point);
            this.map.panTo(point);

            window.user_lng = lng;
            window.user_lat = lat;
        },
        setLocation: function(lat, lng){
            var point = new google.maps.LatLng(lat, lng);

            google.maps.event.trigger(this.map, 'resize');

            this.marker.setPosition(point);
            this.map.panTo(point);

            $("#id_location_lng").val(lng);
            $("#id_location_lat").val(lat);

            window.user_lng = lng;
            window.user_lat = lat;
        }
    };

    $(document).on("ready page:load", function(){
        window.createVenuePage = new CreateVenuePage();
    });

})(jQuery, window, document);    