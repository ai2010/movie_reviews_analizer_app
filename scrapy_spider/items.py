# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy_djangoitem import DjangoItem
from scrapy.item import Field

from webmining.pages.models import Page,Link,SearchTerm

class SearchItem(DjangoItem):
    # fields for this item are automatically created from the django model
    django_model = SearchTerm
class PageItem(DjangoItem):
    # fields for this item are automatically created from the django model
    django_model = Page
class LinkItem(DjangoItem):
    django_model = Link