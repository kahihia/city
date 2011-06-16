from events import utils
# Create your views here.

def create(request, form_class=EventForm, success_url=None,
                 template_name='events/create_event.html'):
    # on success, redirect to the event detail by default
    if success_url is None:
        success_url = reverse('events_event_detail')
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES)
        if form.is_valid():
            event_object = form.save(commit=False)
            event_object.authentication_key = create_authentication_key(form.email)
            event_object.publick_key = create_authentication_key(form.name)
            event_object.save()
            return HttpResponseRedirect(success_url)
    else:
        form = form_class()

    context = RequestContext(request)
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)

#def event_detail():

def edit(request, form_class=EventForm, success_url=None,
         template_name='events/edit_event.html'):

    # Event object is retrieved based on incoming path hash
    # If the hash does not match an existing event, the user
    # is redirected to the event creation page.
    try:
        event_obj = get_event(request.authentication_key)
    except ObjectDoesNotExist:
        return HttpResponseRedirect(reverse('event_create'))

    # Verify and save the form to model
    if request.method == 'POST':
        form = form_class( instance = event_obj,
                              files = request.FILES,
                               data = request.POST )
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(success_url)
    else:
        form = form_class(instance = event_obj)
    
    # Edit the event
    context = RequestContext(request)
    return render_to_response(template_name,
                              { 'form': form },
                              context_instance=context)
