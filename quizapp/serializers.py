from rest_framework import serializers
from .models import *

#Create your quizapp serializers here

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = '__all__'

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['choice_text','is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True,read_only= True)

    class Meta:
        model = Question
        fields = '__all__'


    def to_representation(self, instance):
        representation = super(QuestionSerializer, self).to_representation(instance)
        representation['choices'] = ChoiceSerializer(instance.choice_set.all(), many=True).data
        return representation
    
class UserProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProgress
        fields = '__all__'


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAnswer
        fields = ['question','selected_choice']
