from django import forms
from django.contrib import admin, messages
from django.contrib.admin.actions import delete_selected
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _
from public_project.models import *


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'profile'


class UserAdmin(UserAdmin):
    inlines = (UserProfileInline, )


class ImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'image',)


class WebSourceInline(generic.GenericTabularInline):
    model = WebSource


class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('title', 'short_title', 'title_color', 'sub_title', 'sub_title_color')


class SiteCategoryAdmin(admin.ModelAdmin):
    list_display = ('category',)
    inlines = [
        WebSourceInline,
    ]
    filter_horizontal = ('documents',)


class SearchTagInline(generic.GenericTabularInline):
    model = SearchTag


class CustomMembershipAdminForm(forms.ModelForm):
    
    def clean_to_participant(self):
        to_p = self.cleaned_data['to_participant']
        from_p = self.cleaned_data['from_participant']
        if to_p == from_p:
            raise forms.ValidationError(_("A participant can't have a membership with itself. At least in this system."))
        if to_p.from_memberships.count() > 0:
            raise forms.ValidationError(_("A participant can't belong to a participant which already belongs to another participant. Things would get to complicated."))
        return to_p

class MembershipInline(admin.StackedInline):
    model = Membership
    fk_name = 'from_participant'
    form = CustomMembershipAdminForm

class ParticipantAdmin(admin.ModelAdmin):
    actions = ['delete_selected',]
    list_display = ('name',)
    search_fields = ['name', 'description',]
    inlines = [
        MembershipInline,
        SearchTagInline,
        WebSourceInline,
    ]
    
    def delete_warning_msg(self, request, participant):
        msg  = _('The following associations with "%s" will be deleted') % unicode(participant)  + u': '
        msg += u'%i Events, ' % participant.related_events.count()
        msg += u'%i Documents' % participant.related_documents.count()
        messages.warning(request, msg)

    def delete_view(self, request, object_id, extra_context=None):
        self.delete_warning_msg(request, Participant.objects.get(pk=object_id))
        return super(ParticipantAdmin, self).delete_view(request, object_id, extra_context)
    
    def delete_selected(self, request, queryset):
        for object in queryset.all():
            self.delete_warning_msg(request, object)
        return delete_selected(self, request, queryset)


class CustomProjectPartAdminForm(forms.ModelForm):
    
    def clean_main_project_parts(self):
        data = self.cleaned_data['main_project_parts']
        for main_pp in data.all():
            if main_pp.main_project_parts.count() > 0:
                raise forms.ValidationError(_("A project part can't have a main project part which has a main project part itself. Things would get to complicated."))
        return data


class ProjectPartAdmin(admin.ModelAdmin):
    actions = ['delete_selected',]
    list_display = ('name', 'order',)
    inlines = [
        SearchTagInline,
        WebSourceInline,
    ]
    filter_horizontal = ('main_project_parts',)
    form = CustomProjectPartAdminForm

    def delete_warning_msg(self, request, project_part):
        msg  = _('The following associations with "%s" will be deleted') % unicode(project_part)  + u': '
        msg += u'%i Events, ' % project_part.related_events.count()
        msg += u'%i Documents' % project_part.related_documents.count()
        messages.warning(request, msg)

    def delete_view(self, request, object_id, extra_context=None):
        self.delete_warning_msg(request, ProjectPart.objects.get(pk=object_id))
        return super(ProjectPartAdmin, self).delete_view(request, object_id, extra_context)
    
    def delete_selected(self, request, queryset):
        for object in queryset.all():
            self.delete_warning_msg(request, object)
        return delete_selected(self, request, queryset)


class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'important', 'date')
    filter_horizontal = ('project_parts', 'participants',)
    inlines = [
        SearchTagInline,
        WebSourceInline,
    ]
    list_filter = ('event_type', 'important',)
    search_fields = ['title', 'description',]


class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'answered',)
    inlines = [
        WebSourceInline,
    ]
    filter_horizontal = ('project_parts', 'participants', 'events', 'documents')


class ProjectGoalInline(admin.StackedInline):
    model = ProjectGoal


class ProjectGoalGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'event')
    inlines = [
        ProjectGoalInline,
    ]


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'document', 'date',)
    search_fields = ['title', 'description',]
    filter_horizontal = ('participants', 'project_parts', 'events',)
    exclude = ('pdf_images_generated',)


class PageAdmin(admin.ModelAdmin):
    list_display = ('document', 'number')


class SearchTagCacheEntryAdmin(admin.ModelAdmin):
    list_display = ('tag', 'document', 'num_results')


class ResearchRequestRelationInline(admin.StackedInline):
    model = ResearchRequestRelation


class ResearchRequestAdmin(admin.ModelAdmin):
    list_display = ('nr', 'title', 'open', 'date_added',)
    list_filter = ('open',)
    search_fields = ['title',]
    inlines = [
        ResearchRequestRelationInline,
    ]


class CommentRelationInline(admin.StackedInline):
    model = CommentRelation


class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'published', 'published_by', 'date_added',)
    list_filter = ('published','published_by',)
    search_fields = ['username', 'comment',]
    exclude = ('activation_hash',)
    inlines = [
        CommentRelationInline,
    ]

class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'content_object', 'content_type', 'object_id', 'date')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(SiteConfig, SiteConfigAdmin)
admin.site.register(SiteCategory, SiteCategoryAdmin)
admin.site.register(Participant, ParticipantAdmin)
admin.site.register(ProjectPart, ProjectPartAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(ProjectGoalGroup, ProjectGoalGroupAdmin)
admin.site.register(Document, DocumentAdmin)
#admin.site.register(SearchTagCacheEntry, SearchTagCacheEntryAdmin)
#admin.site.register(Page, PageAdmin)
admin.site.register(ResearchRequest, ResearchRequestAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(ActivityLog, ActivityLogAdmin)