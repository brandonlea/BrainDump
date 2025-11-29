"""
Custom template filters for BrainDump application.

Provides utility filters for use in Django templates.
"""

from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary by key in templates.

    Usage in template: {{ my_dict|get_item:my_key }}

    Args:
        dictionary: Dictionary to access
        key: Key to look up

    Returns:
        Value from dictionary or None if key not found
    """
    return dictionary.get(key)


@register.filter
def format_datetime(value):
    """
    Format datetime for HTML5 datetime attribute.

    HTML5 requires datetime to have 0-3 digits for fractional seconds.
    Django's isoformat() outputs 6 digits by default.

    Usage in template: {{ post.created_at|format_datetime }}

    Args:
        value: datetime object

    Returns:
        str: ISO format datetime with max 3 fractional second digits
    """
    if value:
        # Format to ISO with timezone
        dt_str = value.isoformat()
        # Find the fractional seconds part and truncate to 3 digits
        if '.' in dt_str and '+' in dt_str:
            # Split on the decimal point
            before_dot, after_dot = dt_str.split('.')
            # Get fractional part and timezone
            fractional, tz = after_dot.split('+')
            # Truncate to 3 digits
            fractional = fractional[:3]
            # Reconstruct
            return f"{before_dot}.{fractional}+{tz}"
        elif '.' in dt_str and 'Z' in dt_str:
            # Handle UTC timezone with Z
            before_dot, after_dot = dt_str.split('.')
            fractional = after_dot.replace('Z', '')[:3]
            return f"{before_dot}.{fractional}Z"
        return dt_str
    return ''
