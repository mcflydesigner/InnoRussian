from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    params = context['request'].GET.copy()

    for key, val in kwargs.items():
        params[key] = val

    return params.urlencode()