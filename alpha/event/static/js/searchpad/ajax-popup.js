;(function($, window, document, undefined) {
    'use strict';

    function ajaxPopup(content, type){
        var popup= $('<div>').addClass("ajax-popup").addClass("type"),
            left = ($(window).width()/2)-190,
            top = ($(window).height()/2)-100;
        popup.html(content);
        popup.css({
            left: left + "px",
            top: top + "px"
        });

        $('body').append(popup);

        setTimeout(function(){
            popup.fadeOut(1000);
            setTimeout(function(){
                popup.remove();
            }, 1000);
        }, 2000);
    }

    window.ajaxPopup = ajaxPopup;

})(jQuery, window, document);