;(function($, window, document, undefined) {
    'use strict';

    var google = window.google;

    function SuggestForm(){
        this.initFormButtons();
        this.initSuggestMap();
        this.embedSuggestVenueButtonIntoGoogleAutocomplete();
    }

    SuggestForm.prototype = {
        initFormButtons: function(){
            var that = this;
            $(".suggest .reset-button").on("click", this.resetForm.bind(this));
            $(".suggest .cancel-button").on("click", this.cancelForm.bind(this));
            $(".suggest .submit-button").on("click", this.saveForm.bind(this));
        },
        resetForm: function(){
            $(".suggest .error").hide();
            $("#id_venue_name").val("");
            $("#id_street").val("");
            $("#id_city_0").val("");
        },
        cancelForm: function(){
            this.resetForm();
            $.fancybox.close();
        },
        saveForm: function(){
            var venue, street, city, suggest_values;
            venue = $("#id_venue_name").val();
            street = $("#id_street").val();
            city = $("#id_city_0").val();

            if(!venue || !street || !city){
                $(".suggest .error").show();
                return;
            }

            suggest_values = [venue, street, city];
            $("#id_place").val(suggest_values.join(", "));

            $.fancybox.close();
        },
        initSuggestMap: function(){
            this.suggestMap = new window.SuggestMap();
        },
        embedSuggestVenueButtonIntoGoogleAutocomplete: function(){
            var $pacContainer = $(".pac-container"),
                that = this;

            if($pacContainer.length === 0){
                setTimeout(function(){
                    that.embedSuggestVenueButtonIntoGoogleAutocomplete();
                },100);
            } else {
                var suggestNewVenueButton = $("<div>").addClass("new-venue").html("suggest a new venue");

                $(".pac-container").append(suggestNewVenueButton);

                $(suggestNewVenueButton).on("mousedown", this.showSuggestPopup.bind(this));

                setInterval(function(){
                    if($(".pac-container .pac-item").length>0){
                        $(".pac-container").removeClass("suggest-new");
                    } else {
                        if($("#id_place").val().length>3){
                            $(".pac-container").addClass("suggest-new");
                        }
                    }
                }, 10);
            }
        },
        showSuggestPopup: function(){
            var that = this;
            $(".location-map-wrapper").append(
                $(".location_map").show()
            );

            $.fancybox($(".suggest"), {
                autoSize: true,
                closeBtn: true,
                hideOnOverlayClick: false
            });

            google.maps.event.trigger(this.map, 'resize');

            setTimeout(function(){
                that.suggestMap.setLocation(window.user_lat, window.user_lng);
                that.suggestMap.infowindow.open(that.map, that.marker);
            },100);
        }
    };

    window.SuggestForm = SuggestForm;

})(jQuery, window, document);