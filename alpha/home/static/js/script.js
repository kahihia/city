/* Author: 
   Pulled from: http://stackoverflow.com/questions/2758651/how-to-change-height-div-on-window-resize

*/
$(document).ready(function() {
    var bodyheight = $(document).height();
    $("#container").height(bodyheight);
});

// for the window resize
$(window).resize(function() {
    var bodyheight = $(document).height();
    $("#container").height(bodyheight);
});




















