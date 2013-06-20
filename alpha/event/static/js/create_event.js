(function ($) {
    $(document).ready(function () {
        var keyStop = {
            13: "input, textarea", // stop enter = submit

            end: null
        };
        $(document).bind("keydown", function(event){
            var selector = keyStop[event.which];

            if(selector !== undefined && $(event.target).is(selector)) {
                event.preventDefault(); //stop event
            }
            return true;
        });
        
        setTimeout(function(){
            $.balloon.defaults.classname = "hintbox";
            $.balloon.defaults.css = {};
            var ballons = $(".balloon");
            $(ballons).each(function(){
                var content = $(this).siblings(".balloon-content");
                $(this).balloon({
                    contents:content,
                    position:"left bottom",
                    tipSize: 0,
                    offsetX:0,//$.browser.msie?0:25,
                    offsetY:25,//$.browser.msie?25:0,
                    showDuration: 500, hideDuration: 0,
                    showAnimation: function(d) { this.fadeIn(d); }
                });
            });
            
        },1000);
    });
})(jQuery);
