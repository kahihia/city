;(function($, window, document, undefined) {
    'use strict';

    function CreateEventPage(){
        this.doNotSubmitTwice();
        this.doNotSubmitOnEnter();
        this.initBalloons();
        this.initTagsWidget();
        this.initVenueAccountOwner();
        this.initVenueAutocomplete();
        this.initDescriptionField();
        this.initPriceField();
        this.initWhenWidget();
        this.initImagesWidget();
        this.initAttachmentsWidget();        
    }

    CreateEventPage.prototype = {
        doNotSubmitTwice: function() {
            $("body").on("click", "[data-id=event_submit]", function() {
                if(!$(this).attr("data-submitted")) {
                    $(this).attr("data-submitted", 1);
                    return true;
                }

                return false;
            });
        },
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
            if($("#id_location_lng").val() == 0 && $("#id_location_lat").val() == 0) {
                this.venueAutocomplete.suggestForm.initSuggestMapPosition();
            }
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
            this.venueAccountOwner = new VenueAccountOwnerWidget(this.tagsWidget);
        },
        initWhenWidget: function(){
            var when_json = $("#id_when_json").val();
            $(document).on("mousemove", '[data-event="click"] a, .my-time-picker .remove', function(e) {
                if(!('event' in window)) {
                    window.eventObj = e;
                }
            });

            this.when = new When(
                document.getElementById("id_when")
            );
            
            if(when_json) {
                this.when.setValue(
                    JSON.parse(when_json)
                );
            };
        },
        initImagesWidget: function(){
            new CroppedImages(
                document.getElementById("id_images")
            );
        },
        initAttachmentsWidget: function(){
            new Attachments(
                document.getElementById("id_attachments")
            );
        },
        initTagsWidget: function(){
            this.tagsWidget = new TagsWidget();
        }
    };

    $(document).on("ready page:load", function(){
        window.createEventPage = new CreateEventPage();
    });

})(jQuery, window, document);
