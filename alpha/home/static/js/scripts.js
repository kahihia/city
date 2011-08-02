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

//this hides all the tags after the first ten.
$('#tags ul li').filter(':gt(10)').hide();


$('#tags ul').append('<li>more</li>').find('li:last').click(function(){
    $(this).siblings(':gt(1)').toggle();
});
