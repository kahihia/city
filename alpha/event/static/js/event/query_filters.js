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
        removeFilter: function(key){
            delete this.params[key];
            return this;
        },
        getURL: function(){
            return window.location.pathname + "?" + $.param(this.params, true);
        }        
    };

    $(document).on("ready page:load", function(){
        window.filters = new QueryFilters();
    });

})(jQuery, window, document);