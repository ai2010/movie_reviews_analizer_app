from django.shortcuts import render, get_object_or_404, redirect
from rest_framework import viewsets, generics, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from webmining.pages.serializers import PageSerializer
from webmining.pages.models import Page


#REMARK: 
#the page_size has to be set up from the LargeResultsSetPagination
#to avoid that the call collect partial results!!!!
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000
    
class PagesList(generics.ListAPIView):

    serializer_class = PageSerializer
    #page_size = 100
    permission_classes = (AllowAny,)
    pagination_class = LargeResultsSetPagination
    
    def get_queryset(self):
        return Page.objects.all()
