from django import forms
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.contrib import admin
from django.utils.encoding import force_text
from markdownx.admin import MarkdownxModelAdmin
from import_export import resources
from import_export.admin import ExportMixin
from import_export.fields import Field
from django.utils.html import format_html, linebreaks

from .models import Project, ProjectVendor, ProjectFunctionality, Evaluation


# trying to override the class to see if I can inherit from a different template
class EvaluationExportMixin(ExportMixin):
    change_list_template = 'admin/eval/evaluation/change_list_export.html'


class EvaluationResource(resources.ModelResource):
    """
    Used by import/export to handle exporting evaluations
    """
    # login = Field()

    class Meta:
        model = Evaluation
        # fields = ('id', 'login', 'user__username')
        skip_unchanged = True
        report_skipped = False
        fields = (
            'id',
            # 'user',
            'user__username',
            # 'vendor',
            'vendor__name',
            # 'functionality',
            'functionality__description',
            'score',
            'confirmed',
            'functionality__priorities',
            'notes',
        )
        export_order = (
            'id',
            # 'user',
            'user__username',
            # 'vendor',
            'vendor__name',
            # 'functionality',
            'functionality__description',
            'score',
            'confirmed',
            'functionality__priorities',
            'notes',
        )

    # def dehydrate_login(self, evaluation):
    #     return evaluation.user.username



@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ['name', 'id']
    readonly_fields = ['id']


class ProjectFilter(admin.SimpleListFilter):
    title = 'project'
    parameter_name = 'project'

    def lookups(self, request, model_admin):
        qs_proj = Project.objects.active()
        list_proj = []
        for proj in qs_proj:
            list_proj.append(
                (proj.code, proj.name)
            )
        return (
            sorted(list_proj, key=lambda tp: tp[1])
        )

    def queryset(self, request, queryset):
        if self.value():
            if queryset.model._meta.object_name == 'ProjectVendor' or queryset.model._meta.object_name == \
                    'ProjectFunctionality':
                return queryset.filter(project__code=self.value())
            else:
                return queryset.filter(vendor__project__code=self.value())


@admin.register(ProjectVendor)
class VendorAdmin(admin.ModelAdmin):
    ordering = ('project', 'name', '-is_active')
    list_display = ('name', 'is_active', 'project')
    list_filter = (ProjectFilter, 'is_active')
    search_fields = ['name', 'id']
    readonly_fields = ['id']


class ProjectFunctionalityForm(forms.ModelForm):
    """
    overriding the charfield widget to show as a textarea for better visibility
    """
    class Meta:
        model = ProjectFunctionality
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'cols': 40, 'rows': 10})
        }


class AppliesToFilter(admin.SimpleListFilter):
    title = 'applies to'
    parameter_name = 'applies_to'

    def lookups(self, request, model_admin):
        qs_groups = Group.objects.filter(name__icontains=":").exclude(name__iendswith=":Members")
        list_groups = []
        for grp in qs_groups:
            list_groups.append(
                (grp.id, grp.name)
            )
        return (
            sorted(list_groups, key=lambda tp: tp[1])
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(groups__id=self.value())


@admin.register(ProjectFunctionality)
class ProjectFunctionalityAdmin(admin.ModelAdmin):
    form = ProjectFunctionalityForm
    list_filter = (ProjectFilter, AppliesToFilter)
    search_fields = ['description', 'id']
    readonly_fields = ['id']
    filter_horizontal = ['groups']

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "groups":
            # project_prefix = self.model.project.name + ":"
            kwargs["queryset"] = Group.objects.filter(name__icontains=":").exclude(name__iendswith=":Members")
            # kwargs["queryset"] = Group.objects.exclude(name__in=group_exclusions)
            # if len(Groups.objects.filter(name__startswith=project_prefix) >1):
            #     kwargs["queryset"].filter(name__startswith=project_prefix)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class PercentFilter(admin.SimpleListFilter):
    title = 'has score'
    parameter_name = 'has_score'

    def lookups(self, request, model_admin):
        return (
            ('no', 'Not Entered'),
            ('0', 'Zero Percent'),
            ('lt6', 'Less than 6')
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'no':
            return queryset.filter(
                Q(score__isnull=True)
            )
        if value == '0':
            return queryset.filter(
                Q(score__lte=0)
            )
        if value == 'lt6':
            return queryset.filter(score__lt=6)
        return queryset


class UserFilter(admin.SimpleListFilter):
    title = 'user'
    parameter_name = 'user'

    def choices(self, changelist):
        """Copied from source code to remove the "All" Option"""
        yield {
            'selected': self.value() is None,
            'query_string': changelist.get_query_string({}, [self.parameter_name]),
            'display': 'Me',
        }
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == force_text(lookup),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}, []),
                'display': title,
            }

    def lookups(self, request, model_admin):
        qs_users = User.objects.exclude(id=request.user.id)
        list_users = [(0, ' Everyone')]
        for usr in qs_users:
            list_users.append(
                (usr.id, usr.username)
            )
        return (
            sorted(list_users, key=lambda tp: tp[1])
        )

    def queryset(self, request, queryset):
        if self.value() and self.value() != '0':
            return queryset.filter(user__id=self.value())
        return queryset


@admin.register(Evaluation)
class EvaluationAdmin(EvaluationExportMixin, MarkdownxModelAdmin):
    fields = ('functionality', 'score', 'confirmed', 'notes', 'user', 'vendor', 'id')
    list_display = ('vendor', 'formatted_functionality', 'priorities', 'categories', 'user', 'score', 'custom_confirmed')
    list_filter = ('vendor', PercentFilter, ProjectFilter, UserFilter)
    search_fields = ['functionality__description', ]
    readonly_fields = ['id', 'user', 'vendor', 'functionality']

    def custom_confirmed(self, obj):
        return obj.confirmed
    custom_confirmed.short_description = 'confirmed'
    custom_confirmed.boolean = True

    def formatted_functionality(self, obj):
        if obj.functionality and obj.functionality.description:
            return format_html(linebreaks(obj.functionality.description))
        return obj.functionality.description
    formatted_functionality.short_description = 'functionality'

    def priorities(self, obj):
        return format_html("<br>".join([str(p) for p in obj.functionality.priorities.all()]))

    def categories(self, obj):
        return format_html("<br>".join([str(c) for c in obj.functionality.categories.all()]))

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        """
        override the queryset to return only records selected by the filtered user or ourselves
        :param request: the request for this call
        :return: the queryset to display on admin screen
        """
        qs = super().get_queryset(request)
        # if we specified another user let normal filtering happen
        if request.GET.get('user') or request.POST.get('user'):
            return qs
        # if we are on an edit page we still want to show the record
        if '/change/' in request.path:
            return qs
        # otherwise filter to the current user
        return qs.filter(user=request.user)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     """
    #     override the functionality field list to only show what is applicable to this user
    #     :param db_field: the field the form is on
    #     :param request: the request object for this call
    #     :param kwargs: the params so we can return the modified queryset
    #     :return: super instance with our qs change possibly
    #     """
    #     if db_field.name == "functionality":
    #         # get the current user
    #         user = request.user
    #         if not user.is_superuser:
    #             groups = list(user.groups.all())
    #             # only display if our groups match
    #             kwargs["queryset"] = ProjectFunctionality.objects.filter(groups__in=groups)
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


def export_evaluations():
    return EvaluationResource.export()
