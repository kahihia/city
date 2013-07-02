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

    SearchPadPage.prototype = {
        open: function(){
            this.prepareSearchPad();            
            this.popup.show();

        },
        prepareSearchPad: function(){

        }
    };

    $(document).on("ready page:load", function(){
        window.searchPadPopup = new SearchPadPopup();
    });

})(jQuery, window, document);