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
            return "/events/browse?" + $.param(this.params, true);
        }
        
    };

    $(window).load(function(){
        window.filters = new QueryFilters();
    });

})(jQuery, window, document);