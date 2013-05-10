;(function($, window, document, undefined) {
    $(document).on("page:change", function(){
        window.prevPageYOffset = window.pageYOffset;
        window.prevPageXOffset = window.pageXOffset;
    });
        
    $(document).on("page:load", function(){
        // if($(".fix-scroll").length > 0){
        //     $('.fix-scroll').hide().show();
            window.scrollTo(window.prevPageXOffset, window.prevPageYOffset);
        // }
    });
})(jQuery, window, document);