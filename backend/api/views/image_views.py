# from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from api.models import Image
from api.serializers import ImageSerializer
from plugins.detector import Detection


# class ImageViewSet(ModelViewSet):
#     queryset = Image.objects.all()
#     serializer_class = ImageSerializer

#     def post(self, request, *args, **kwargs):
#         img = request.data.get("file")
#         print(request.data)
#         if img is None:
#             return Response(status=status.HTTP_400_BAD_REQUEST)

#         format_detector = Detection()
#         data = format_detector.detect(img)
#         print(data)
#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ImageView(APIView):
    def post(self, request):
        img = request.data.get("file")

        if img is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        format_detector = Detection()
        data = format_detector.detect(img)
        serializer = ImageSerializer(data=data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
