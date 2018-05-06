from utils.functions import log
from rest_framework.response import Response
from rest_framework import status as s

class SuccessResponse(Response):

    def __init__(self, data=None):
        status = s.HTTP_200_OK
        super(SuccessResponse, self).__init__(data=data, status=status)


class CreatedResponse(Response):

    def __init__(self, data=None):
        status = s.HTTP_201_CREATED
        super(CreatedResponse, self).__init__(data=data, status=status)


class ErrorResponse(Response):

    def __init__(self, data=None):
        status = s.HTTP_400_BAD_REQUEST
        super(ErrorResponse, self).__init__(data=data, status=status)
