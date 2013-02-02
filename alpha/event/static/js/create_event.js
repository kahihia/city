(function ($) {
    var SearchLocation = function(location_name, location_point, map){
        this.location_name = location_name;
        this.location_point = location_point;
        this.map = map;        
        $(location_name).on("autocompletechange", function(event, ui){
            if ($(location_point).val()) {
                var point = $(location_point).val().split(','), identifier;
                
                $("#id_city_identifier").val(point[0]);

                user_lat = parseFloat(point[2]);
                user_lng = parseFloat(point[1]);
                
                lnglat = new google.maps.LatLng(parseFloat(point[2]), parseFloat(point[1]));
                savePosition_location(lnglat);
                marker_location.setPosition(lnglat);
                map_location.panTo(lnglat);
            } else {
                var lng = document.getElementById("id_location_lng"),
                    lat = document.getElementById("id_location_lat");

                user_lat = lat;
                user_lng = lng;
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
        var keyStop = {            
            13: "input, textarea", // stop enter = submit 

            end: null
        };
        $(document).bind("keydown", function(event){
            var selector = keyStop[event.which];

            if(selector !== undefined && $(event.target).is(selector)) {
                event.preventDefault(); //stop event
            }
            return true;
        });
        
        setTimeout(function(){
            new SearchLocation('#id_city_0', '#id_city_1', '.location_map', '.choose_location');

            $.balloon.defaults.classname = "hintbox";
            $.balloon.defaults.css = {};
            var ballons = $(".balloon");
            $(ballons).each(function(){
                var content = $(this).siblings(".balloon-content");
                $(this).balloon({                 
                    contents:content,
                    position:"right bottom",
                    tipSize: 0,
                    offsetX:25,                    
                    showDuration: 500, hideDuration: 0,
                    showAnimation: function(d) { this.fadeIn(d); }
                });
            });
            
        },100);        
    });
})(jQuery);