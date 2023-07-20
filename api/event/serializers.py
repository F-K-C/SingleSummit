from rest_framework import serializers

from api.event.models import Event
from api.users.models import User
from main.serilaizer import DynamicFieldsModelSerializer


class EventSerializer(DynamicFieldsModelSerializer):
    id = serializers.IntegerField(read_only=True)
    participants = serializers.SerializerMethodField(read_only=True)
    grade = serializers.SerializerMethodField(read_only=True)
    first_name = serializers.CharField(read_only=True, source="user.first_name")
    last_name = serializers.CharField(read_only=True, source="user.last_name")

    class Meta:
        model = Event
        exclude = ('modified_on', 'modified_by', 'created_on')

    def get_participants(self,obj):
        return [d[0] for d in obj.event_participant.filter().values_list("user_id")]

    def get_grade(self,obj):
        try:
            user_id = self.context.get('user_id')
            return obj.event_participant.get(user_id=user_id).grade
        except:
            return None