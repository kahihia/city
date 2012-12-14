(function ($) {
    var SearchLocation = function(location_name, location_point, map, choose_location_button){
        this.location_name = location_name;
        this.location_point = location_point;
        this.map = map;
        this.choose_location_button = choose_location_button;
        $(location_name).on("autocompletechange", function(event, ui){
            if ($(location_point).val()) {
                var point = $(location_point).val().split(',');
                console.log(point);
                lnglat = new google.maps.LatLng(parseFloat(point[1]), parseFloat(point[0]));
                savePosition_location(lnglat);
                marker_location.setPosition(lnglat);
                map_location.panTo(lnglat);
            } else {
                var lng = document.getElementById("id_location_lng"),
                    lat = document.getElementById("id_location_lat");
                $(map).show();
                google.maps.event.trigger(map_location, 'resize');
                map_location.panTo(new google.maps.LatLng(parseFloat(lat.value), parseFloat(lng.value)));
            }
        });

        function panMapToCenter(){
            var lng = document.getElementById("id_location_lng"),
                lat = document.getElementById("id_location_lat");
            $(map).toggle();
            google.maps.event.trigger(map_location, 'resize');
            map_location.panTo(new google.maps.LatLng(parseFloat(lat.value), parseFloat(lng.value)));
        }

        $(choose_location_button).on("click", panMapToCenter);
        $(document).mouseup(function (e){
            var container = $(map);

            if (container.has(e.target).length === 0 && container.is(':visible')){
                container.hide();
            }
        });
    }

    $(document).ready(function () {
        new SearchLocation('#id_location_name_0', '#id_location_name_1', '.location_map', '.choose_location');
    });
})(jQuery);