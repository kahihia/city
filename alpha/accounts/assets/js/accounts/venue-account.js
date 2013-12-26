;(function($, window, document, undefined) {
    'use strict';
    var venue_account_id = window.venue_account_id,
        google = window.google,
        venue_account_latitude = window.venue_account_latitude,
        venue_account_longtitude = window.venue_account_longtitude;

    function VenueAccountPage(){        
        var that = this;
        $("#venue_account_make_public").on("click", function(){
            $.ajax({
                url: "/venues/set-venue-privacy/" + venue_account_id + "/public",
                success: function(data) {
                    window.ajaxPopup(data, 'success');
                }
            });
        });

        $("#venue_account_make_private").on("click", function(){
            $.ajax({
                url: "/venues/set-venue-privacy/" + venue_account_id + "/private",
                success: function(data) {
                    window.ajaxPopup(data, 'success');
                }
            });
        });

        $(".show-on-map").on("click", function(){
            that.showMap();
        });

        this.initEventActions();
    }

    VenueAccountPage.prototype = {
        showMap: function(){
            var point = new google.maps.LatLng(venue_account_latitude, venue_account_longtitude),
                options = {
                    zoom: 14,
                    center: point,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                },
                venue_account_map = new google.maps.Map(document.getElementById("venue_account_map"), options),
                marker = new google.maps.Marker({
                    map: venue_account_map,
                    position: point,
                    draggable: false
                });

            $.fancybox(document.getElementById("venue_account_map"), {
                autoSize: true,
                closeBtn: true,
                hideOnOverlayClick: false
            });

            google.maps.event.trigger(venue_account_map, 'resize');
            venue_account_map.panTo(point);
        },
        initEventActions: function(){
            this.eventActions = new window.EventActions($(".entry-info"));
        }
    };

    $(document).on("ready page:load", function(){
        window.venueAccountPage = new VenueAccountPage();
    });

})(jQuery, window, document);
