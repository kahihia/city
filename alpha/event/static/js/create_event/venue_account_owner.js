;(function($, window, document, undefined) {
    'use strict';

    function VenueAccountOwnerWidget(){
        var that = this;

        $(".venue-account-owner-dropdown").qap_dropdown();        
        this.select = $(".venue-account-owner-dropdown select");
        
        $(".venue-account-owner-dropdown").on("dropdown.change", function(){
            var values = that.select.val().split("|"),
                user_context_type = values[0],
                user_context_id = values[1];

            console.log([user_context_type, user_context_id]);
            $("#id_user_context_type").val(user_context_type);
            $("#id_user_context_id").val(user_context_id);

            that.showOrHideLocationWidget();
        });

        this.showOrHideLocationWidget();
    }

    VenueAccountOwnerWidget.prototype = {
        showOrHideLocationWidget: function(){
            if(this.getUserContextType() == "venue_account"){
                $(".location-tr").hide();
            } else {
                $(".location-tr").show();
            }

        },
        getUserContextType: function(){
            return this.select.val().split("|")[0];
        }
    };

    window.VenueAccountOwnerWidget = VenueAccountOwnerWidget;

})(jQuery, window, document);
