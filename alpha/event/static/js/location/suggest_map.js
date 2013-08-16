;(function($, window, document, undefined) {
    'use strict';
    var google = window.google;

    function SuggestMap(){
        this.initSuggestPopup();
        this.initGoogleMap();
    }

    SuggestMap.prototype = {
        initSuggestPopup: function(){
            var that = this;

            $(".show-map").on("click", function(){
                that.infowindow.close();
                $.fancybox($(".location_map"), {
                    autoSize: true,
                    closeBtn: true,
                    hideOnOverlayClick: false
                });

                google.maps.event.trigger(that.map, 'resize');

                window.setTimeout(function(){
                    that.setLocation(
                        +(document.getElementById("id_location_lat").value) || window.userLocationLat,
                        +(document.getElementById("id_location_lng").value) || window.userLocationLng
                    );
                },100);
            });

        },
        initGoogleMap: function(){
            var point, options, marker, map,
                that = this;
            
            point = new google.maps.LatLng(0, 0);

            this.infowindow = new google.maps.InfoWindow({
                content: "<div class='map-held'>Hi, I'm your Event's location!<br>Please move me along the map<br>to the exact location your<br>event is being held.</div>"
            });

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
            if(lat&&lng){
                var point = new google.maps.LatLng(lat, lng);

                google.maps.event.trigger(this.map, 'resize');

                this.marker.setPosition(point);
                this.map.panTo(point);

                $("#id_location_lng").val(lng);
                $("#id_location_lat").val(lat);

                window.userLocationLng = lng;
                window.userLocationLat = lat;
            }            
        }
    };

    window.SuggestMap = SuggestMap;
})(jQuery, window, document);