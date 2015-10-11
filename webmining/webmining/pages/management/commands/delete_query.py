from webmining.pages.models import Link,Page,SearchTerm
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option





class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
                make_option('-n', '--searchid',
                             dest='searchid', type='int',
                             action='store',
                             help=('id of the search term to delete')),
       )


    def handle(self, *args, **options):
         searchid = options['searchid']
         search_obj = SearchTerm.objects.get(id=searchid)
         pages = search_obj.pages.all()
         pages.delete()
         links = search_obj.links.all()
         links.delete()