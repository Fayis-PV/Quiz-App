from django.db import models
from django.contrib.auth.models import User

class Level(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    value = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    correct_answers = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def total_questions(self):
        return self.question_set.count()

    def valid_correct_answers(self, correct_answers):
        return correct_answers <= self.total_questions()


class Question(models.Model):
    question_text = models.CharField(max_length=4000, null=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, verbose_name='Select a level')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.question_text} ({self.level})'

    def level_id(self):
        return self.level.id


class Choice(models.Model):
    choice_text = models.CharField(max_length=1000)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.choice_text}'

    def question_id(self):
        return self.question.id


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    completed_questions = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} : {self.level.name}'

    def check_level_completion(self):
        questions_in_level = self.level.question_set.all()
        correctly_answered_questions = Choice.objects.filter(
            question__in=questions_in_level,
            user_response=True,
            is_correct=True
        ).count()

        if correctly_answered_questions == questions_in_level.count():
            self.is_completed = True
            self.save()


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name} : {self.question}'
