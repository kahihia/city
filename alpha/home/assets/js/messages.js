;(function($, window, document, undefined) {
    'use strict';

    $(document).on("ready page:load", function(){
        window.setTimeout(function() {
            if($(".messages").length>0){
                window.ajaxPopup($(".messages")[0].outerHTML,
                                 'success',
                                 ($($(".messages")[0]).data("no-hide") === true));
            }
        }, 500);

        $("a.danger-action").on("click", function(e){
            var message = $(this).data("confirm-message") || "Are you sure?";
            return confirm(message);
        });

        $("a.event-delete-action").on("click", function() {
            var isFeatured = parseInt($(this).data("is-featured")),
                message = "Are you sure?";
            if(isFeatured) {
                message += "\r\nThis is the featured event and its remaining budget will be added to your bonus.";
            }

            return confirm(message);
        });

        $("body").on("click", "button.close", function() {
            $(this).closest(".ajax-popup").fadeOut(400, function() {$(this).remove();});
        });
    });
})(jQuery, window, document);