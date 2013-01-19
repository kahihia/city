(function($) {
    $(document).ready(function() {

        function panMapToCenter(lat, lng) {
            var point = new google.maps.LatLng(lat, lng);
            google.maps.event.trigger(map_location, 'resize');
            marker_location.setPosition(point);
            map_location.panTo(point);
            $("#id_location_lng").val(lng);
            $("#id_location_lat").val(lat);
        }

        $(".suggest .close-button").on("click", function(){
            var venue, street, city;
            $(".suggest .error").hide();
            venue = $("#id_venue_name").val();
            street = $("#id_street").val();
            city = $("#id_city_0").val();
            if(!venue || !street || !city){
                $(".suggest .error").show();
                return;
            }
            var suggest_values = [venue, street, city];
            $("#id_place").val(suggest_values.join(", "))
            $(".suggest").hide();
            $(".modal-bg").hide();
        });
        $(".suggest .reset-button").on("click", function(){
            $(".suggest .error").hide();
            $("#id_venue_name").val("");
            $("#id_street").val("");
            $("#id_city_0").val("");
            $(".suggest").hide();
            $(".modal-bg").hide();
        });

        $(".choose_location").on("click", function(){
            $(".suggest").show();
            $(".modal-bg").show();
            google.maps.event.trigger(map_location, 'resize');
            if(user_lat && user_lng) {
                panMapToCenter(user_lat, user_lng);
            }
        });
        
    });
})(jQuery);