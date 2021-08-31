# import re
# from django.conf import settings
# from django.http import JsonResponse
# from datetime import datetime
from eval.models import Evaluation

# static context definition
context = {'title': 'SPE Evaluations', 'description': 'SPE Evaluation Application'}


# dynamic context return
# NOTE: don't forget to use .update to add/replace instead of = which will ignore static definition
def get_context(request):
    evaluations = Evaluation.objects.all()
    context.update({'evaluations': evaluations})
    return context


# web service definitions
# NOTE: if not defined or commented will return 405-method not supported if called
#   if no data file or no web service methods defined returns 404-not found
# BEST PRACTICE: GET does not update only reads and returns data
# def GET(request):
#     ctx = get_context(request)
#     now = datetime.now()
#     ctx['freshness_date'] = str(now)
#     return JsonResponse(ctx, safe=False)
#
#
# BEST PRACTICE: POST inserts/updates a single record and returns data/response (form post encoded body)
# def POST(request):
#     pass
#
#
# BEST PRACTICE: PUT inserts/updates record(s) and returns data/response (various body formats like json/xml etc)
# def PUT(request):
#     pass
#
#
# BEST PRACTICE: DELETE deletes (maybe soft delete like marking record deleted) record and returns data/response
#   best practice is to pass just unique identifier not a lot complete data set
# def DELETE(request):
#     pass
