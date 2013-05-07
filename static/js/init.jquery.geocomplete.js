(function($) {
    $(document).ready(function() {
        setTimeout(function(){
            var map = $('.location_map');

            function panMapToCenter(lat, lng) {
                var point = new google.maps.LatLng(lat, lng);
                google.maps.event.trigger(map_location, 'resize');
                marker_location.setPosition(point);
                map_location.panTo(point);
                $("#id_location_lng").val(lng);
                $("#id_location_lat").val(lat);
            }
    
            //$("#id_place").val("");
            $("#id_place").geocomplete({
                details: ".geo-details",
                detailsAttribute: "data-geo",
                types: ['geocode', 'establishment'],
                componentRestrictions: {
                    country: 'ca'
                }
            }).bind("geocode:result", function(event, result) {
                $("#id_venue_name").val("");
                $("#id_street").val("");
                $("#id_city_0").val("");                
                $("#id_tags__tagautosuggest")[0].tagspopup.forCity($("#id_geo_city").val());
                user_lat = result.geometry.location.lat();
                user_lng = result.geometry.location.lng();
                panMapToCenter(result.geometry.location.lat(), result.geometry.location.lng());

                setTimeout(function(){
                    var address = $("#id_geo_address").val(),
                        venue = $("#id_geo_venue").val();
                    if(address.indexOf(venue)===-1){
                        $("#id_place").val(
                            $("#id_geo_venue").val()+", "+$("#id_geo_address").val()
                        );    
                    }                    
                });
            });
    
            $("#id_place").on("blur", function() {
                $(".pac-container").removeClass("show");
                setTimeout(function(){
                    var address = $("#id_geo_address").val(),
                        venue = $("#id_geo_venue").val();
                    if(address.indexOf(venue)===-1){
                        $("#id_place").val(
                            $("#id_geo_venue").val()+", "+$("#id_geo_address").val()
                        );    
                    }                    
                },10);
            });
            $("#id_place").on("focus", function() {
                $(".pac-container").addClass("show");            
            });            
        },100);        
    });
})(jQuery);