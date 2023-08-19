from django import template

register = template.Library()

def sort_variations_by_size_color(variations):
    return sorted(variations, key=lambda variation: (variation.frame_size, variation.color))
    
register.filter('sort_variations', sort_variations_by_size_color)
