;(function($, window, document, undefined) {
    'use strict';

    function VenueEditPage(){
        this.initCKEditor();
        this.watchTagsCount();
    }

    VenueEditPage.prototype = {
        initCKEditor: function(){
            CKEDITOR.instances.id_about.on("instanceReady", function(){
                CKEDITOR.instances.id_about.on('paste', function(e){
                    e.data.html = e.data.dataValue.replace(/\s*width="[^"]*"/g, '');
                });

                CKEDITOR.instances.id_about.resize(340, 200);
            });
        },
        watchTagsCount: function(){
            setInterval(this.calculateTagsCount.bind(this), 50);
        },
        calculateTagsCount: function(){
            var count = _.filter($("#as-values-id_tags__tagautosuggest").val().split(","), function(tag){ 
                return tag.trim(); 
            }).length;

            $(".tags-counter").text(count);

            if(count>10) {
                $(".tags-counter-container").addClass("overflow");
            } else {
                $(".tags-counter-container").removeClass("overflow");
            }
        }
    };

    $(document).on("ready page:load", function(){
        window.venueEditPage = new VenueEditPage();
    });

})(jQuery, window, document);