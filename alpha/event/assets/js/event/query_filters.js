;(function($, window, document, undefined) {

    'use strict';

    var QueryFilters = function(){        
        var params = $.url(window.location.href).data.param.query;

        this.params = {};

        for(var key in params) {
            if(key && params[key]) {
                this.params[key] = params[key];
            }
        }
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
        getURL: function(root){
            if(!root) {
                root = window.location.pathname;
            }
                        
            return root + "?" + $.param(this.params, true);
        },
        clear: function(){
            this.params = {};
            return this;
        }
    };

    $(document).on("ready page:load", function(){
        window.filters = new QueryFilters();
    });

})(jQuery, window, document);