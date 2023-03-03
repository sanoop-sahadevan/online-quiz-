from rest_framework import serializers

from .models import Quiz, Question, Choice, User, QuizResult


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'], validated_data['email'], validated_data['password'])

        return user      


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['options', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['text', 'choices']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(source = 'question',many=True)

    class Meta:
        model = Quiz
        fields = ['title', 'topic', 'difficulty','questions']

    def create(self, validated_data):
        questions_data = validated_data.pop('question')
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            choices_data = question_data.pop('choices')
            question = Question.objects.create(quiz=quiz, **question_data)

            for choice_data in choices_data:
                Choice.objects.create(question=question, **choice_data)

        return quiz


class UserprofileSerializer(serializers.ModelSerializer):
    quiz= QuizSerializer(source = 'user',many =True)
    
    
    class Meta:
        model = User
        fields = ['username','email','quiz']


class QuizResultSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)

    class Meta:
        model = QuizResult
        fields = ['quiz_title','score','quiz_id']



class UpdateModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
       
        fields = [ 'username', 'email']










   






