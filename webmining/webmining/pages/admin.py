from django.contrib import admin
from django_markdown.admin import MarkdownField, AdminMarkdownWidget

from webmining.pages.models import SearchTerm,Page,Link
# Register your models here.

class SearchTermAdmin(admin.ModelAdmin):
    formfield_overrides = {MarkdownField: {'widget': AdminMarkdownWidget}}
    list_display = ['id', 'term', 'num_reviews']
    ordering = ['-id']
    
class PageAdmin(admin.ModelAdmin):
    formfield_overrides = {MarkdownField: {'widget': AdminMarkdownWidget}}
    list_display = ['id', 'searchterm', 'url','title']
    ordering = ['-id']
    
admin.site.register(SearchTerm,SearchTermAdmin)
admin.site.register(Page,PageAdmin)
admin.site.register(Link)