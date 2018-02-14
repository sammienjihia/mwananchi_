from django import template

register = template.Library()

@register.filter(name='check_field_name')
def check_field_name(value):
    if value == 'county' or value == 'ward' or value == 'constituency' or value == 'region_name':
        return True
    else:
        return False

@register.filter(name='divisible_by_2')
def divisible_by_2(value):
    if value%2 == 0:
        return True
    else:
        return False
@register.filter(name='check_label_name')
def check_label_name(value):
    if value == 'Email' or value == 'Ward' or value == 'Constituency':
        return True
    else:
        return False
