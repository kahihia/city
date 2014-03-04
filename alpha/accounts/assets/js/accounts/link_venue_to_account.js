;(function($, window, document, undefined) {
    'use strict';
    var google = window.google;

    function LinkVenueToAccount(){
        this.newVenuePopup = $(".new-venue-popup");
        this.newVenueButton = $(".new-venue-button");

        this.newVenueButton.on("click", this.showNewVenuePopup.bind(this));

        this.initSwitchBetweenAutocompleteAndSuggest();

        this.initAutocomplete();
        this.initSuggestion();

        $(".reset-button", this.newVenuePopup).on("click", this.resetForm.bind(this));
        $(".cancel-button", this.newVenuePopup).on("click", this.cancelForm.bind(this));
        $(".submit-button", this.newVenuePopup).on("click", this.saveForm.bind(this));

        this.currentMode = "AUTOCOMPLETE";
    }

    LinkVenueToAccount.prototype = {
        showNewVenuePopup: function(){
            var that = this;
            $.fancybox(this.newVenuePopup , {
                autoSize: true,
                closeBtn: true,
                hideOnOverlayClick: false,
                afterShow: function(){
                    if(that.map) that.setLocation(window.userLocationLat, window.userLocationLng);
                }
            });

            
        },
        switchToAutocomplete: function(){
            $(".venue-autocomplete", this.newVenuePopup).addClass("active");
            $(".venue-suggest", this.newVenuePopup).removeClass("active");
            $.fancybox.update();
            this.currentMode = "AUTOCOMPLETE";
        },
        switchToSuggestion: function(){
            $(".venue-autocomplete", this.newVenuePopup).removeClass("active");
            $(".venue-suggest", this.newVenuePopup).addClass("active");
            $.fancybox.update();
            this.currentMode = "SUGGEST";
        },
        initSwitchBetweenAutocompleteAndSuggest: function(){
            this.switchToAutocompleteButton = $(".switch-to-autocomplete", this.newVenuePopup);
            this.switchToSuggestionButton = $(".switch-to-suggestion", this.newVenuePopup);

            this.switchToAutocompleteButton.on("click", this.switchToAutocomplete.bind(this));
            this.switchToSuggestionButton.on("click", this.switchToSuggestion.bind(this));
        },
        initAutocomplete: function(){
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

                window.userLocationLat = result.geometry.location.lat();
                window.userLocationLng = result.geometry.location.lng();

                that.setLocation(window.userLocationLat, window.userLocationLng);
            });

            this.initGoogleMap();

        },
        initGoogleMap: function(){
            var point, options, marker, map,
                that = this;
            
            point = new google.maps.LatLng(window.userLocationLat , window.userLocationLng);

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
        },
        setLocationFromMap: function(point){
            var lng = point.lng(),
                lat = point.lat();

            $("#id_location_lng").val(lng);
            $("#id_location_lat").val(lat);

            this.marker.setPosition(point);
            this.map.panTo(point);

            window.userLocationLng = lng;
            window.userLocationLat = lat;
        },
        setLocation: function(lat, lng){
            var point = new google.maps.LatLng(lat, lng);

            google.maps.event.trigger(this.map, 'resize');

            this.marker.setPosition(point);
            this.map.panTo(point);

            $("#id_location_lng").val(lng);
            $("#id_location_lat").val(lat);

            window.userLocationLng = lng;
            window.userLocationLat = lat;

        },
        initSuggestion: function(){

        },
        resetForm: function(){
            $(".error", this.newVenuePopup).hide();
            $("#id_venue_name").val("");
            $("#id_street").val("");
            $("#id_city_0").val("");
        },
        cancelForm: function(){
            this.resetForm();
            $.fancybox.close();
        },
        saveForm: function(){

            switch(this.currentMode){
                case "AUTOCOMPLETE":
                    this.saveIfAutocompleteIsUsed();
                break;
                case "SUGGEST":
                    this.saveIfSuggestIsUsed();
                break;
            }

            $.fancybox.close();
            // TODO: add ajax call to link account
        },
        saveIfAutocompleteIsUsed: function(){

        },
        saveIfSuggestIsUsed: function(){
            var venue, street, city, suggest_values;
            venue = $("#id_venue_name").val();
            street = $("#id_street").val();
            city = $("#id_city_0").val();

            if(!venue || !street || !city){
                $(".error", this.newVenuePopup).show();
                return;
            }

            $.ajax({
                url: "/account-actions/",
                success: function(data) {
                    window.ajaxPopup(data, 'success');
                }
            });

        }

    };

    window.LinkVenueToAccount = LinkVenueToAccount;

})(jQuery, window, document);