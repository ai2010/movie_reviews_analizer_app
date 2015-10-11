import datetime
import os
import urllib2
import urllib
import numpy
import json
from django.shortcuts import render
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template import loader

from webmining.pages.models import Page,SearchTerm
from webmining.pgrank.pgrank import pgrank
import nltk.classify.util, nltk.metrics
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.corpus import stopwords
import itertools
from nltk.collocations import BigramCollocationFinder
from nltk.metrics import BigramAssocMeasures
import collections
import logging



# Bing API key
API_KEY = "X/+6jgJS0FkPGql4w7tphwJh2dj+trSqXxcnbSZUHPc"

#PARAMETERS
test_mode = False
num_reviews = 10

# Create your views here.


def about(request):
    return render(request, 'movie_reviews/about.html',
                          {'request': request})
                          
def bing_api(query, source_type = "Web", top = 10, format = 'json'):
    keyBing = API_KEY        # get Bing key from: https://datamarket.azure.com/account/keys
    credentialBing = 'Basic ' + (':%s' % keyBing).encode('base64')[:-1] # the "-1" is to remove the trailing "\n" which encode adds
    searchString = '%27X'+query.replace(" ",'+')+'movie+review%27'
    top = 50
    offset = 0

    url = 'https://api.datamarket.azure.com/Bing/Search/Web?' + \
          'Query=%s&$top=%d&$skip=%d&$format=json' % (searchString, top, offset)

    request = urllib2.Request(url)
    request.add_header('Authorization', credentialBing)
    requestOpener = urllib2.build_opener()
    response = requestOpener.open(request) 

    results = json.load(response)
    reviews_urls = [ d['Url'] for d in results['d']['results']]

    print 'REVIEWS NUMBER:',len(reviews_urls)
    return reviews_urls

def parse_bing_results():
    file_data = open(os.path.dirname(__file__)+'/bing_the_martian_results.json','r')
    bing_json = json.load(file_data)
    print len(bing_json['d']['results'])
    reviews_urls = [ d['Url'] for d in bing_json['d']['results']]
    print reviews_urls
    return reviews_urls
            
def analyzer(request):
    """View that renders the main search page and results.
    """
    context = {}

    if request.method == 'POST':
        post_data = request.POST
        query = post_data.get('query', None)
        if query:
            return redirect('%s?%s' % (reverse('webmining.views.analyzer'),
                                urllib.urlencode({'q': query})))   
    elif request.method == 'GET':
        get_data = request.GET
        query = get_data.get('q')
        if not query:
            context['no_header_search_box'] = True
            return render_to_response(
                'movie_reviews/home.html', RequestContext(request, context))

        context['query'] = query
        stripped_query = query.strip()
        urls = []
        
        if test_mode:
           urls = parse_bing_results()
        else:
           urls = bing_api(stripped_query)
           
        if len(urls)== 0:
           return render_to_response(
               'movie_reviews/noreviewsfound.html', RequestContext(request, context))
               
        print 'urls:',str(urls[:num_reviews])
        if not SearchTerm.objects.filter(term=stripped_query).exists():
           s = SearchTerm(term=stripped_query)
           s.save()
           try:
               #scrape
               cmd = 'cd ../scrapy_spider & scrapy crawl scrapy_spider_reviews -a url_list=%s -a search_key=%s' %('\"'+str(','.join(urls[:num_reviews]).encode('utf-8'))+'\"','\"'+str(stripped_query)+'\"')
               print 'cmd:',cmd
               os.system(cmd)
           except:
               print 'error!'
               s.delete()
        else:
           #collect the pages already scraped 
           s = SearchTerm.objects.get(term=stripped_query)
           
        #calc num pages
        pages = s.pages.all().filter(review=True)
        if len(pages) == 0:
           s.delete()
           return render_to_response(
               'movie_reviews/noreviewsfound.html', RequestContext(request, context))
               
        s.num_reviews = len(pages)
        s.save()
         
        context['searchterm_id'] = int(s.id)


        #train classifier with nltk
        def train_classifier(featx):
            train_portion =1#9/10.
            negids = movie_reviews.fileids('neg')
            posids = movie_reviews.fileids('pos')
 
            negfeatures = [(featx(movie_reviews.words(fileids=[file])), 'neg') for file in negids]
            posfeatures = [(featx(movie_reviews.words(fileids=[file])), 'pos') for file in posids]

 
            trainfeatures = negfeatures[:] + posfeatures[:]
 
            classifier = NaiveBayesClassifier.train(trainfeatures)
            '''
 
            negcutoff = int(len(negfeatures)*train_portion)
            poscutoff = int(len(posfeats)*train_portion)
            testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]

            refsets = collections.defaultdict(set)
            testsets = collections.defaultdict(set)
 
            for i, (feats, label) in enumerate(testfeats):
                    refsets[label].add(i)
                    observed = classifier.classify(feats)
                    testsets[observed].add(i)
 
            print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
            print 'pos precision:', nltk.metrics.precision(refsets['pos'], testsets['pos'])
            print 'pos recall:', nltk.metrics.recall(refsets['pos'], testsets['pos'])
            print 'neg precision:', nltk.metrics.precision(refsets['neg'], testsets['neg'])
            print 'neg recall:', nltk.metrics.recall(refsets['neg'], testsets['neg'])
            classifier.show_most_informative_features()
            '''
            return classifier
            
        stopset = set(stopwords.words('english'))
        def stopword_filtered_word_features(words):
            return dict([(word, True) for word in words if word not in stopset])
            
        def bigram_word_features(words, score_fn=BigramAssocMeasures.chi_sq, n=200):
            bigram_finder = BigramCollocationFinder.from_words(words)
            bigrams = bigram_finder.nbest(score_fn, n)
            return dict([(ngram, True) for ngram in itertools.chain(words, bigrams)])
 
        #classifier = evaluate_classifier(stopword_filtered_word_features)
        classifier = train_classifier(bigram_word_features)
        
        cntpos = 0
        cntneg = 0
        for p in pages:
            words = p.content.split(" ")
            feats = bigram_word_features(words)#stopword_filtered_word_feats(words)
            #print feats
            str_sent = classifier.classify(feats)
            if str_sent == 'pos':
               p.sentiment = 1
               cntpos +=1
            else:
               p.sentiment = -1
               cntneg +=1
            p.save()

        context['reviews_classified'] = len(pages)
        context['positive_count'] = cntpos
        context['negative_count'] = cntneg

        context['classified_information'] = True

    return render_to_response(
        'movie_reviews/home.html', RequestContext(request, context))

def pgrank_view(request,pk): 
    context = {}
    get_data = request.GET
    scrape = get_data.get('scrape','False')
    s = SearchTerm.objects.get(id=pk)
    
    if scrape == 'True':
        pages = s.pages.all().filter(review=True)
        urls = []
        for u in pages:
            urls.append(u.url)
        #crawl
        cmd = 'cd ../scrapy_spider & scrapy crawl scrapy_spider_recursive -a url_list=%s -a search_id=%s' %('\"'+str(','.join(urls[:num_reviews]).encode('utf-8'))+'\"','\"'+str(pk)+'\"')
        print 'cmd:',cmd
        os.system(cmd)
    else:
        #check links are available
        links = s.links.all()
        if len(links)==0:
           context['no_links'] = True
           return render_to_response(
               'movie_reviews/pg-rank.html', RequestContext(request, context))
    #calc pgranks
    pgrank(pk)
    #load pgranks in descending order of pagerank
    pages_ordered = s.pages.all().filter(review=True).order_by('-new_rank')
    context['pages'] = pages_ordered
    
    return render_to_response(
        'movie_reviews/pg-rank.html', RequestContext(request, context)) 