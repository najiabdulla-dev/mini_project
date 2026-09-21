"""
Custom exception handler and exception classes for Skill Swap.

Ensures all API errors return a consistent JSON format:
{
    "success": false,
    "message": "Human-readable error message",
    "errors": { ... }  // field-level errors, if applicable
}
"""

from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.http import Http404
from django.core.exceptions import ValidationError as DjangoValidationError


def custom_exception_handler(exc, context):
    """
    Custom exception handler that wraps DRF's default handler
    with a consistent error response format.
    """
    # Handle Django ValidationError by converting to DRF exception
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, 'message_dict'):
            detail = exc.message_dict
        else:
            detail = {'non_field_errors': exc.messages}
        from rest_framework.exceptions import ValidationError
        exc = ValidationError(detail=detail)

    response = exception_handler(exc, context)

    if response is not None:
        # Build consistent error format
        error_data = {
            'success': False,
            'status_code': response.status_code,
        }

        if isinstance(response.data, dict):
            # Extract a human-readable message
            if 'detail' in response.data:
                error_data['message'] = str(response.data['detail'])
            else:
                error_data['message'] = 'Validation error'
                error_data['errors'] = response.data
        elif isinstance(response.data, list):
            error_data['message'] = response.data[0] if response.data else 'An error occurred'
        else:
            error_data['message'] = str(response.data)

        response.data = error_data

    return response


# =============================================================================
# Custom Exception Classes
# =============================================================================

class EmailAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'An account with this email already exists.'
    default_code = 'email_exists'





class AccountNotVerifiedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Please verify your email before logging in.'
    default_code = 'not_verified'


class AccountDeactivatedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'Your account has been deactivated. Contact support.'
    default_code = 'account_deactivated'


class PermissionDeniedError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = 'You do not have permission to perform this action.'
    default_code = 'permission_denied'
