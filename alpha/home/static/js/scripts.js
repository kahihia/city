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
    //this hides all the tags after the first ten.
    $('#tags ul li').slice(10).hide();
    $('#tags ul').append('<li><a href="#" class="more"><span class="tickbox"><span class="downtick"></span></span>More</a></li>');
    $('#tags ul').find('li:last').bind('click', function(){ $(this).siblings(':gt(10)').toggle(); $(this).toggle(); });
    $('#tags ul').append('<li><a href="#" class="more"><span class="tickbox"><span class="uptick"></span></span>Fewer</a></li>');
    $('#tags ul').find('li:last').hide().bind('click', function(){ $(this).siblings(':gt(10)').toggle(); $(this).toggle(); });
}

if ( $('.active').filter(':hidden').length > 0) {
    $('.more').filter(':visible').trigger('click');
}