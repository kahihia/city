;(function($, window, document, undefined) {
    'use strict';
    var google = window.google;

    function CreateVenuePage(){
        this.initVenueAutocomplete();
        this.initCKEditor();

        if(typeof(SuggestCityfusionVenue) !== "undefined") {
            this.suggestCityfusionVenue = new SuggestCityfusionVenue(this, this.onCityfusionVenueChoose.bind(this));
        }
    }

    CreateVenuePage.prototype = {
        initVenueAutocomplete: function(){
            var locationNameField = this.locationNameField = $('#id_city_0'),
                locationPointField = this.locationPointField = $('#id_city_1'),
                locationMap = this.locationMap = $('.location_map'),
                that = this, latlng;

            if (window.navigator.geolocation){
                window.navigator.geolocation.getCurrentPosition(function(position){
                    Cityfusion.userLocationLat = position.coords.latitude;
                    Cityfusion.userLocationLng = position.coords.longitude;
                });
            }

            $("#id_place").on("blur", function() {
                $(".pac-container").removeClass("show");
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
                $("#id_venue_name").val($("#id_geo_venue").val());
                $("#id_street").val($("#id_geo_street").val());
                $("#id_street_number").val($("#id_geo_street_number").val());
                $("#id_city_0").val($("#id_geo_city").val());

                Cityfusion.userLocationLat = result.geometry.location.lat();
                Cityfusion.userLocationLng = result.geometry.location.lng();

                that.setLocation(Cityfusion.userLocationLat, Cityfusion.userLocationLng);
            });

            this.initGoogleMap();
        },
        initGoogleMap: function(){
            var point, options, marker, map,
                that = this;
            
            point = new google.maps.LatLng(Cityfusion.userLocationLat|0, Cityfusion.userLocationLng|0);

            options = {
                zoom: 14,
                center: point,
                mapTypeId: google.maps.MapTypeId.ROADMAP
            };
            
            this.map = new google.maps.Map(document.getElementById("map_location"), options);

            this.marker = new google.maps.Marker({
                map: this.map,
                position: point,
                draggable: true
            });

            google.maps.event.addListener(this.marker, 'dragend', function(mouseEvent) {
                that.setLocationFromMap(mouseEvent.latLng);
            });
            
            google.maps.event.addListener(this.map, 'click', function(mouseEvent){
                that.marker.setPosition(mouseEvent.latLng);
                that.setLocationFromMap(mouseEvent.latLng);
            });

            $(".show-map").on("click", function(){
                $.fancybox($(".location_map"), {
                    autoSize: true,
                    closeBtn: true,
                    hideOnOverlayClick: false
                });

                google.maps.event.trigger(that.map, 'resize');

                window.setTimeout(function(){
                    that.setLocation(
                        +(document.getElementById("id_location_lat").value) || Cityfusion.userLocationLat,
                        +(document.getElementById("id_location_lng").value) || Cityfusion.userLocationLng
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

            Cityfusion.userLocationLng = lng;
            Cityfusion.userLocationLat = lat;
        },
        setLocation: function(lat, lng){
            if(lat&&lng){
                var point = new google.maps.LatLng(lat, lng);

                google.maps.event.trigger(this.map, 'resize');

                this.marker.setPosition(point);
                this.map.panTo(point);

                $("#id_location_lng").val(lng);
                $("#id_location_lat").val(lat);

                Cityfusion.userLocationLng = lng;
                Cityfusion.userLocationLat = lat;

            }
        },
        initCKEditor: function(){
            CKEDITOR.instances.id_about.on("instanceReady", function(){

                CKEDITOR.instances.id_about.on('paste', function(e){
                    e.data.html = e.data.dataValue.replace(/\s*width="[^"]*"/g, '');
                });
            });
        },
        onCityfusionVenueChoose: function(venue){
            setTimeout(function(){
                $("#id_place").val(venue.full_name);
            }, 10);

            $("#id_venue_identifier").val(venue.id);
            this.setLocation(parseFloat(venue.lat), parseFloat(venue.lng));

            $("#id_venue_name").val(venue.name);
            $("#id_street").val(venue.street);
            $("#id_city_0").val(venue.city_name);
            $("#id_city_1").val([venue.city_id, venue.lat, venue.lng].join(","));
            $("#id_city_identifier").val(venue.city_id);
        }
    };

    $(document).on("ready page:load", function(){
        window.createVenuePage = new CreateVenuePage();
    });

})(jQuery, window, document);    