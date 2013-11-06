;(function($, window, document, undefined) {
    'use strict';

    function CreateEventPage(){
        this.doNotSubmitOnEnter();
        this.initBalloons();
        this.initVenueAccountOwner();
        this.initVenueAutocomplete();
        this.initDescriptionField();
        this.initPriceField();
        this.initWhenWidget();
    }

    CreateEventPage.prototype = {
        doNotSubmitOnEnter: function(){
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
        },
        initBalloons: function(){
            $.balloon.defaults.classname = "hintbox";
            $.balloon.defaults.css = {};
            var ballons = $(".balloon");
            $(ballons).each(function(){
                var content = $(this).siblings(".balloon-content");
                $(this).balloon({
                    contents:content,
                    position:"top",
                    tipSize: 0,
                    offsetX:0,//$.browser.msie?0:25,
                    offsetY:10,//$.browser.msie?25:0,
                    showDuration: 500, hideDuration: 0,
                    showAnimation: function(d) { this.fadeIn(d); }
                });
            });
        },
        initVenueAutocomplete: function(){
            this.venueAutocomplete = new window.VenueAutocomplete();
        },
        initDescriptionField: function(){
            var value = $("#id_description_json").val();
            this.descriptionWidget = new DescriptionWidget(document.getElementById("id_description"));            
            
            if(value){
                var json = JSON.parse(value);
                $("#id_description").html(json["default"]);
                this.descriptionWidget.setValue(json);
                this.descriptionWidget.saveCurrentDay();
            }
        },
        initPriceField: function(){
            var priceInput = $("#id_price");
            this.price = new PriceWidget(priceInput);
        },
        initVenueAccountOwner: function(){
            this.venueAccountOwner = new VenueAccountOwnerWidget();
        },
        initWhenWidget: function(){
            $(document).on("mousemove", '[data-event="click"] a', function(e) {
                if(!('event' in window)) {
                    window.eventObj = e;
                }
            });
            $("#id_when").when();
            
            if($("#id_when_json").val()) {
                $("#id_when").data("ui-when").setValue(
                    JSON.parse(
                        $("#id_when_json").val()
                    )
                );
            };
        }
    };

    $(document).on("ready page:load", function(){
        window.createEventPage = new CreateEventPage();
    });

})(jQuery, window, document);
