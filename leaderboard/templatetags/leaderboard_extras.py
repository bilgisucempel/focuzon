from django import template
register = template.Library()

@register.filter
def hm(total_minutes):
    """
    90  -> '1 h 30 m'
    60  -> '1 h'
    45  -> '45 m'
    0   -> '0 m'
    """
    try:
        total_minutes = int(total_minutes)
    except (TypeError, ValueError):
        return ""
    hours, minutes = divmod(total_minutes, 60)
    if hours and minutes:
        return f"{hours} h {minutes} m"
    if hours:
        return f"{hours} h"
    return f"{minutes} m"
