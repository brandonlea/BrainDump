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
