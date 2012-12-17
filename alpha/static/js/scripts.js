$('#city-nav a').bind('click', function() {
    $('#city-nav a, #city-widget').toggleClass('active');
    return false;
});

$('html').click(function() {
    if($('#city-widget').hasClass('active') == true)
    {
	$('#city-nav a, #city-widget').toggleClass('active');
    }
});
$('#city-widget').click(function(event){
    event.stopPropagation();
});

$('.addevent').click(function(remove_time) {
    $('.end_time').toggle();
    $('#addevent').toggle();
    remove_time.preventDefault();
    remove_time.stopPropagation();
});

// Tags list in event_browse: More/less toggle buttons
if ($('#tags ul').children().length > 10) {
    $('#tags_more').bind('click', function(){ $(this).siblings(':gt(10)').toggle(); $(this).toggle(); });
    $('#tags_less').bind('click', function(){ $(this).siblings(':gt(10)').toggle(); $(this).toggle(); });
}

if ( $('.active').filter(':hidden').length > 0) {
    $('.more').filter(':visible').trigger('click');
}