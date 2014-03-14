;(function($, window, document, undefined) {
    'use strict';

    function EditVenueAccountPage() {
        this.initLocationChanging();
    }

    EditVenueAccountPage.prototype = {
        initLocationChanging: function() {
            this.changeIndicationInput = $("[data-id=venue_changing_indicator]");
            this.venueNameBlock = $(".venue-account-venue-name");
            this.venueAutocompleteBlock = $(".venue-wrapper");
            $("body").on("click", "[data-id=change_venue_link]", {"obj": this}, this.onChangeClick);
        },
        onChangeClick: function(event) {
            var _this = event.data.obj;

            _this.changeIndicationInput.val(1);
            _this.venueNameBlock.hide();
            _this.venueAutocompleteBlock.removeClass("hidden");
        }
    };

    $(document).on("ready page:load", function(){
        window.editVenueAccountPage = new EditVenueAccountPage();
    });

})(jQuery, window, document);