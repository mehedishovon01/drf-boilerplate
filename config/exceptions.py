from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, NotFound
from rest_framework import status
from django.utils.translation import gettext_lazy as _
from django.http import Http404


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and response.status_code > 400:
        if type(exc) is Http404:
            response_code = NotFound().get_codes()
            response.data['code'] = response_code
        else:
            response_code = exc.get_codes()
            response.data['code'] = response_code
    return response


class ServiceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _(
        'Service temporarily unavailable, please try again later.')
    default_code = 'service_unavailable'


class AlreadyProcessed(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('The request has already been processed.')
    default_code = 'already_processed'


class AlreadyExists(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = _('An entity with your request already exists.')
    default_code = 'already_exists'
