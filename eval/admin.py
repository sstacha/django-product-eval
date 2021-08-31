from django import forms
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.contrib import admin
from django.utils.encoding import force_text
from markdownx.admin import MarkdownxModelAdmin
from import_export import resources
from import_export.admin import ExportMixin

from .models import Project, ProjectVendor, ProjectFunctionality, Evaluation


# trying to override the class to see if I can inherit from a different template
class EvaluationExportMixin(ExportMixin):
    change_list_template = 'admin/eval/evaluation/change_list_export.html'


class EvaluationResource(resources.ModelResource):
    """
    Used by import/export to handle exporting evaluations
    """
    class Meta:
        model = Evaluation
        skip_unchanged = True
        report_skipped = False


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
            return queryset.filter(vendor__project__code=self.value())


@admin.register(ProjectVendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('project', 'name', 'is_active')
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
            'functionality': forms.Textarea(attrs={'cols': 40, 'rows': 10})
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
    search_fields = ['functionality', 'id']
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
    title = 'has percent'
    parameter_name = 'has_percent'

    def lookups(self, request, model_admin):
        return (
            ('no', 'Not Entered'),
            ('0', 'Zero Percent'),
            ('lt60', 'Less than 60%')
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'no':
            return queryset.filter(
                Q(percent_met__isnull=True)
            )
        if value == '0':
            return queryset.filter(
                Q(percent_met__lte=0)
            )
        if value == 'lt60':
            return queryset.filter(percent_met__lt=60)
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
    list_display = ('vendor', 'functionality', 'user', 'percent_met', 'confirmed')
    list_filter = ('vendor', PercentFilter, ProjectFilter, UserFilter)
    search_fields = ['functionality__functionality', ]
    readonly_fields = ['id', 'user', 'vendor', 'functionality']

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
