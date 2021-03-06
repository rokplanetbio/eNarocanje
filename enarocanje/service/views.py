import datetime
import json
import pdb
import urllib

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import FieldError
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from post_office import mail

from enarocanje.accountext.decorators import for_service_providers
from enarocanje.accountext.forms import ServiceProviderImageForm
from enarocanje.accountext.models import ServiceProvider, ServiceProviderImage, Category as SPCategory
from enarocanje.ServiceProviderEmployee.models import ServiceProviderEmployee, ServiceProviderEmployeeImage
from enarocanje.reservations.models import Reservation
from enarocanje.settings import DEFAULT_FROM_EMAIL
from enarocanje.workinghours.models import EmployeeWorkingHours
from forms import ServiceForm, FilterForm, DiscountFormSet, CommentForm
from models import Service, Category, Discount, Comment, User

# List of services for editing

def view_gallery(request, id):

    gallery = ServiceProviderImage.objects.filter(service_provider_id=id)
    # ServiceProviderImage.objects.all().delete()
    edit_gallery = False
    # print "id, provID", id, request.user.service_provider_id
    if hasattr(request.user, 'service_provider_id'):
        if str(id) == str(request.user.service_provider_id):
            edit_gallery = True

    if request.method == 'POST':
        if request.POST.get('action') == 'delete':
            form = ServiceProviderImageForm()
            if request.POST.getlist('img_id'):
                for img_id in request.POST.getlist('img_id'):
                    print "iiid", img_id
                    img = ServiceProviderImage.objects.get(id=int(img_id))
                    img.delete()

        if request.POST.get('action') == 'update':
            form = ServiceProviderImageForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.save(commit=False)
                image.service_provider_id = request.user.service_provider_id
                image.save()
    else:
        form = ServiceProviderImageForm()

    return render_to_response('browse/gallery.html', locals(), context_instance=RequestContext(request))

@for_service_providers
def myservices(request):
    services = request.user.service_provider.services.all()
    durations = set(service.duration for service in services)
    # discounts = set(service.get_discount().discount for service in services if service.get_discount())
    discounts = set(discount.discount for discount in Discount.objects.filter(service__in=services))
    filter_form = FilterForm(request.GET, durations=sorted(list(durations)), discounts=discounts)
    if filter_form.is_valid():
        if filter_form.cleaned_data['duration'] != 'all':
            services = services.filter(duration=filter_form.cleaned_data['duration'])
        if filter_form.cleaned_data['discount'] != 'all':
            services = services.filter(discounts__discount=filter_form.cleaned_data['discount']).distinct()
        if filter_form.cleaned_data['active'] == 'active':
            services = [service for service in services if service.is_active()]
        elif filter_form.cleaned_data['active'] == 'inactive':
            services = [service for service in services if not service.is_active()]
    # locals() returns a dictionary of variables in the local scope (request and services in this case)
    return render_to_response('service/myservices.html', locals(), context_instance=RequestContext(request))

# Add a new service

@for_service_providers
def add(request):
    if request.method == 'POST':
        # if method was post (form submittion), fill form from post data
        form = ServiceForm(request.POST)
        form_valid = form.is_valid()
        formset = DiscountFormSet(request.POST)
        formset_valid = formset.is_valid()
        if form_valid and formset_valid:
            # if form is valid, save it and redirect back to myservices
            # commit=False tells form to not save the object to the database just yet and return it instead
            service = form.save(commit=False)
            # set service_provider to the current user before we save the object to the database
            service.service_provider = request.user.service_provider
            service.save()
            formset.instance = service
            formset.save()
            return HttpResponseRedirect(reverse(myservices))
    else:
        # on get request create empty form
        form = ServiceForm()
        formset = DiscountFormSet()
    # render form - new (get request) or invalid with error messages (post request)
    return render_to_response('service/add.html', locals(), context_instance=RequestContext(request))

# Edit existing service

@for_service_providers
def edit(request, id):
    service = get_object_or_404(Service, service_provider=request.user.service_provider, id=id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        form_valid = form.is_valid()
        formset = DiscountFormSet(request.POST, instance=service)
        formset_valid = formset.is_valid()
        if form_valid and formset_valid:
            form.save()
            formset.save()
            return HttpResponseRedirect(reverse(myservices))

    else:
        form = ServiceForm(instance=service)
        formset = DiscountFormSet(instance=service)
    return render_to_response('service/edit.html', locals(), context_instance=RequestContext(request))

# Activate/deactivate service

@for_service_providers
def manage(request):
    if request.method == 'POST':
        service = get_object_or_404(Service, service_provider=request.user.service_provider, id=request.POST.get('service'))
        if request.POST.get('action') == 'activate':
            service.active_until = None
            service.save()
        if request.POST.get('action') == 'deactivate':
            service.active_until = datetime.date.today() - datetime.timedelta(1)
            service.save()
        if request.POST.get('action') == 'delete':
            service.delete()
    return HttpResponseRedirect(reverse(myservices))

# Individual service

def service_comments(request, id):
    service = get_object_or_404(Service, id=id)
    if not service.is_active():
        raise Http404

    # check if user is allowed to comment
    if request.user.is_authenticated():
        now = datetime.datetime.now()
        reservations = Reservation.objects.filter(Q(user=request.user, service=service) & (Q(date__lt=now.date()) | Q(date=now.date(), time__lt=now.time()))).order_by('-date', '-time')
        if len(reservations) and not Comment.objects.filter(author=request.user, service=service, created__gt=datetime.datetime.combine(reservations[0].date, reservations[0].time)).exists():
            # handle form
            if request.method == 'POST':
                form = CommentForm(request.POST)
                if form.is_valid():
                    comment = form.save(commit=False)
                    comment.service = service
                    comment.author = request.user
                    comment.save()
                    return HttpResponseRedirect(reverse(service_comments, args=(id,)))
            else:
                form = CommentForm()

    # get all comments
    comments = service.comments.order_by('-created').all()

    return render_to_response('service/comments.html', locals(), context_instance=RequestContext(request))

# Browse

def int_get(d, k):
    try:
        return int(d[k])
    except:
        return None

def get_location(request):
    try:
        location = request.COOKIES.get('location')
        location = urllib.unquote(location)
        location = json.loads(location)
        location['lat'] = float(location['lat'])
        location['lng'] = float(location['lng'])
        location['accuracy'] = float(location['accuracy'])
    except:
        location = None
    return location

ORDER_CHOICES_PROVIDER = (
    (_('Order by distance'), 'dist'),
    (_('Order lexicographically'), 'lexi'),
)

def construct_url_providers(cat, q, sor, page):
    parts = []
    if cat:
        parts.append('category=%d' % cat)
    if q:
        parts.append('q=%s' % q)
    if sor != 'dist':
        parts.append('sort=%s' % sor)
    if page:
        parts.append('page=%s' % page)
    if parts:
        return '?' + '&'.join(parts)
    return reverse(browse_providers)

def browse_providers(request):
    location = get_location(request)
    providers = ServiceProvider.objects.all()

    if hasattr(request.user, 'has_service_provider'):
        if request.user.has_service_provider():
            provider = ServiceProvider.objects.get(id=request.user.service_provider_id)
            if provider.subscription_end_date < timezone.now():
                if not provider.subscription_mail_sent:
                    send_mail('Subscription expirations', 'Sorry to inform you but your subscription has expired.', 'from@example.com',
                          [request.user.email], fail_silently=False)
                provider.subscription_mail_sent = 1
                provider.save()

    cat = int_get(request.GET, 'category')
    q = request.GET.get('q', '')
    sor = request.GET.get('sort', 'dist')
    page = request.GET.get('page')

    categories = [(_('All'), construct_url_providers(None, q, sor, page), not cat)] + [
        (category.name, construct_url_providers(category.id, q, sor, page), category.id == cat)
        for category in SPCategory.objects.all()
    ]
    sort_choices = [
        (sort[0], construct_url_providers(cat, q, sort[1], page), sort[1] == sor)
        for sort in ORDER_CHOICES_PROVIDER
    ]

    if cat:
        providers = providers.filter(category_id=cat)
    if q:
        # Added support for other backends different from MySQL
        try:
            providers = providers.filter(name_search=q)
        except FieldError:
            providers = providers.filter(name__contains=q)

    # Order by
    if sor == 'dist':
        if location and settings.DATABASE_SUPPORTS_TRIGONOMETRIC_FUNCTIONS:
            providers = providers.extra(select={'dist': ServiceProvider.DISTANCE_FORMULA % location}).order_by('dist')
    elif sor == 'lexi':
        providers = providers.order_by('name')

    paginator = Paginator(providers, 12)
    try:
        providers = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        providers = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        providers = paginator.page(paginator.num_pages)

    if providers.has_previous():
        prev_page = construct_url_providers(cat, q, sor, providers.previous_page_number())
    if providers.has_next():
        next_page = construct_url_providers(cat, q, sor, providers.next_page_number())

    return render_to_response('browse/providers.html', locals(), context_instance=RequestContext(request))

SORT_CHOICES_SERVICE = (
    (_('Order by distance'), 'dist'),
    (_('Order by price'), 'price'),
    (_('Order by discount level'), 'disc'),
    (_('Order lexicographically'), 'lexi'),
)

def construct_url_services(prov, cat, disc, q, sor, page):
    parts = []
    if prov:
        parts.append('provider=%d' % prov)
    if cat:
        parts.append('category=%d' % cat)
    if disc:
        parts.append('discount=%d' % disc)
    if q:
        parts.append('q=%s' % q)
    if sor != 'dist':
        parts.append('sort=%s' % sor)
    if page:
        parts.append('page=%s' % page)
    if parts:
        return '?' + '&'.join(parts)
    return reverse(browse_services)

def browse_services(request):
    location = get_location(request)
    services = Service.objects.filter(Q(active_until__gte=datetime.date.today()) | Q(active_until__isnull=True))

    prov = int_get(request.GET, 'provider')
    cat = int_get(request.GET, 'category')
    disc = int_get(request.GET, 'discount')
    q = request.GET.get('q', '')
    sor = request.GET.get('sort', 'dist')
    page = request.GET.get('page')

    categories = [(_('All'), construct_url_services(prov, None, disc, q, sor, page), not cat)] + [
        (category.name, construct_url_services(prov, category.id, disc, q, sor, page), category.id == cat)
        for category in Category.objects.all()
    ]
    discounts = [(_('All'), construct_url_services(prov, cat, None, q, sor, page), not disc)] + [
        ('%s%%' % discount, construct_url_services(prov, cat, discount, q, sor, page), discount == disc)
        for discount in set(
            service.get_discount().discount
            for service in services if service.get_discount()
        )
    ]
    sort_choices = [
        (sort[0], construct_url_services(prov, cat, disc, q, sort[1], page), sort[1] == sor)
        for sort in SORT_CHOICES_SERVICE
    ]

    if cat:
        services = services.filter(category_id=cat)
    selected_provider = None
    if prov:
        selected_provider = get_object_or_404(ServiceProvider, id=prov)
        services = services.filter(service_provider_id=prov)
    if q:
         # Added support for other backends different from MySQL
        try:
            services = services.filter(Q(name_search=q) | Q(description_search=q))
        except FieldError:
            services = services.filter(Q(name__contains=q) | Q(description__contains=q))


    # Order by
    if sor == 'dist':
        if location and settings.DATABASE_SUPPORTS_TRIGONOMETRIC_FUNCTIONS:
            services = services.select_related('service_provider').extra(select={'dist': ServiceProvider.DISTANCE_FORMULA % location}).order_by('dist')
    elif sor == 'price':
        # TODO: sort in database
        services = sorted(services, lambda a, b: cmp(a.discounted_price() or float('inf'), b.discounted_price() or float('inf')))
    elif sor == 'disc':
        # TODO: sort in database
        services = sorted(services, lambda a, b: cmp(a.get_discount().discount if a.get_discount() else 0, b.get_discount().discount if b.get_discount() else 0), reverse=True)
    elif sor == 'lexi':
        services = services.order_by('name')

    if disc:
        services = [service for service in services if service.get_discount() and service.get_discount().discount == disc]

    paginator = Paginator(services, 12)
    try:
        services = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        services = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        services = paginator.page(paginator.num_pages)

    if services.has_previous():
        prev_page = construct_url_services(prov, cat, disc, q, sor, services.previous_page_number())
    if services.has_next():
        next_page = construct_url_services(prov, cat, disc, q, sor, services.next_page_number())

    return render_to_response('browse/services.html', locals(), context_instance=RequestContext(request))

# 16.4.2014 RokA; added for browsing employees:
ORDER_CHOICES_EMPLOYEE = (
    (_('Order lexicographically'), 'lexi'),
)

def construct_url_employees(provider, service, q, sor, page):
    parts = []
    if provider:
        parts.append('provider=%s' % provider)
    if service:
        parts.append('service=%s' % service)
    if q:
        parts.append('q=%s' % q)
    if sor != 'dist':
        parts.append('sort=%s' % sor)
    if page:
        parts.append('page=%s' % page)
    if parts:
        return '?' + '&'.join(parts)
    return reverse(browse_employees)

# RokA: naredi filtriranje podobno kot za browse_services
def browse_employees(request):
    workinghours = EmployeeWorkingHours.objects.all().values_list('service_provider_employee_id', flat=True)
    employees = ServiceProviderEmployee.objects.filter(pk__in=workinghours)


    if hasattr(request.user, 'has_service_provider'):
        if request.user.has_service_provider():
            provider = ServiceProvider.objects.get(id=request.user.service_provider_id)
            if provider.subscription_end_date < timezone.now():
                if not provider.subscription_mail_sent:
                    send_mail('Subscription expirations', 'Sorry to inform you but your subscription has expired.', 'from@example.com',
                          [request.user.email], fail_silently=False)
                provider.subscription_mail_sent = 1
                provider.save()

    prov = int_get(request.GET, 'provider')
    service = int_get(request.GET, 'service')
    q = request.GET.get('q', '')
    sor = request.GET.get('sort')
    page = request.GET.get('page')

    sort_choices = [
        (sort[0], construct_url_employees(prov, service, q, sort[1], page), sort[1] == sor)
        for sort in ORDER_CHOICES_EMPLOYEE
    ]

    selected_provider = None
    if prov:
        selected_provider = get_object_or_404(ServiceProvider, id=prov)
        employees = employees.filter(service_provider_id=prov)
    selected_service = None
    if service:
        selected_service = get_object_or_404(Service, id=service)
        workinghours = EmployeeWorkingHours.objects.filter(service=selected_service).values_list('service_provider_employee_id', flat=True)
        employees = ServiceProviderEmployee.objects.filter(pk__in=workinghours)


    if q:
        # Added support for other backends different from MySQL
        try:
            employees = employees.filter(name_search=q)
        except FieldError:
            employees = employees.filter(name__contains=q)

    # Order by
    if sor == 'lexi':
        providers = employees.order_by('last_name')

    paginator = Paginator(employees, 12)
    try:
        employees = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        employees = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        employees = paginator.page(paginator.num_pages)

    if employees.has_previous():
        # (provider, service, q, sor, page)
        prev_page = construct_url_employees(prov, service, q, sor, providers.previous_page_number())
    if employees.has_next():
        next_page = construct_url_providers(prov, service, q, sor, providers.next_page_number())

    return render_to_response('browse/employees.html', locals(), context_instance=RequestContext(request))

def service_with_employee(request):

    service_id = int_get(request.GET, 'service')

    selected_service = None
    if service_id:
        service = get_object_or_404(Service, id=service_id)

    return render_to_response('service/service.html', locals(), context_instance=RequestContext(request))
# end Employees


@for_service_providers
def managereservation(request):
    if request.method == 'POST':
        reservation = get_object_or_404(Reservation, service_provider=request.user.service_provider, id=request.POST.get('reservation'))
        if request.POST.get('action') == 'confirm':
            reservation.is_confirmed = True
            reservation.save()
            if not reservation.user:
                email_to1 = reservation.user_email
            else:
                email_to1 = reservation.user.email
            subject = _('Confirmation of service reservation')
            renderedToCustomer = render_to_string('emails/reservation_customer.html', {'reservation': reservation})
            send_mail(subject, renderedToCustomer, DEFAULT_FROM_EMAIL, [email_to1], fail_silently=False)
        if request.POST.get('action') == 'deny':
            reservation.is_deny = True
            reservation.save()
            if not reservation.user:
                email_to1 = reservation.user_email
            else:
                email_to1 = reservation.user.email
            subject = _('Your reservation was not confirmed')
            renderedToCustomer = render_to_string('emails/reservation_customer.html', {'reservation': reservation})
            send_mail(subject, renderedToCustomer, DEFAULT_FROM_EMAIL, [email_to1], fail_silently=False)
            reservation.delete()
    return HttpResponseRedirect(reverse(myunconfirmedreservations))

def managereservationall(request):

    if request.method == 'POST':
        if request.POST.get('action') == 'confirmall':
            reservations = request.user.service_provider.reservations.filter(service_provider_id=request.user.service_provider_id, is_confirmed=False, is_deny=False, isfromgcal=False, date__gte=datetime.date.today())
            for res in reservations:
                res.is_confirmed = True
                res.save()
                if not res.user:
                    email_to1 = res.user_email
                else:
                    email_to1 = res.user.email
                subject = _('Confirmation of service reservation')
                renderedToCustomer = render_to_string('emails/reservation_customer.html', {'reservation': res})
                send_mail(subject, renderedToCustomer, None, [email_to1], fail_silently=False)
        if request.POST.get('action') == 'denyall':
            reservations = request.user.service_provider.reservations.filter(service_provider_id=request.user.service_provider_id, is_confirmed=False, is_deny=False, isfromgcal=False, date__gte=datetime.date.today())
            for res in reservations:
                res.is_deny = True
                res.save()
                if not res.user:
                    email_to1 = res.user_email
                else:
                    email_to1 = res.user.email
                subject = _('Your reservation was not confirmed')
                renderedToCustomer = render_to_string('emails/reservation_customer.html', {'reservation': res})
                send_mail(subject, renderedToCustomer, None, [email_to1], fail_silently=False)
                res.delete()
    return HttpResponseRedirect(reverse(myunconfirmedreservations))


@for_service_providers
def myunconfirmedreservations(request):
    res_confirm = request.user.service_provider.reservation_confirmation_needed
    unconfirmed = Reservation.objects.filter(service_provider_id=request.user.service_provider_id, is_confirmed=False, is_deny=False, date__gte=datetime.date.today(), isfromgcal=False)
    return render_to_response('service/myunconfirmedreservation.html', locals(), context_instance=RequestContext(request))
