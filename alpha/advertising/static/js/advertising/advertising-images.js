;(function($, window, document, undefined) {
    'use strict';

    $(document).on("ready page:load", function(){
    	 $("a.advertising-image").fancybox({
            'hideOnContentClick': true
        });
    });
})(jQuery, window, document);