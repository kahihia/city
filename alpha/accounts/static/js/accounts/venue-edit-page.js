;(function($, window, document, undefined) {
    'use strict';

    function VenueEditPage(){
        this.initCKEditor();
    }

    VenueEditPage.prototype = {
        initCKEditor: function(){
            CKEDITOR.instances.id_about.on("instanceReady", function(){
                CKEDITOR.instances.id_about.on('paste', function(e){
                    e.data.html = e.data.dataValue.replace(/\s*width="[^"]*"/g, '');
                });

                CKEDITOR.instances.id_about.resize(340, 200);
            });
        }
    };

    $(document).on("ready page:load", function(){
        window.venueEditPage = new VenueEditPage();
    });

})(jQuery, window, document);