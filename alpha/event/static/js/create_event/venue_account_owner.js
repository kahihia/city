;(function($, window, document, undefined) {
    'use strict';

    function VenueAccountOwnerWidget(){
        var that = this;

        if($(".venue-account-owner-dropdown select option").length<=1){
            $(".event-owner-tr, .venue-account-owner").hide();
        } else {
            $(".venue-account-owner-dropdown").qap_dropdown();
            this.select = $(".venue-account-owner-dropdown select");
            
            $(".venue-account-owner-dropdown").on("dropdown.change", function(){
                that.onSelect(true)
            });

            if(window.location.pathname.indexOf("events/create")!=-1) {
                // only on create
                setTimeout(function(){
                    that.onSelect(false);
                }, 200);    
            }
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
                    that.useDefaultVenueTags(tags, clear);
                });
            } else {
                $("#id_place").val("");
                $("#id_linking_venue_mode").val("");
            }

            if($("#id_tags__tagautosuggest").length !== 0) {
                $("#id_tags__tagautosuggest")[0].tagspopup.loadTagsForCityByVenueAccount();
            }
        },
        getUserContextType: function(){
            return this.select.val().split("|")[0];
        },
        useDefaultVenueTags: function(tags, clear){
            $("#id_tags__tagautosuggest")[0].tagspopup.useDefaultTags(tags, clear);
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
