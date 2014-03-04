;(function($, window, document, undefined) {
    'use strict';
    var google = window.google;

    function CreateVenuePage(){
        this.initVenueAutocomplete();
        this.initCKEditor();

        if(typeof(SuggestCityfusionVenue) !== "undefined") {
            this.suggestCityfusionVenue = new SuggestCityfusionVenue(this, this.onCityfusionVenueChoose.bind(this));
        }

        this.watchTagsCount();
        this.initSocialLinks();
    }

    CreateVenuePage.prototype = {
        initVenueAutocomplete: function(){
            var locationNameField = this.locationNameField = $('#id_city_0'),
                locationPointField = this.locationPointField = $('#id_city_1'),
                locationMap = this.locationMap = $('.location_map'),
                that = this, latlng;

            $("#id_place").on("blur", function() {
                $(".pac-container").removeClass("show");
            });

            $("#id_place").on("focus", function() {
                $(".pac-container").addClass("show");
            });

            $(locationNameField).on("autocompletechange", function(event, ui){
                if ($(locationPointField).val()) {
                    var point = $(locationPointField).val().split(','), identifier;

                    $(this).parent().find("[name=city_identifier]").val(point[0]);
                    
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

                Cityfusion.userLocationLat = result.geometry.location.lat();
                Cityfusion.userLocationLng = result.geometry.location.lng();

                that.setLocation(Cityfusion.userLocationLat, Cityfusion.userLocationLng);
                $("#id_linking_venue_mode").val("GOOGLE");
            });

            $("#id_place").attr("data-autocomplete-binded", "1");

            this.initGoogleMap();
            this.venueAutocomplete = new window.VenueAutocomplete();

            if($("#id_location_lng").val() == 0 && $("#id_location_lat").val() == 0) {
                this.venueAutocomplete.suggestForm.initSuggestMapPosition();
            }
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

                window.userLocationLng = lng;
                window.userLocationLat = lat;
            }
        },
        initCKEditor: function(){
            if(typeof(CKEDITOR) !== "undefined") {
                CKEDITOR.instances.id_about.on("instanceReady", function(){
                    CKEDITOR.instances.id_about.on('paste', function(e){
                        e.data.html = e.data.dataValue.replace(/\s*width="[^"]*"/g, '');
                    });

                    CKEDITOR.instances.id_about.resize(340, 200);
                });
            }
        },
        onCityfusionVenueChoose: function(venue){
            setTimeout(function(){
                $("#id_place").val(venue.full_name);
            }, 10);

            $("#id_venue_identifier").val(venue.id);
            this.setLocation(parseFloat(venue.lat), parseFloat(venue.lng));

            $("#id_linking_venue_mode").val("EXIST");
        },
        watchTagsCount: function(){
            setInterval(this.calculateTagsCount.bind(this), 50);
        },
        calculateTagsCount: function(){
            if($("#as-values-id_tags__tagautosuggest").length === 0) {
                return;
            }

            var count = _.filter($("#as-values-id_tags__tagautosuggest").val().split(","), function(tag){ 
                return tag.trim(); 
            }).length;

            $(".tags-counter").text(count);

            if(count>10) {
                $(".tags-counter-container").addClass("overflow");
            } else {
                $(".tags-counter-container").removeClass("overflow");
            }
        },
        initSocialLinks: function(){
            this.socialLinksWidget = new SocialLinks();
        }
    };

    $(document).on("ready page:load", function(){
        window.createVenuePage = new CreateVenuePage();
    });

})(jQuery, window, document);