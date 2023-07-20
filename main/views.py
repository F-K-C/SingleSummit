# Create your views here.

# from main.serilaizer import PlateFormConstDataSerializer
#
#
# class PlatFormConstDataView(BaseAPIView):
#     authentication_classes = ()
#     permission_classes = ()
#
#     def get(self, request):
#         try:
#             data = PlatformConstantData.objects.all()
#             return self.send_response(
#                 success=True,
#                 code=status.HTTP_200_OK,
#                 payload=PlateFormConstDataSerializer(data,many=True).data,
#                 description="Constant Data"
#             )
#         except Exception as e:
#             return self.send_response(
#                 description=str(e)
#             )
