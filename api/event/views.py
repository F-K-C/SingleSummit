import json
from datetime import datetime

from django.conf import settings
from django.db.models import Q, Count, F, Avg
from django.urls import reverse
from rest_framework import status

from rest_framework import status

from api.event.models import Event, EventParticipant
from api.event.serializers import EventSerializer
from api.permissions import IsAuthenticated, IsClientAuthenticated, IsGETorClientAuthenticated
from api.users.models import User, Role, AccessLevel
from api.users.serializers import UserSerializer
from api.views import BaseAPIView
from single_summit_app.send_email import send_email_sendgrid_template
from single_summit_app.utils import parse_email


class EventAPIView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = (IsClientAuthenticated,)

    def get(self, request, pk=None):
        """
        :param request:
        :param pk: to get event instance
        :return: response of required event listings
        """
        try:
            is_calendar = request.query_params.get('is_calendar', '')
            if is_calendar:
                data = Event.objects.filter().values("id", 'name', 'date')
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    payload=data,
                    description="Event Data",
                    count=0
                )
            if pk:
                data = Event.objects.get(id=pk)
                serializer = EventSerializer(data)
                count = 1
            else:
                limit = int(request.query_params.get("limit", 10))
                offset = int(request.query_params.get("offset", 0))
                event_data_type = int(request.query_params.get("event_data_type", 0))
                query_object = Q()
                data = Event.objects
                if event_data_type == 1:
                    query_object &= Q(event_participant__user_id=request.user.id, date__lte=datetime.now())
                elif event_data_type == 2:
                    query_object &= Q(user_id=request.user.id)
                else:
                    query_object &= Q(date__gte=datetime.now())
                    # data = data.exclude(user_id=request.user.id)
                data = data.filter(query_object).order_by("-date")
                serializer = EventSerializer(data[offset: limit + offset], many=True, context={
                    "user_id": request.user.id
                })
                count = data.count()
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                payload=serializer.data,
                description="Event Data",
                count=count
            )

        except Event.DoesNotExist as e:
            return self.send_response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description=str(e)
            )
        except Exception as e:
            return self.send_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description=str(e)
            )

    def post(self, request, pk=None):
        try:
            serializer = EventSerializer(data=request.data)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                validated_data['user'] = request.user
                serializer.save(**validated_data)
                return self.send_response(
                    success=True,
                    code=f'200',
                    status_code=status.HTTP_200_OK,
                    description='Evento criado com sucesso',
                )
            else:
                return self.send_response(
                    success=False,
                    code='422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors
                )
        except Exception as e:
            if hasattr(e.__cause__, 'pgcode') and e.__cause__.pgcode == '23505':
                return self.send_response(
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description="Um usuário com esse email já existe no sistema."
                )
            return self.send_response(
                code=f'500',
                description=e
            )

    def put(self, request, pk=None):
        try:
            instance = Event.objects.get(id=pk)
            serializer = EventSerializer(data=request.data, instance=instance)
            if serializer.is_valid():
                serializer.save()
                return self.send_response(
                    success=True,
                    code=f'200',
                    status_code=status.HTTP_200_OK,
                    description='Evento atualizado com sucesso',
                )
            else:
                return self.send_response(
                    success=False,
                    code='422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description=serializer.errors
                )
        except Exception as e:
            if hasattr(e.__cause__, 'pgcode') and e.__cause__.pgcode == '23505':
                return self.send_response(
                    code=f'422',
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description="Um usuário com esse email já existe no sistema."
                )
            return self.send_response(
                code=f'500',
                description=e
            )


class EventDeleteAPIView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = (IsClientAuthenticated,)

    def get(self, request, pk=None):
        """
        :param request:
        :param pk: to get event instance
        :return: response of required event listings
        """
        try:
            instance = Event.objects.get(id=pk)
            if instance.user_id == request.user.id:
                instance.delete()
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    description="Event Deleted Successfully",
                )
            else:
                return self.send_response(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    description="Sorry, you are not the creator. You cannot delete this event.",
                )
        except Event.DoesNotExist as e:
            return self.send_response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event does not exist in our system."
            )
        except Exception as e:
            return self.send_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description=str(e)
            )


class EventJoinAPIView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = (IsClientAuthenticated,)

    def get(self, request, event_id=None, user_id=None):
        """
        :param request:
        :param pk: to get event instance
        :return: response of required event listings
        """
        try:
            instance = EventParticipant.objects.get_or_create(
                event_id=event_id,
                user_id=user_id
            )
            if instance[1]:
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    description="Muito obrigado por participar! Nos vemos no evento!",
                )
            else:
                instance[0].delete()
                return self.send_response(
                    success=True,
                    status_code=status.HTTP_200_OK,
                    description="Que pena que você não está participando do evento",
                )
        except EventParticipant.DoesNotExist as e:
            return self.send_response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event does not exist in our system."
            )
        except Exception as e:
            return self.send_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description=str(e)
            )


class EventRatingAPIView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = (IsClientAuthenticated,)

    def get(self, request, event_id=None, rating=None):
        """
        :param request:
        :param pk: to get event instance
        :return: response of required event listings
        """
        try:
            instance = EventParticipant.objects.get(
                event_id=event_id,
                user_id=request.user.id
            )
            instance.grade = rating
            instance.save()
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                description="Evento avaliado com sucesso",
            )
        except EventParticipant.DoesNotExist as e:
            return self.send_response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event does not exist in our system."
            )
        except Exception as e:
            return self.send_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description=str(e)
            )


class EventSendInvitationAPIView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = (IsClientAuthenticated,)

    def post(self, request, event_id=None, rating=None):
        """
        :param request:
        :param pk: to get event instance
        :return: response of required event listings
        """
        try:
            email_list = request.data.get("email_list").split(",")
            event = Event.objects.get(id=request.data.get("id"))
            send_email_sendgrid_template(
                from_email=settings.CONTACT_US_EMAIL,
                to_email=email_list,
                subject="Invitation",
                data={
                    "first_name": event.user.first_name,
                    "last_name": event.user.last_name,
                    "url": f"{settings.WEB_URL}{reverse('visitor-event-detail', kwargs={'pk': event.id})}"
                },
                template=settings.EVENT_INVITATION
            )
            return self.send_response(
                success=True,
                status_code=status.HTTP_200_OK,
                description="Convite enviado com sucesso",
            )
        except Event.DoesNotExist as e:
            return self.send_response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event does not exist in our system."
            )
        except Exception as e:
            return self.send_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description=str(e)
            )


class EventStatisticsAPIView(BaseAPIView):
    """
    API View for Login Super Admin and Admin
    """
    authentication_classes = ()
    permission_classes = (IsClientAuthenticated,)

    def get(self, request, event_id=None, user_id=None):
        """
        :param request:
        :param pk: to get event instance
        :return: response of required event listings
        """
        try:
            city = request.query_params.get('city', "")
            type = request.query_params.get('type', "")
            query_object = Q()
            query_object_participant = Q()
            if city:
                query_object &= Q(city__exact=city)
                query_object_participant &= Q(event__city__exact=city)
            if type:
                query_object &= Q(type__exact=type)
                query_object_participant &= Q(event__type__exact=type)
            if request.user.role.code == AccessLevel.CLIENT_CODE:
                query_object &= Q(user_id=request.user.id)
                query_object_participant &= Q(user_id=request.user.id)

            city_data = Event.objects.filter(
                query_object,
            ).annotate(
                count=Count("city"),
                data_name=F('city'),
            ).values("data_name","count")
            type_data = Event.objects.filter(
                query_object
            ).annotate(
                count=Count("type"),
                data_name=F('type')
            ).values("data_name","count")

            event_data = Event.objects.filter(
                query_object
            ).values('date__month').annotate(
                count=Count("id"),
                data_name=F('date__month'),
            ).values("data_name", "count")

            event_price = Event.objects.filter(
                query_object
            ).annotate(
                count=F("price"),
                data_name=F('name'),
            ).values("data_name", "count")

            event_data_grade = EventParticipant.objects.filter(
                query_object_participant
            ).values('event__name').annotate(
                count=Avg("grade"),
                data_name=F('event__name'),
            ).values("data_name", "count")

            event_participant_data = EventParticipant.objects.filter(
                query_object_participant,
            ).values('event__date__month').annotate(
                count=Count("id"),
                data_name=F('event__date__month'),
            ).values("data_name", "count")

            return self.send_response(
                success=True,
                payload={
                    "city_data": city_data,
                    "type_data": type_data,
                    "event_data": event_data,
                    "event_participant_data": event_participant_data,
                    "event_data_grade": event_data_grade,
                    "event_price": event_price
                },
                status_code=status.HTTP_200_OK,
                description="Thank you very much for joining. See you at the venue",
            )
        except EventParticipant.DoesNotExist as e:
            return self.send_response(
                code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Event does not exist in our system."
            )
        except Exception as e:
            return self.send_response(
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description=str(e)
            )
