"""
Provides Django view functions to manually control the atomic transaction
sessions managed by `AtomicSession`. These views are typically used in
end-to-end testing scenarios to explicitly start and roll back transactions
between test steps.
"""

from http import HTTPStatus


from django.http import HttpResponse, HttpRequest

from atomicserver.atomic import AtomicSession


def begin(request: HttpRequest) -> HttpResponse:
    """
    View to begin atomic transactions for all configured databases.
    """
    AtomicSession.enter_atomics()
    return HttpResponse(status=HTTPStatus.NO_CONTENT)


def setup(request: HttpRequest) -> HttpResponse:
    """
    View to setup the database for the test.
    """
    # TODO: Implement your fixtures here
    return HttpResponse(status=HTTPStatus.OK)


def rollback(request: HttpRequest) -> HttpResponse:
    """
    View to roll back the current atomic transaction.
    """
    AtomicSession.rollback_atomics()
    return HttpResponse(status=HTTPStatus.NO_CONTENT)
