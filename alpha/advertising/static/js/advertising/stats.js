;(function($, window, document, undefined) {
    'use strict';

    function AdvertisingStats(){
        var that = this;
        this.container = $(".advertising-stats");
        this.detailedView = $(".detailed-view", this.container);
        this.lines = $(".ad-line", this.container);

        _.each(this.lines, function(line){
            $(line).on("click", function(){
                var cells = $("[data-stat-key]", line);
                _.each(cells, function(cell){
                    var key = $(cell).data("stat-key"),
                        value = $(cell).data("stat-value")||$(cell).html();

                    $("[data-stat-key=" + key + "]", that.detailedView).html(value);

                });

                $(that.lines).removeClass("selected");
                $(line).addClass("selected");
            });
        });

        
        
    }

    AdvertisingStats.prototype = {
        
        
    };

    window.AdvertisingStats = AdvertisingStats;

})(jQuery, window, document);