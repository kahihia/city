;(function($, window, document, undefined) {
    'use strict';

    function VenueAccountOwnerWidget(){
        var that = this;

        $(".venue-account-owner-dropdown").qap_dropdown();        
        this.select = $(".venue-account-owner-dropdown select");
        
        $(".venue-account-owner-dropdown").on("dropdown.change", function(){
            var values = that.select.val().split("|"),
                user_context_type = values[0],
                user_context_id = values[1],
                place = values[2];


            $("#id_user_context_type").val(user_context_type);
            $("#id_user_context_id").val(user_context_id);            

            if(user_context_type=="venue_account"){
                $("#id_place").val(place);
                $("#id_linking_venue_mode").val("OWNER");
            } else {
                $("#id_place").val("");
                $("#id_linking_venue_mode").val("");
            }

            if($("#id_tags__tagautosuggest").length !== 0) {
                $("#id_tags__tagautosuggest")[0].tagspopup.loadTagsForCityByVenueAccount();
            }
        });
    }

    VenueAccountOwnerWidget.prototype = {        
        getUserContextType: function(){
            return this.select.val().split("|")[0];
        }
    };

    window.VenueAccountOwnerWidget = VenueAccountOwnerWidget;

})(jQuery, window, document);
