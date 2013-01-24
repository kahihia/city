(function($) {
    $(document).ready(function() {

        $("[data-switch-to='suggest-tr']").on("click", function(){
            $(".location-tr").hide();
            $(".suggest-tr").show();
        });

        $("[data-switch-to='location-tr']").on("click", function(){            
            $(".suggest-tr").hide();
            $("#id_venue_name").val("");
            $("#id_street").val("");
            $("#id_city_0").val("");
            $(".location-tr").show();
        });

        function panMapToCenter(lat, lng) {
            var point = new google.maps.LatLng(lat, lng);
            google.maps.event.trigger(map_location, 'resize');
            marker_location.setPosition(point);
            map_location.panTo(point);
            $("#id_location_lng").val(lng);
            $("#id_location_lat").val(lat);
        }

        setTimeout(function(){
            panMapToCenter(user_lat, user_lng);
        },1000);
    });
})(jQuery);