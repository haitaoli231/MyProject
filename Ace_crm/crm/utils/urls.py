from django.urls import reverse


def reverse_url(request, name, *args, **kwargs):
    # ?next=/crm/customer_list/?query=1&page=2
    next = request.GET.get('next')
    if next:
        return next
    else:
        return reverse(name, args=args, kwargs=kwargs)
