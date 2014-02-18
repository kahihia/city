;(function($, window, document, undefined) {
    'use strict';

    function VenueAccountOwnerWidget(tagsWidget){
        var that = this;

        this.tagsWidget = tagsWidget;

        $(".venue-account-owner-dropdown").qap_dropdown();
        this.select = $(".venue-account-owner-dropdown select");

        if($(".venue-account-owner-dropdown select option").length > 1) {
            $(".venue-account-owner-dropdown").on("dropdown.change", function() {
                that.onSelect(true)
            });
        }

        if(window.location.pathname.indexOf("events/create")!=-1) {
            that.onSelect(false);
        }
    }

    VenueAccountOwnerWidget.prototype = {
        onSelect: function(clear){
            var that = this,
                values = this.select.val().split("|"),
                user_context_type = values[0],
                user_context_id = values[1],
                place = values[2];

            $("#id_user_context_type").val(user_context_type);
            $("#id_user_context_id").val(user_context_id);            

            if(user_context_type=="venue_account"){
                $("#id_place").val(place);
                $("#id_linking_venue_mode").val("OWNER");

                $.post("/venues/venue-account-tags/" + user_context_id, {}, function(data){
                    var tags = data.tags;
                    that.loadTagsForVenueAccount(tags, clear);
                });
            } else {
                $("#id_place").val("");
                $("#id_linking_venue_mode").val("");
            }

            that.tagsWidget.loadTagsForCityByVenueAccount();
        },
        getUserContextType: function(){
            return this.select.val().split("|")[0];
        },
        loadTagsForVenueAccount: function(tags, clear){
            this.tagsWidget.loadTagsForVenueAccount(tags, clear);
        },
        getVenueAccountId: function(){
            if(this.getUserContextType()=="venue_account") {
                return this.select.val().split("|")[1];
            } else {
                return null;
            }
        }
    };

    window.VenueAccountOwnerWidget = VenueAccountOwnerWidget;

})(jQuery, window, document);
