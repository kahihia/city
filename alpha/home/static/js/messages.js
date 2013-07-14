;(function($, window, document, undefined) {

    'use strict';

    $(document).on("ready page:load", function(){
        window.setTimeout(function(){
            if($(".messages").length>0){
                window.ajaxPopup($(".messages")[0].outerHTML, 'success');
            }
        }, 500);

        $("a.danger-action").on("click", function(e){
            var message = $(this).data("confirm-message") || "Are you sure?";
            return confirm(message);
        });
    });
})(jQuery, window, document);