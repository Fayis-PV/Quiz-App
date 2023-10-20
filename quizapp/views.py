from django.shortcuts import render,redirect
from django.http import HttpResponse
from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import status
from django.core.exceptions import MultipleObjectsReturned
from django.http import Http404
from django.urls import reverse

# Create your views here.


def index(request):
    return HttpResponse('Welcome to Quiz App')


class LevelView(generics.ListAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

class LevelCreateView(generics.CreateAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

class LevelDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

class QuestionView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionCreateView(generics.ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get(self, request):
        # Retrieve levels for the user interface
        levels = Level.objects.all()
        context = {
            'levels': levels
        }
        return render(request, 'question_add.html', context)

    def post(self, request):
        # Deserialize the incoming request data
        question_serializer = QuestionSerializer(data=request.data)
        if question_serializer.is_valid():
            question = question_serializer.save()

            # Create choices for the question
            choices_data = request.data.getlist('choices')
            correct_choice_index = int(request.data.get('correct_choice', -1))

            if correct_choice_index < 0 or correct_choice_index >= len(choices_data):
                # Return an error response when the correct choice index is invalid
                return Response('Please select a valid correct choice index.', status=status.HTTP_400_BAD_REQUEST)

            for i, choice_text in enumerate(choices_data):
                choice = Choice.objects.create(
                    question=question,
                    choice_text=choice_text,
                    is_correct=i == correct_choice_index,
                )
                choice.save()

            # Serialize the created question and return a success response
            response_data = QuestionSerializer(question).data
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            # Return an error response when the serializer is not valid
            return Response(question_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class UserProgressAPI(generics.ListCreateAPIView):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer
    
    def get(self, request):
        # Retrieve a list of all users and levels for the user interface
        users = User.objects.all()
        levels = Level.objects.all()
        context = {
            'users': users,
            'levels': levels
        }
        return render(request, 'user_level_progress.html', context)
    
    def post(self, request):
        user_id = request.data.get('user_id')
        current_level_value = request.data.get('level')
        
        try:
            user = User.objects.get(pk=user_id)
            level = Level.objects.get(value=current_level_value)
            
            user_progress_instance = UserProgress.objects.get(user=user, level=level)
            is_completed = user_progress_instance.check_level_completion()
            
            if is_completed:
                next_level = self.get_next_level(current_level_value)
                self.upgrade_user_level(user_id, next_level)
            
            return Response({"message": "Level updated successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Level.DoesNotExist:
            return Response({"message": "Level not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserProgress.DoesNotExist:
            return Response({"message": "User progress not found."}, status=status.HTTP_404_NOT_FOUND)

    def get_next_level(self, current_level_value):
        # Find the next level based on the current level
        current_level = Level.objects.get(value=current_level_value)
        next_level = Level.objects.filter(value__gt=current_level.value).first()

        return next_level

    def upgrade_user_level(self, user_id, next_level):
        try:
            user_progress = UserProgress.objects.get(user_id=user_id)
            user_progress.level = next_level
            user_progress.save()
        except UserProgress.DoesNotExist:
            return Response({"message": "User progress not found."}, status=status.HTTP_404_NOT_FOUND)

    # The following method should be indented properly, and there is a variable "self.is_completed" that seems undefined.
    def check_level_completion(self, user_id, level_value):
        questions_in_level = Question.objects.filter(level=level_value)

        # Count the correctly answered questions
        correctly_answered_questions = Choice.objects.filter(
            question__in=questions_in_level,
            user_response=True,
            is_correct=True
        ).count()

        # Check if all questions are correctly answered
        if correctly_answered_questions == questions_in_level.count():
            # It's unclear what "self.is_completed" refers to; make sure to define it appropriately.
            self.is_completed = True
            self.save()


#Client Works

class ClientLevelListView(generics.ListAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

class ClientQuestionListView(generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        level_id = self.kwargs['level_id']
        user_id = self.request.user.id  # Replace with your actual user ID or retrieve it dynamically

        # Find questions for the current level that the user hasn't answered
        answered_questions = UserAnswer.objects.filter(user=user_id, question__level_id=level_id)
        questions = Question.objects.filter(level_id=level_id).exclude(id__in=answered_questions.values('question_id'))

        return questions

    def list(self, request, *args, **kwargs):
        try:
            questions = self.get_queryset()
            question = questions.first()

            if not question:
                # Redirect to user progress page if no unanswered questions
                return redirect(f'/user-progress/')

            # Prepare the context for rendering the quiz page
            context = {
                'question': question,
                'user': request.user  # Replace with the actual user data
            }

            # Render the quiz page
            return render(request, 'quiz.html', context)

        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    
class ClientUserProgressView(generics.RetrieveUpdateAPIView):
    queryset = UserProgress.objects.all()
    serializer_class = UserProgressSerializer

    def get(self, request, *args, **kwargs):
        
        user_progress = UserProgress.objects.get(user=request.user)  # Replace with your actual user ID or retrieve it dynamically
        if user_progress.is_completed:
            return Response({"message": "All levels completed."}, status=status.HTTP_200_OK)

        user_answers = UserAnswer.objects.filter(user=request.user, question__level=user_progress.level)

        correct_answers = 0

        # Check if the user's answers are correct for all questions in the level
        for user_answer in user_answers:
            if user_answer.selected_choice.is_correct:
                correct_answers += 1

        if correct_answers >= user_progress.level.correct_answers:
            # Update user progress to the next level
            next_level = Level.objects.filter(value__gt=user_progress.level.value).first()
            # print(next_level)

            if next_level:
                user_progress.level = next_level
                user_progress.completed_questions = 0
                user_progress.total_questions = 0
                user_progress.is_completed = False
                user_progress.save()
                context = {
                    'level' : next_level
                }
                return render(request,'progress.html',context)
            else:
                user_progress.is_completed = True
                user_answers = UserAnswer.objects.filter(user = user_progress.user).delete()
                return Response({"message": "All levels completed."}, status=status.HTTP_200_OK)

        return Response({"message": "Level not completed. Keep trying!"}, status=status.HTTP_200_OK)

class ClientUserAnswerView(generics.ListCreateAPIView):
    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        question = serializer.validated_data['question']
        selected_choice = serializer.validated_data['selected_choice']
        # Check if the selected choice is correct
        is_correct = selected_choice.is_correct

        # Create a UserAnswer instance
        user_answer = UserAnswer(user=user, question=question, selected_choice=selected_choice, is_correct=is_correct)
        user_answer.save()
        # Calculate and update user progress
        try:
            user_progress = UserProgress.objects.get(user=user, level=question.level)
        except UserProgress.DoesNotExist:
            # UserProgress does not exist, create it
            user_progress, created = UserProgress.objects.get_or_create(user=user, level=question.level)
        except MultipleObjectsReturned:
            # Multiple UserProgress objects found, take the first one
            user_progress = UserProgress.objects.filter(user=user, level=question.level).first()
        
        if is_correct:
            user_progress.completed_questions += 1

        user_progress.total_questions += 1
        user_progress.save()

        level_value = question.level.value

        questions = Question.objects.filter(level__value = level_value)
        print(questions)
        if questions.count() == user_progress.total_questions:
            
            return redirect('/user-progress/')
            
        else:
            answered_questions = UserAnswer.objects.filter(user=user, question__level_id=user_answer.question.level.id)
            next_question = Question.objects.filter(level_id=user_answer.question.level.id).exclude(id__in=answered_questions.values('question_id')).first()
            print(next_question)
            context = {
                'user': 1,
                'question' : next_question
                }
            message = "Answer submitted successfully."
            return render(request,'quiz.html',context)
        print(message)

        return Response({"message": message}, status=status.HTTP_201_CREATED)


