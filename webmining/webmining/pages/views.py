import cPickle
import datetime
import email
import os
import urllib

import numpy

from django.shortcuts import render
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader
from django.utils.datastructures import SortedDict

# Create your views here.