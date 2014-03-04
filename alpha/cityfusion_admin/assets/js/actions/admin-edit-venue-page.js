;(function($, window, document, undefined) {
    'use strict';

    var AdminVenueEditPage = function() {
        var self = this;

        self.init = function() {
            setTimeout(function(){
                self.initMap();
            }, 200);
        };

        self.initMap = function() {
            self.map = window.createVenuePage.venueAutocomplete.suggestForm.suggestMap.map;
            self.marker = window.createVenuePage.venueAutocomplete.suggestForm.suggestMap.marker;

            var initLng = $("[data-id=init_lng]").data("value"),
                initLat = $("[data-id=init_lat]").data("value");

            if(initLng && initLat) {
                    var point = new google.maps.LatLng(initLat, initLng);

                    google.maps.event.trigger(self.map, 'resize');

                    self.marker.setPosition(point);
                    self.map.panTo(point);

                    $("#id_location_lng").val(initLng);
                    $("#id_location_lat").val(initLat);

                    window.userLocationLng = initLng;
                    window.userLocationLat = initLat;
            }
        };

        self.init();
    };

    $(document).ready(function() {
        new AdminVenueEditPage();
    });
})(jQuery, window, document);