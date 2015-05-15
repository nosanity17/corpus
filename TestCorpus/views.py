# -*- coding=utf-8 -*-
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect, render
#from models import Doc, Sentence, Error, Analysis, Token
from annotator.models import Document, Sentence, Annotation, Token, Morphology
from django.views.generic.base import View
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from forms import QueryForm
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseForbidden
from django.views.generic import View
from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.conf import settings
from django.template import *


import re
rePage = re.compile(u'&page=\\d+', flags=re.U)

from django.forms.formsets import formset_factory


class Struct:
    def __init__(self, **values):
        vars(self).update(values)


class Index(View):

    def get(self, request, page):
        doc_list = Document.objects.all()
        # эта функция просто достает нужный шаблон и показывает его
        if page == '':
            return render_to_response(u'start.html', {'docs': doc_list}, context_instance=RequestContext(request))
        page = 'simple/' + page + '.html'
        return render_to_response(page, {'docs': doc_list}, context_instance=RequestContext(request))


class Search(Index):
    # тут все для поиска
    # todo make this into a neat one-line js-function
    jquery = """jQuery(function ($) {
                $('#***').annotator()
                    .annotator('addPlugin', 'Tags')
                    .annotator('addPlugin', 'Corr')
                    .annotator('addPlugin', 'Correction', 'Enter correct variant...')
                    .annotator('addPlugin', 'ReadOnlyAnnotations')
                    .annotator('addPlugin', 'Store', {
                          prefix: '/heritage_corpus/document-annotations',
                          annotationData: {
                            'document': ***
                          },
                          loadFromSearch: {
                            'document': ***
                          }
                        });
                    });"""

    def bold(self, word, sent):
        s = re.sub('(' + word + ')', u'<b>\\1</b>', sent)
        return s

    def prepare_data(self, tokens):
        d = {}
        for t in tokens:
            if t.doc_id not in d:
                d[t.doc_id] = {t.sent: [t.num]}
            else:
                if t.sent not in d[t.doc]:
                    d[t.doc][t.sent] = [t.num]
                else:
                    d[t.doc][t.sent].append(t.num)
        dictlist = []
        for doc in d:
            sents = []
            for sent in d[doc]:
                sents.append(self.bold(sent, d[doc][sent]))
            dictlist.append((doc, sents))
        return dictlist

    # todo write search
    def get(self, request, page):  # page does nothing here, just ignore it
        if len(request.GET) < 1:
            QueryFormset = formset_factory(QueryForm, extra=2)
            return render_to_response('search.html', {'form': QueryFormset},
                                      context_instance=RequestContext(request))
        else:
            # print request.GET
            if "exact_word" in request.GET.keys():
                jq, sent_list, word = self.exact_search(request.GET["exact_word"].lower().encode('utf-8'))

            elif "wordform[]" in request.GET.keys():
                # QueryFormset = formset_factory(QueryForm)
                # formset = QueryFormset(request.GET, request.FILES)
                # if formset.is_valid():
                # todo rewrite this part of search
                query = request.GET
                jq, sent_list, word = self.lex_search(query)

            else:
                jq, sent_list, word = [], [], ''

            page = request.GET.get('page')
            sents = self.pages(sent_list, page, 10)
            full_path = rePage.sub('', request.get_full_path())
            return render_to_response('result.html',
                                      {'query': word, 'result': sents, 'path':full_path, 'j':jq},
                                      context_instance=RequestContext(request))

    def pages(self, sent_list, page, num):
        paginator = Paginator(sent_list, num)
        try:
            sents = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            sents = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            sents = paginator.page(paginator.num_pages)
        return sents

    def exact_search(self, word):
        tokens = Token.objects.filter(token__iexact=word)
        jq = []
        sent_list = list(set([token.sent for token in tokens]))
        # sent_list_tagged = [self.bold(word, sent.tagged) for sent in sent_list]
        # print len(sent_list)
        for sent in sent_list:
            jq.append(self.jquery.replace('***', str(sent.id)))
        return jq, sent_list, word

    def lex_search(self, query):
        print query
        words = query.getlist(u'wordform[]')
        grams = query.getlist(u'grammar[]')
        errs = query.getlist(u'errors[]')
        extras = query.getlist(u'additional[]')
        froms = query.getlist(u'from[]')
        tos = query.getlist(u'to[]')
        # <QueryDict: u'wordform[]' u'date1':  u'grammar[]': [u'S', u'A'], [u''], u'format': [u'full'], u'errors[]': u'from[]' u'major':  u'sort_by': [u'wordform'], u'additional[]': u'gender' u'genre'  u'per_page': [u'10'], u'expand': [u'+-1'], u'to[]'}>
        sent_list = []
        jq = []
        for wn in xrange(len(words)):
            word = words[wn].lower().encode('utf-8')
            gram = grams[wn]
            err = errs[wn]
            morphs = Morphology.objects.filter(lem=word)
            tokens = list(set([morph.token for morph in morphs]))
            sent_list += list(set([token.sent for token in tokens]))
        for sent in sent_list:
            jq.append(self.jquery.replace('***', str(sent.id)))
        word=' '.join(query.getlist(u'wordform[]'))
        return jq, sent_list, word

# todo write subcorpus selection
class Subcorpus(Index):
    genres = [
        ('genre', 'курсовая', 'genre_course', "SC_GENRE_COURSE"),
        ('genre', 'эссе', 'genre_essay', "SC_GENRE_ESSAY"),
        ('genre', 'абзацы', 'genre_paragraphs', "SC_GENRE_PARAGRAPHS"),
        ('genre', 'аннотация', 'genre_annotation', "SC_GENRE_ANNOTATION"),
        ('genre', 'реферат', 'genre_retelling', "SC_GENRE_RETELLING"),
        ('genre', 'автобиография', 'genre_autobiography', "SC_GENRE_AUTOBIOGRAPHY"),
        ('genre', 'семестровая работа', 'genre_semwork', "SC_GENRE_SEMWORK"),
        ('genre', 'диплом', 'genre_diploma', "SC_GENRE_DIPLOMA"),
        ('genre', 'ВКР', 'genre_thesis', "SC_GENRE_THESIS"),
        ('genre', 'заявление', 'genre_request', "SC_GENRE_REQUEST"),
        ('genre', 'коммерческое предложение', 'genre_offer', "SC_GENRE_OFFER"),
        ('genre', 'аннотация проекта', 'genre_project', "SC_GENRE_PROJECT")
    ]
    majors = [
        ('major', 'историк', 'major_history', "SC_MAJOR_HISTORY"),
        ('major', 'лингвист', 'major_linguistics', "SC_MAJOR_LINGUISTICS"),
        ('major', 'логист', 'major_logistics', "SC_MAJOR_LOGISTICS"),
        ('major', 'политолог', 'major_politsci', "SC_MAJOR_POLITSCI"),
        ('major', 'социолог', 'major_sociology', "SC_MAJOR_SOCIOLOGY"),
        ('major', 'экономист', 'major_economics', "SC_MAJOR_ECONOMICS"),
        ('major', 'журналист', 'major_journalism', "SC_MAJOR_JOURNALISM"),
        ('major', 'психолог', 'major_psychology', "SC_MAJOR_PSYCHOLOGY"),
        ('major', 'юрист', 'major_law', "SC_MAJOR_LAW"),
        ('major', 'филолог', 'major_philology', "SC_MAJOR_PHILOLOGY"),
        ('major', 'дизайнер', 'major_design', "SC_MAJOR_DESIGN"),
        ('major', 'менеджер', 'major_management', "SC_MAJOR_MANAGEMENT"),
        ('major', 'культуролог', 'major_culture', "SC_MAJOR_CULTURE")
    ]

    def get(self, request, page):
        genre_items = []
        for i in self.genres:
            genre_items.append(Struct(group_name=i[0],
                                value=i[1],
                                id=i[2],
                                title=i[3]))
        major_items = []
        for i in self.majors:
            major_items.append(Struct(group_name=i[0],
                                value=i[1],
                                id=i[2],
                                title=i[3]))
        return render_to_response('subcorpus.html', {'genre_items': genre_items,
                                                     'major_items': major_items},
                                  context_instance=RequestContext(request))


# todo write preferences
class Preferences(Index):

    def get(self, request, page):

        return render_to_response('preferences.html', {}, context_instance=RequestContext(request))

class Statistics(Index):

    def get(self, request, page):
        docs =Document.objects.all().count()
        sents = Sentence.objects.all().count()
        words = Token.objects.all().count()
        annotations = Annotation.objects.all().count()

        return render_to_response('stats.html', {'docs':docs, 'sents':sents, 'words':words, 'annot':annotations},
                                  context_instance=RequestContext(request))
# todo write login \ registration (if needed??)