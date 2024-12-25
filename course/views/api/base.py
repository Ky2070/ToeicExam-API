from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError

class BaseAPIView(APIView):
    service_class = None  # Service class to be used
    
    def get_service(self):
        if not self.service_class:
            raise NotImplementedError("service_class must be defined")
        return self.service_class()

    def handle_exception(self, e):
        if isinstance(e, ValidationError):
            return Response({
                'status': 'error',
                'message': str(e),
                'errors': e.message_dict if hasattr(e, 'message_dict') else None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'status': 'error',
            'message': 'Operation failed',
            'errors': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BaseCreateAPIView(BaseAPIView):
    def post(self, request):
        service = self.get_service()
        
        try:
            data = service.create(
                data=request.data,
                author=request.user
            )
            
            return Response({
                'status': 'success',
                'data': data,
                'message': 'Created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return self.handle_exception(e)

class BaseUpdateAPIView(BaseAPIView):
    def post(self, request, id):
        return self.update(request, id)
        
    def put(self, request, id):
        return self.update(request, id)
    
    def update(self, request, id):
        service = self.get_service()
        
        try:
            data = service.update(
                id=id,
                data=request.data,
                author=request.user
            )
            
            return Response({
                'status': 'success',
                'data': data,
                'message': 'Updated successfully'
            })
            
        except Exception as e:
            return self.handle_exception(e)

class BaseDeleteAPIView(BaseAPIView):
    def delete(self, request, id):
        service = self.get_service()
        
        try:
            service.delete(
                id=id,
                author=request.user
            )
            
            return Response({
                'status': 'success',
                'message': 'Deleted successfully'
            })
            
        except Exception as e:
            return self.handle_exception(e) 