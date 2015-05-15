# coding=utf-8
from django.db import models
from django.contrib.auth.models import User

import uuid
import json
from utils import *
regSpan= re.compile('<span class="token.*?</span>', flags=re.U | re.DOTALL)

class Document(models.Model):
    """A document being annotated"""
    owner = models.ForeignKey(User, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    title = models.CharField(max_length=64, db_index=True, null=True, blank=True, editable=True)
    body = models.TextField()  # HTML
    # todo probably should delete this field and create a special form in admin
    author = models.CharField(max_length=50)

    # optional fields - need them for meta in CoRST
    date1 = models.IntegerField(null=True, blank=True)
    date2 = models.IntegerField(null=True, blank=True)
    genre = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True, choices=((u'ж', u'женский'), (u'м', u'мужской')))
    course = models.CharField(max_length=50, null=True, blank=True)
    language_background = models.CharField(max_length=50, null=True, blank=True)
    text_type = models.CharField(max_length=50, null=True, blank=True)
    level = models.CharField(max_length=50, null=True, blank=True)
    annotation = models.CharField(max_length=50, null=True, blank=True)
    student_code = models.IntegerField(null=True, blank=True)
    time_limit = models.CharField(max_length=50, null=True, blank=True)

    # needed for general corpus statictics
    words = models.IntegerField(editable=False, null=True, blank=True)
    sentences = models.IntegerField(editable=False, null=True, blank=True)
    date_displayed = models.CharField(editable=False, max_length=10, null=True, blank=True)

    # needed for annotation statistics
    annotated = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)

    def __unicode__(self):
        return self.title + ', ' + self.author

    def save(self, **kwargs):
        handle_sents = False
        if self.id is None:
            handle_sents = True
        if self.date1 and self.date2:
            if self.date1 == self.date2:
                self.date_displayed = self.date1
            else:
                self.date_displayed = str(self.date1) + '-' + str(self.date2)
        genre = self.genre if self.genre else ' -genre'
        course = self.course if self.course else '-course '
        text_type = self.major if self.text_type else ' -texttype '
        self.title = genre + ' (' + text_type + ', ' + course + ')'     # filename or id
        super(Document, self).save()
        # todo how to close body change after a Document has been created?
        # we don't want people to change the texts after it has been parsed and loaded to the DB
        # but we want them to be able to edit meta
        if handle_sents:
            pass
            self.handle_sentences()

    def handle_sentences(self):
        self.words, text = mystem(self.body)
        self.sentences = len(text)
        for sent_id in range(len(text)):
            sent, created = Sentence.objects.get_or_create(text=text[sent_id].text, doc_id=self, num=sent_id+1)
            words = text[sent_id].words
            stagged = []
            for i_word in range(len(words)):
                sent_pos = ''
                if i_word == 0: sent_pos = 'bos'
                elif i_word == len(words) - 1: sent_pos = 'eos'
                token, created = Token.objects.get_or_create(doc=self, sent=sent, num=i_word+1,
                                                             sent_pos=sent_pos,
                                                             token=words[i_word].wf,
                                                             punctr=words[i_word].pr,
                                                             punctl=words[i_word].pl)
                analyses = words[i_word].anas
                all_ana = words[i_word].tooltip
                for ana in analyses:
                    lem = ana[0]
                    bastard = False
                    if 'qual="' in lem:
                        lem = lem.split('"')[0]
                        bastard = True
                    lex, gram = ana[1].split('=')
                    if bastard:
                        lex = 'bastard,' + lex
                    Morphology.objects.get_or_create(token=token, lem=lem,
                                                     lex=lex, gram=gram)
                word = ' <span class="token" title="' + all_ana + '">' + \
                       token.punctl + token.token + token.punctr + '</span> '
                # todo rethink this piece
                # Tim says storing html is fine, since you never change it later and they do it in EANC, for example
                # but still, there must be a better implementation - absolutely not urgent
                stagged.append(word)

            sent.tagged = ''.join(stagged)
            sent.correct = sent.tagged
            sent.save()


class Sentence(models.Model):
    text = models.CharField(max_length=1000)
    doc_id = models.ForeignKey(Document)
    num = models.IntegerField()
    tagged = models.CharField(max_length=1000000)  # stores the html-piece
    correct = models.CharField(max_length=1000000)

    def __unicode__(self):
        return self.text


class Annotation(models.Model):
    # taken from Django-Annotator-Store
    owner = models.ForeignKey(User, db_index=True, blank=True, null=True)
    document = models.ForeignKey(Sentence, db_index=True)
    guid = models.CharField(max_length=64, unique=True, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True, db_index=True)
    data = models.TextField()  # all other annotation data as JSON
    tag = models.CharField(max_length=100, null=True, blank=True)

    def set_guid(self):
        self.guid = str(uuid.uuid4())

    def can_edit(self, user):
        if self.owner and self.owner != user and (not user or not user.has_perm('annotator.change_annotation')):
            return False
        return True

    def save(self, **kwargs):
        super(Annotation, self).save()
        sent, tagged = self.document, self.document.correct
        d = json.loads(self.data)
        corr, start, end = d['corrs'], \
                           int(d["ranges"][0]['start'].replace('/span[', '').replace(']', '')), \
                           int(d["ranges"][0]['start'].replace('/span[', '').replace(']', ''))
        tagged = regSpan.findall(tagged)
        corr = '<span class="token green" title="">' + corr + '</span>'
        if start == end:
            tagged[start-1] = corr
        else:
            tagged[start-1:end] = corr

        sent.correct = ' '.join(tagged)
        sent.save()

    def as_json(self, user=None):
        d = {"id": self.guid,
             "document": self.document_id,
             "created": self.created.isoformat(),
             "updated": self.updated.isoformat(),
             "readonly": not self.can_edit(user),
             }

        d.update(json.loads(self.data))

        return d

    def update_from_json(self, new_data):
        d = json.loads(self.data)

        for k, v in new_data.items():  # Skip special fields that we maintain and are not editable.
            if k in ('document', 'id', 'created', 'updated', 'readonly'):
                continue

                # Put other fields into the data object.
            d[k] = v

        self.data = json.dumps(d)
        self.tag = ', '.join(d["tags"])

    @staticmethod
    def as_list(qs=None, user=None):
        if qs is None:
            qs = Annotation.objects.all()
        return [
            obj.as_json(user=user)
            for obj in qs.order_by('-updated')
        ]

    def __unicode__(self):
        d = json.loads(self.data)["quote"]
        return self.document.doc_id.title + ' - ' + d


class Token(models.Model):
    token = models.CharField(max_length=100)
    doc = models.ForeignKey(Document)
    sent = models.ForeignKey(Sentence)
    num = models.IntegerField()
    punctl = models.CharField(max_length=10)
    punctr = models.CharField(max_length=10)
    sent_pos = models.CharField(max_length=10)
    corr = models.BooleanField(default=False)

    def __unicode__(self):
        return self.token


class Morphology(models.Model):
    # stupid class name, will change it someday
    token = models.ForeignKey(Token)
    lem = models.CharField(max_length=100)
    lex = models.CharField(max_length=100)
    gram = models.CharField(max_length=100)

    def __unicode__(self):
        return self.lem + ' ' + self.lex + ' ' + self.gram