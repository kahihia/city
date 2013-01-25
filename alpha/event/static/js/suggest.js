(function($) {
    $(document).ready(function() {
        setTimeout(function(){

            function panMapToCenter(lat, lng) {
                var point = new google.maps.LatLng(lat, lng);
                google.maps.event.trigger(map_location, 'resize');
                marker_location.setPosition(point);
                map_location.panTo(point);
                $("#id_location_lng").val(lng);
                $("#id_location_lat").val(lat);
            }

            $(".suggest .reset-button").on("click", function(){                
                $(".suggest .error").hide();
                $("#id_venue_name").val("");
                $("#id_street").val("");
                $("#id_city_0").val("");                                
            });
            $(".suggest .cancel-button").on("click", function(){
                $(".suggest .error").hide();
                $("#id_venue_name").val("");
                $("#id_street").val("");
                $("#id_city_0").val("");
                $.fancybox.close();
            });

            $(".suggest .submit-button").on("click", function(){
                var venue, street, city;
                venue = $("#id_venue_name").val();
                street = $("#id_street").val();
                city = $("#id_city_0").val();
                if(!venue || !street || !city){
                    $(".suggest .error").show();
                    return;
                }
                var suggest_values = [venue, street, city];
                $("#id_place").val(suggest_values.join(", "));
                $.fancybox.close();
            });

            $(".choose_location").on("click", function(){
                $(".location-map-wrapper").append($(".location_map").show());
                $.fancybox($(".suggest"), {
                        autoSize: true,
                        closeBtn: true,
                        hideOnOverlayClick: false
                    });                
                google.maps.event.trigger(map_location, 'resize');

                setTimeout(function(){
                    panMapToCenter(user_lat, user_lng);
                },100);
                
            });

            $(".show_map").on("click", function(){
                $.fancybox($(".location_map"), {
                        autoSize: true,
                        closeBtn: true,
                        hideOnOverlayClick: false
                    });
                google.maps.event.trigger(map_location, 'resize');
                setTimeout(function(){
                    panMapToCenter(user_lat, user_lng);
                },100);
            });

            setTimeout(function(){
                $("#id_location_lng").on("change", function(){
                    user_lng = +($(this).val());
                });
                $("#id_location_lat").on("change", function(){
                    user_lat = +($(this).val());
                });            
            },1000);  
        },100);        
        
    });
})(jQuery);