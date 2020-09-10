# from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from api.models import Image
from api.serializers import ImageUploadSerializer
from plugins.detector import Detection
from plugins.engines import send


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


class ImageUploadView(APIView):
    def post(self, request):
        img = request.data.get("file")
        url = request.META.get("HTTP_URL")
        key = request.META.get("HTTP_API_KEY")
        if img is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        format_detector = Detection()
        detection_result = format_detector.detect(img)
        recognition_result = send(img, url, key)
        print(recognition_result)

        serializer = ImageUploadSerializer(data=detection_result, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
