# -*- coding: utf-8 -*-

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET', 'POST'])
def contact_callback(request):
    pass