;(function($, window, document, undefined) {

    'use strict';

    var SearchPadPopup = function(){
        var that=this;
        this.openButton = $(".search-pad-popup-open-button");
        this.popup = $(".search-pad-popup");

        this.openButton.on("click", function(){            
            that.open();
        });
    };

    SearchPadPopup.prototype = {
        open: function(){
            this.prepareSearchPad();      
            $.fancybox($(this.popup), {                
                closeBtn: true,
                hideOnOverlayClick: false,
                width: 600
            });

        },
        prepareSearchPad: function(){
            this.popup.load('/events/search/', function() {

            });
        }
    };

    $(document).on("ready page:load", function(){
        window.searchPadPopup = new SearchPadPopup();
    });

})(jQuery, window, document);