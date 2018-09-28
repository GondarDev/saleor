from django.templatetags.static import static
from django.template import Library

register = Library()


@register.simple_tag
def placeholder(size):
    return static('images/placeholder{size}x{size}.png'.format(size=size))
