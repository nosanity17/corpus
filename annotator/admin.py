from django.contrib import admin
from annotator.models import Document, Annotation, Sentence, Token, Morphology
from django.contrib.admin import AdminSite
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

class LearnerCorpusAdminSite(AdminSite):
    site_header = 'Russian Heritage Corpus'
    site_title = 'Admin'
    index_title = 'RULEC'


class DocumentAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['owner', 'body']}),
        ('Author', {'fields': [('author', 'gender', 'course', 'language_background'), ('student_code', 'level')]}),
        ('Date', {'fields': [('date1', 'date2')]}),
        ('Text', {'fields': [('genre', 'text_type', 'annotation', 'time_limit')]}),
        ('Autocompletion', {'fields': [('annotated', 'checked')], 'classes': [('collapse')]}),
    ]

    list_display = ('title', 'author', 'date_displayed', 'created')
    # list_filter = ['author', 'gender', 'major']


class AnnotationAdmin(admin.ModelAdmin):
    readonly_fields = ('annotated_doc',)
    list_display = ('annotated_doc', 'tag', 'owner', 'updated', 'created')

    def annotated_doc(self, instance):
        return instance.document.doc_id.title


class MorphAdmin(admin.ModelAdmin):
    list_display = ('token', 'lem', 'lex', 'gram')


class MorphInline(admin.TabularInline):
    model = Morphology
    extra = 0


class TokenAdmin(admin.ModelAdmin):
    readonly_fields = ('sent_num',)
    fieldsets = [
        (None,               {'fields': ['token', 'doc', 'sent']}),
        ('Token data', {'fields': [('num', 'punctl', 'punctr', 'sent_pos')]}),
    ]

    list_display = ('token', 'sent_num', 'num', 'doc')
    inlines = [MorphInline]

    def sent_num(self, instance):
        return instance.sent.num


learner_admin = LearnerCorpusAdminSite(name='admin')
learner_admin.register(Document, DocumentAdmin)
learner_admin.register(Annotation, AnnotationAdmin)
learner_admin.register(Sentence)
learner_admin.register(Token, TokenAdmin)
# learner_admin.register(Morphology, MorphAdmin)
learner_admin.register(User, UserAdmin)
learner_admin.register(Group, GroupAdmin)
