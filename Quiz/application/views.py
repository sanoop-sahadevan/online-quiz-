from rest_framework import generics
from rest_framework.generics import CreateAPIView,ListAPIView,RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated,AllowAny,IsAdminUser
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import QuizSerializer,RegisterSerializer,UsersSerializer,UserprofileSerializer,QuizResultSerializer, UpdateModelSerializer
from application.models import Quiz,Question,QuizResult,Choice
from django.contrib.auth.models import User
from rest_framework import filters
from django.db.models import Avg
from rest_framework_simplejwt.tokens import RefreshToken


from rest_framework_simplejwt.views import TokenObtainPairView

#JWT token authentication

class ObtainTokenPairWithCookieView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = response.data['access']
        print(token)
        response.set_cookie('jwt', token, max_age=3600, httponly=True)
        return response

# Logout

# class LogoutView(APIView):
#     def post(self, request, *args, **kwargs):
#         response = JsonResponse({'message': 'Successfully logged out'}, status=200)
#         response.delete_cookie('jwt')
#         return response



class TokenBlacklistView(APIView):
    def post(self, request):
        token = RefreshToken(request.data.get('refresh'))
        token.blacklist()
        return Response("Success")


 #Admin user management   
    


class AdminUserListAPIView(generics.ListAPIView):     #adminUSerlistview Add_On feature
    permission_classes = [IsAuthenticated,IsAdminUser] 
    serializer_class = UsersSerializer
    queryset = User.objects.all()

    




class AdminCreateView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = {
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
        return Response(response_data)


#Admin update,delete,retrive user data
class AdminUpdateView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UpdateModelSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminUser]





# User registeration

class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_data = {
            "message": "User created successfully",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }
        return Response(response_data)


#user profile apiview

class UserProfileAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserprofileSerializer

    def get(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        quizzes = Quiz.objects.filter(created_by=user)    #filter quiz created by user
        quiz_serializer = QuizSerializer(quizzes, many=True)   
        data = {
            'user' : serializer.data,                      
        }

        return Response(data)


# Quiz creation

class QuizCreateAPIView(generics.CreateAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

        return Response(serializer.data)

#Quiz listing

class QuizListAPIView(generics.ListAPIView):
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]                 # authentication_classes = [TokenAuthentication]
    filter_backends = [filters.SearchFilter]
    search_fields = ['topic','created_at','difficulty']


    def get_queryset(self):
        user = self.request.user
        print(user)
        if user.is_superuser: 
            queryset=Quiz.objects.all()
        else:
            queryset=Quiz.objects.filter(created_by=user)
        return queryset
        
    




#Quiz taking

class QuizTakingAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizSerializer

    def post(self,request,quiz_id):
        quiz = Quiz.objects.get(pk = quiz_id)
        user = request.user

        if QuizResult.objects.filter(user=user, quiz=quiz).exists():  #check if the quiz is already taken 
            return Response({'message': 'Quiz has already been taken by the user'})

        total_questions = quiz.question.count()                        #count of  total questions
        correct_answers = 0                                            #initialize correct_answer = 0
        for question in quiz.question.all():                           # iterate through all questions
            answer = request.data.get(str(question.id))
            if not answer :                                            
                return Response({'message' : f'answer is missing for question { question.id }'})
            check_answers = Choice.objects.filter(question_id=question.id)  #filter out choices with question_id
            choice_num = 1
            for check_answer in check_answers:                              #Get the correct choice_num          
                if check_answer.is_correct == True:
                    break
                choice_num += 1

            if choice_num == int(answer) :
                correct_answers += 1

        score = int((correct_answers/total_questions)*100)        
        
        quiz_result = QuizResult.objects.create(user = user, quiz = quiz, score = score)


        
        return Response({'message' : f'Your score is { score }'})



#Quiz result

class QuizResultAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuizResultSerializer

    def get(self, request):
        user = request.user
        quiz_results = QuizResult.objects.filter(user = user)
        serializer = QuizResultSerializer(quiz_results, many=True)
        data = {
            'user' : serializer,
            
        }

        return Response(serializer.data)



#quiz analytics

class QuizAnalyticsAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    # serializer_class = QuizResultSerializer

    def get(self, request):
        user = request.user
        if request.user.is_superuser:          #if user is admin
            quizzes = Quiz.objects.all()
        else:
            quizzes = Quiz.objects.filter(created_by = user)    #if not admin
            print(quizzes)
        analytics = []

        for quiz in quizzes:

            quiz_results = QuizResult.objects.filter(quiz = quiz)
            print(quiz_results)
            number_of_quiztaken = quiz_results.count()
            
            number_of_users_passed = quiz_results.filter(score__gte  =60). values('user').distinct().count()
            if number_of_quiztaken > 0:
                passrate = number_of_users_passed / number_of_quiztaken *100
                average_quiz_score = quiz_results.aggregate(Avg('score'))['score__avg']
            else:
                passrate = 0
                average_quiz_score = 0
            
            analytics.append({
            'quiz_id ' : quiz.id,
            'quiz_title ' : quiz.title,
            'quiz_taken' : number_of_quiztaken,
            'quiz_average' : average_quiz_score,
            'quiz_percentage':passrate,


            })
    
        return Response(analytics)
    

             
   





















 




    


    








        

    
  















       
        
        
