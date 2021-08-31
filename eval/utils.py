from eval.models import *
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError, ImproperlyConfigured


def get_project_groups(user, project_code):
    return user.groups.filter(name__istartswith=project_code).exclude(name__iexact=project_code+":Members")
    # return Group.objects.filter(name__istartswith=project_code).exclude(name__iexact=project_code+":Members")


def generate_evaluations(project_code):
    """
    generate missing evaluations for the project for all people/vendors with null evaluations
    """
    # get the users for this project.  NOTE: requires group named <project_code>:Members
    group_name = f"{project_code}:Members"
    return_msg = ""

    try:
        project = Project.objects.get(code__iexact=project_code)
    except ObjectDoesNotExist:
        raise ObjectDoesNotExist(f"Project was not found for project code [{project_code}]! Pass a valid project code")
    if not project.is_active:
        raise ValidationError(f"Project [{project.code}] is inactive! Activate to generate evaluations")
    members_group = Group.objects.filter(name__iexact=group_name).all()
    if not members_group:
        raise ImproperlyConfigured(f"Group [{group_name}] does not exist!  You need to create and add members.")
    members = members_group[0].user_set.all()
    if not members:
        raise ValidationError(f"No members defined for group [{group_name}]!  Set some up to generate evaluations")
    vendors = ProjectVendor.objects.active().filter(project=project)
    if not vendors:
        raise ValidationError(
            f"No vendors defined with project [{project.code}]!  Set up a vendor to generate evaluations")
    requirements = ProjectFunctionality.objects.active().filter(project=project)

    # loop over all members/vendors and generate records if needed
    for member in members:
        # filter evaluations if this user is in a project group other than project_code:Members
        member_filter_groups = get_project_groups(member, project_code)
        if member_filter_groups:
            # member_requirements = requirements.filter(groups__in=member_groups)
            member_requirements = requirements.filter(groups__in=member_filter_groups)
        else:
            member_requirements = requirements
        for member_requirement in member_requirements:
            for vendor in vendors:
                evaluation = Evaluation.objects.filter(user=member, vendor=vendor, functionality=member_requirement)
                if not evaluation:
                    Evaluation.objects.create(
                        user=member,
                        vendor=vendor,
                        functionality=member_requirement,
                    )
                    return_msg += f"     created evaluation [{member.username}], {vendor}, {member_requirement}\n"
    return_msg += "done!\n"
    return return_msg
