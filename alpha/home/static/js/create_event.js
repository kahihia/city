(function ($) {
    var SearchLocation = function(location_name, location_point, map){
        this.location_name = location_name;
        this.location_point = location_point;
        this.map = map;        
        $(location_name).on("autocompletechange", function(event, ui){
            if ($(location_point).val()) {
                var point = $(location_point).val().split(','), identifier;
                
                $("#id_city_identifier").val(point[0]);
                
                lnglat = new google.maps.LatLng(parseFloat(point[2]), parseFloat(point[1]));
                savePosition_location(lnglat);
                marker_location.setPosition(lnglat);
                map_location.panTo(lnglat);
            } else {
                var lng = document.getElementById("id_location_lng"),
                    lat = document.getElementById("id_location_lat");                
                google.maps.event.trigger(map_location, 'resize');
                map_location.panTo(new google.maps.LatLng(parseFloat(lat.value), parseFloat(lng.value)));
            }
        });

        function panMapToCenter(){
            var lng = document.getElementById("id_location_lng"),
                lat = document.getElementById("id_location_lat");            
            google.maps.event.trigger(map_location, 'resize');
            map_location.panTo(new google.maps.LatLng(parseFloat(lat.value), parseFloat(lng.value)));
        }
    }

    $(document).ready(function () {
        new SearchLocation('#id_city_0', '#id_city_1', '.location_map', '.choose_location');
    });
})(jQuery);