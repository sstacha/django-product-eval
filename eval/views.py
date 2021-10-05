from django.shortcuts import HttpResponse
from .utils import generate_evaluations
from .admin import EvaluationResource


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


def generate_missing_evaluations(request, product_code):
    """
    generates any missing evals for a project and returns status output to include on a dialog
    :param request: request object
    :param product_code: the product_code to generate for
    :return: list of records created or empty string
    """
    try:
        return_msg = generate_evaluations(product_code)
    except Exception as ex:
        return HttpResponse(str(ex), status=500)
    return HttpResponse(return_msg)


def export_evaluations(request):
    """
    exports all evaluations from the admin screen button
    :param request: request object
    :return: list of records created or empty string
    """
    try:
        dataset = EvaluationResource().export()
        response = HttpResponse(dataset.csv, content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename="evaluations.csv"'
        return response
    except Exception as ex:
        return HttpResponse(str(ex), status=500)
