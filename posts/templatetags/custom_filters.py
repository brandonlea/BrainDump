"""
Custom template filters for the BrainDump application.
Provides filters for accessing dictionary values in templates.
"""

from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a key.
    Usage: {{ dict|get_item:key }}
    """
    if dictionary:
        return dictionary.get(key)
    return None