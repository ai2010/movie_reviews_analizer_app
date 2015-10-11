from webmining.pages.models import Page
from rest_framework import serializers


class PageSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Page
        fields = ('id', 'url', 'title', 'depth', 'html', 'old_rank', 'new_rank','content','sentiment')
