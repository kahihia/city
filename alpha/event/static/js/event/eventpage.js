;(function($, window, document, undefined) {
    'use strict';

    var EventPage = function(){
        this.initEventActions();
        $("a#photoFancy").fancybox({
            'hideOnContentClick': true
        });

        this.showMap();
    };

    EventPage.prototype = {
        initEventActions: function(){
            this.eventActions = new window.EventActions($(".event-details"));
        },
        showMap: function(){
            var point = new google.maps.LatLng(window.venue_latitude, window.venue_longtitude),
                options = {
                    zoom: 14,
                    center: point,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                },
                venue_account_map = new google.maps.Map(document.getElementById("venue_map"), options),
                marker = new google.maps.Marker({
                    map: venue_account_map,
                    position: point,
                    draggable: false
                });
        }
    };

    $(document).on("ready page:load", function(){
        window.eventPage = new EventPage();
    });

})(jQuery, window, document);