from django.core.management.base import BaseCommand
from argparse import RawTextHelpFormatter
from eval.models import *
from eval.utils import generate_evaluations

from django.contrib.auth.models import User
# from django.db import connection


class Command(BaseCommand):
    project_code = None

    help = """
        usage: ./manage.py evaluations [option]
        --------------------------------------
        usage: ./manage.py evaluations generate project_code
        example: ./manage.py evaluations generate auth

        options
        --------
        generate - generates evaluations for the specified project
        
        NOTE: errors if project code is not found
    """

    def create_parser(self, *args, **kwargs):
        parser = super(Command, self).create_parser(*args, **kwargs)
        parser.formatter_class = RawTextHelpFormatter
        return parser

    def add_arguments(self, parser):
        parser.add_argument('option', nargs='+', type=str)

    def handle(self, *args, **options):
        params = options['option']
        if "generate" in params and len(params) >= 2:
            self.project_code = params[1]
            self.stdout.write(self.style.SUCCESS(f'project: {str(self.project_code)}'))
            self.stdout.write(self.style.SUCCESS('%s' % generate_evaluations(self.project_code)))
        else:
            self.stdout.write(self.style.SUCCESS(self.help))
