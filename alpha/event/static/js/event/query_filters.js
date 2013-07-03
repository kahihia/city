;(function($, window, document, undefined) {

    'use strict';

    var QueryFilters = function(){
        this.params = $.url(window.location.href).data.param.query;
    };

    QueryFilters.prototype = {
        setFilter: function(key, value){
            this.params[key] = value;
            return this;
        },
        getURL: function(){
            return "/events?" + $.param(this.params, true);
        }        
    };

    $(document).on("ready page:load", function(){
        window.filters = new QueryFilters();
    });

})(jQuery, window, document);