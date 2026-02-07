from django import template
from django.contrib.admin.templatetags.admin_urls import admin_urlname, admin_urlquote

register = template.Library()

# Re-register the admin filters
register.filter('admin_urlname', admin_urlname)
register.filter('admin_urlquote', admin_urlquote)