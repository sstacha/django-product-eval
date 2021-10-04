from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.safestring import mark_safe
from django.core.validators import MaxValueValidator, MinValueValidator
from tagulous.models import TagField, TagModel, TagTreeModel
from docrootcms.models import ContentMarkdownField


class EvaluationManager(models.Manager):
    """
    Currently using one evaluation manager for all is_active stuff; split if need other specialized methods
    """
    def active(self):
        queryset = self.get_queryset()
        return queryset.filter(is_active=True)


class FunctionalityCategory(TagTreeModel):
    """
    Functionality Categories describe the different categories we want to pick from.
    Ex: content has been tagged with 'user/basic', 'user/advanced' and 'staff/basic'
    """
    class TagMeta:
        force_lowercase = True

    class Meta:
        verbose_name_plural = "Functionality categories"


class PriorityCategory(TagTreeModel):
    """
    Functionality Categories describe the different categories we want to pick from.
    Ex: content has been tagged with 'large/must-have' 'small/must-have' 'large/like-to-have'
    """
    class TagMeta:
        force_lowercase = True

    class Meta:
        verbose_name_plural = "Priority categories"


class Project(models.Model):
    """
    basic project info to group evaluations
    """
    objects = EvaluationManager()
    code = models.CharField(max_length=16)
    name = models.CharField(max_length=255)
    notes = models.CharField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['is_active', '-name']

    def __str__(self):
        return self.name


class ProjectVendor(models.Model):
    """
    vendor info for a project
    """
    objects = EvaluationManager()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    notes = models.TextField(max_length=1200, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['is_active', '-name']

    def __str__(self):
        return self.name


class ProjectFunctionality(models.Model):
    """
    functionality info for a project
    """
    objects = EvaluationManager()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.CharField(max_length=400)
    # priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default=DEFAULT_PRIORITY)
    priorities = TagField(
        to=PriorityCategory,
        blank=True,
        help_text="Splits on commas and spaces;  hierarchy is defined by paths.  "
                  "Ex: 'large/must-have' 'small/must-have' 'large/like-to-have'"
    )
    groups = models.ManyToManyField(Group, blank=True, verbose_name='Applies to', help_text='Leave blank for everyone')
    categories = TagField(
        to=FunctionalityCategory,
        blank=True,
        help_text="Splits on commas and spaces;  hierarchy is defined by paths.  "
                  "Ex: 'user/basic' 'user/advanced' 'staff/basic'"
    )
    order = models.PositiveIntegerField(null=True, blank=True)  
    notes = models.TextField(max_length=500, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['project', 'order', 'description']
        verbose_name = "Project requirement"

    def __str__(self):
        if self.order:
            return f'{str(self.order)}. {str(self.description)}'
        return self.description


class Evaluation(models.Model):
    """
    a user evaluation for a vendor
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(ProjectVendor, on_delete=models.CASCADE)
    functionality = models.ForeignKey(ProjectFunctionality, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(null=True, blank=True, default=None,
                                             validators=[MaxValueValidator(10), MinValueValidator(0)],
                                             help_text="(0-10) How well does this vendor meet this requirement 0-None "
                                                       "to 10-The best.  Remember that 2 vendors can meet a "
                                                       "requirement but one could be more difficult to setup or "
                                                       "maintain.  Your scores should reflect this.")
    confirmed = models.BooleanField(default=False, verbose_name="Confirmed during product demonstration or evaluation")
    notes = ContentMarkdownField(field_image_prefix='evaluation/notes', null=True, blank=True, help_text=mark_safe(
        'Markdown Reference: <a href="https://commonmark.org/help/">https://commonmark.org/help/</a>'))
    
    class Meta:
        ordering = ['vendor', 'functionality', 'user']

    def __str__(self):
        return f'({self.score}) {str(self.functionality)}'