from rest_framework import status
from rest_framework.decorators import api_view

from .models import Status
from .serializers import StatusSerializer
from .utils import errorcall, succescall

# Create your views here.


@api_view(["GET"])
def get_all_statuses(request):
    """
    API general para obtener todos los estados configurados en el sistema.
    """
    try:
        statuses = Status.objects.all()
        serializer = StatusSerializer(statuses, many=True)
        return succescall(serializer.data, "Estados obtenidos correctamente")
    except Exception as e:
        return errorcall(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
