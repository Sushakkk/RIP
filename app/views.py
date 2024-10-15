from django.contrib.auth import authenticate
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .minio import *
from .jwt_helper import *
from .permissions import *
from .serializers import *
from .utils import identity_user









#  ex-----------------------------------------Деятельности------------------------------------------------



# # Определяем параметры для Swagger
# category_param = openapi.Parameter(
#     'category',  # имя параметра
#     openapi.IN_QUERY,  # указываем, что это параметр в URL
#     type=openapi.TYPE_STRING,  # тип данных
#     required=False,  # параметр не обязателен
#     description='Категория для фильтрации активностей'  # описание параметра
# )

# @swagger_auto_schema(method='get', manual_parameters=[category_param])



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_activities(request):
    user = identity_user(request)

    if user is None:
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    # Получаем категорию из параметров запроса
    category = request.query_params.get('category')

    if category:
        activities = Activities.objects.filter(category__iexact=category)
    else:
        activities = Activities.objects.all()

    serializer = ActivitiesSerializer(activities, many=True)

    self_employed_drafts = SelfEmployed.objects.filter(user_id=user.id, status='draft')

    if not self_employed_drafts.exists():
        return Response({"message": "У пользователя нет черновиков самозанятых."}, status=status.HTTP_404_NOT_FOUND)

    first_draft = self_employed_drafts.first()

    activity_count = SelfEmployedActivities.objects.filter(self_employed=first_draft).count()
    
    return Response({
        "activities": serializer.data,
        "self_employed_id": first_draft.id,
        "activity_count": activity_count
    }, status=status.HTTP_200_OK)




@api_view(["GET"])
def get_activity_by_id(request, activity_id):
    """
    Получает активность по ID. Если активность не найдена — возвращает 404.
    """
    if not Activities.objects.filter(pk=activity_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    activity = Activities.objects.get(pk=activity_id)
    serializer = ActivitiesSerializer(activity, many=False)

    return Response(serializer.data)









@api_view(["PUT"])
@permission_classes([IsModerator])
def update_activity(request, activity_id):
    try:
        activity = Activities.objects.get(pk=activity_id)
    except Activities.DoesNotExist:
        return Response({"error": "Активность не найдена."}, status=status.HTTP_404_NOT_FOUND)

    pic = request.FILES.get('pic')

    if pic:
        pic_result = add_pic_to_activity(activity, pic)
        if 'error' in pic_result.data:
            return pic_result

    serializer = ActivitiesSerializer(activity, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes([IsModerator])
def create_activity(request):
    """
    Создает новую деятельность и загружает изображение в MinIO.
    """

    title = request.data.get('title')
    description = request.data.get('description')
    category = request.data.get('category')
    pic = request.FILES.get('pic')  # Получаем файл изображения

    
    # Создаем объект активности
    activity = Activities.objects.create(
        title=title,
        description=description,
        category=category
    )

    # Добавляем изображение через MinIO
    response = add_pic_to_activity(activity, pic)

    # Сериализация и возврат обновленных данных
    serializer = ActivitiesSerializer(activity)
    return Response(serializer.data, status=status.HTTP_200_OK)






@api_view(["DELETE"])
@permission_classes([IsModerator])
def delete_activity(request, activity_id):
    """
    Удаляет активность по ID, устанавливая статус 5 (удален). Если активность не найдена — возвращает 404.
    """
    try:
        activity = Activities.objects.get(pk=activity_id)
    except Activities.DoesNotExist:
        return Response({"error": "Активность не найдена."}, status=status.HTTP_404_NOT_FOUND)

    # Удаляем изображение из MinIO, если оно существует
    if activity.img_url:
        remove_result = remove_pic_from_activity(activity)  # Вызываем функцию для удаления изображения
        if 'error' in remove_result:
            return Response(remove_result, status=status.HTTP_400_BAD_REQUEST)  # Возвращаем ошибку, если удаление не удалось

    # Устанавливаем статус активности на 5 (удален)
    activity.status = 'deleted'
    activity.save()

    # Сериализация и возврат обновленных данных
    serializer = ActivitiesSerializer(activity)
    return Response(serializer.data, status=status.HTTP_200_OK)



# def get_draft_self_employed(request):
#     user = identity_user(request)

#     if user is None:
#         return None

#     self_employed = SelfEmployed.objects.filter(user=user).filter(status='draft').first()

#     return self_employed

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def add_activity(request, activity_id):
    
    # Проверяем, существует ли активность
    if not Activities.objects.filter(pk=activity_id).exists():
        return Response({"error": "Активность не найдена."}, status=status.HTTP_404_NOT_FOUND)

    activity = Activities.objects.get(pk=activity_id)
    
    
    
    # draft_self_employed = get_draft_self_employed(request)
    
    user = identity_user(request)

    if user is None:
        return None

    self_employed = SelfEmployed.objects.filter(user=user).filter(status='draft').first()


    # Проверяем, существует ли уже самозанятый для данного пользователя
    self_employed, created = SelfEmployed.objects.get_or_create(
        user=user,
        defaults={
            'status': 'draft',  # Устанавливаем статус на черновик
            'created_date': timezone.now()
        }
    )

    

    # Проверяем, существует ли связь между активностью и самозанятым
    if SelfEmployedActivities.objects.filter(activity=activity, self_employed=self_employed).exists():
        return Response({"error": "Эта активность уже добавлена к самозанятому."}, status=status.HTTP_400_BAD_REQUEST)

    # Добавляем активность к самозанятому
    SelfEmployedActivities.objects.create(activity=activity, self_employed=self_employed)
      
    
    # Получаем связанные активности через модель SelfEmployedActivities
    self_employed_activities = SelfEmployedActivities.objects.filter(self_employed=self_employed)
    
    # Создаем список активностей с полем importance
    activities_with_importance = []
    for self_employed_activity in self_employed_activities:
        activity = self_employed_activity.activity  # Получаем связанную активность
        activity_data = ActivitiesSerializer(activity).data  # Сериализуем активность
        
        # Добавляем поле importance из SelfEmployedActivities
        activity_data['importance'] = self_employed_activity.importance  
        
        activities_with_importance.append(activity_data)



    return Response({
        "message": "Активность успешно добавлена к самозанятому.",
        "self_employed_id": self_employed.id,
        "user_name": user.username,
        "status": self_employed.status,
        "activities":activities_with_importance,  # Добавляем информацию о добавленной активности
    }, status=status.HTTP_200_OK)




@api_view(["POST"])
@permission_classes([IsModerator])
def update_activity_image(request, activity_id):
    """
    Обновляет данные активности по ID. Если активность не найдена — возвращает 404.
    """
    try:
        activity = Activities.objects.get(pk=activity_id)
    except Activities.DoesNotExist:
        return Response({"error": "Активность не найдена."}, status=status.HTTP_404_NOT_FOUND)

 
    pic = request.FILES.get('pic')  # Получаем файл изображения

    # Если есть новое изображение, обновляем его
    if pic:
        pic_result = add_pic_to_activity(activity, pic)  # Добавляем изображение через MinIO
        if 'error' in pic_result.data:  # Проверка на наличие ошибок
            return pic_result  # Возвращаем ошибку, если загрузка не удалась

    # Сохраняем изменения
    activity.save()

    # Сериализация и возврат обновленных данных
    serializer = ActivitiesSerializer(activity)
    return Response(serializer.data, status=status.HTTP_200_OK)



# ex-----------------------------------------Пользователь------------------------------------------------


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    access_token = create_access_token(user.id)

    serializer = UserSerializer(user)

    response = Response(serializer.data, status=status.HTTP_201_CREATED)

    response.set_cookie('access_token', access_token, httponly=True)

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    access_token = create_access_token(user.id)

    serializer = UserSerializer(user)

    response = Response(serializer.data, status=status.HTTP_201_CREATED)

    response.set_cookie('access_token', access_token, httponly=True)

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    access_token = get_access_token(request)

    if access_token not in cache:
        cache.set(access_token, settings.JWT["ACCESS_TOKEN_LIFETIME"])

    return Response(status=status.HTTP_200_OK)


@swagger_auto_schema(method='PUT', request_body=UserSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)



#  ex-----------------------------------------Самозанятые------------------------------------------------




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_self_employed(request):
    # Инициализация переменной self_employed
    self_employed = SelfEmployed.objects.all()  # Получение всех самозанятых

    # Получаем статус из запроса
    status_value = request.data.get('status')

    # Исключаем записи со статусами 'deleted' и 'draft'
    if status_value in ['deleted', 'draft']:
        return Response({"error": "Невозможно получить данные с этим статусом"}, status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)
    if not user.is_staff:
        self_employed = self_employed.filter(user=user)  # Фильтруем по пользователю, если не администратор

    if status_value:
        # Если передан массив статусов
        if isinstance(status_value, list):
            self_employed = self_employed.filter(status__in=status_value)
        else:
            # Если передан один статус
            self_employed = self_employed.filter(status=status_value)

    # Исключаем удаленные и черновики, если статусы не переданы
    self_employed = self_employed.exclude(status__in=['deleted', 'draft']).order_by('created_date')

    serializer = SelfEmployedSerializer(self_employed, many=True)

    resp = {
        "self_employed": serializer.data,
    }

    return Response(resp)





@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_self_employed_by_id(request, self_employed_id):
    user = identity_user(request)
 
    # Проверяем, существует ли самозанятый с данным ID
    if not SelfEmployed.objects.filter(pk=self_employed_id, user=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Получаем самозанятого по ID
    self_employed = SelfEmployed.objects.get(pk=self_employed_id)
    serializer = SelfEmployedSerializer(self_employed, many=False)

    # Получаем связанные активности через модель SelfEmployedActivities
    self_employed_activities = SelfEmployedActivities.objects.filter(self_employed=self_employed)
    
    # Создаем список активностей с полем importance
    activities_with_importance = []
    for self_employed_activity in self_employed_activities:
        activity = self_employed_activity.activity  # Получаем связанную активность
        activity_data = ActivitiesSerializer(activity).data  # Сериализуем активность
        
        # Добавляем поле importance из SelfEmployedActivities
        activity_data['importance'] = self_employed_activity.importance  
        
        activities_with_importance.append(activity_data)

    return Response({
        'self_employed': serializer.data,
        'activities': activities_with_importance  # Возвращаем активности с полем importance
    })

    
  

@swagger_auto_schema(method='put', request_body=SelfEmployedSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_self_employed(request, self_employed_id):
    user = identity_user(request)

    try:
        self_employed = SelfEmployed.objects.get(pk=self_employed_id, user=user)
    except SelfEmployed.DoesNotExist:
        return Response({"error": "Self-employed not found"}, status=status.HTTP_404_NOT_FOUND)

    # Получаем данные из запроса
    data = request.data

    # Обновляем поля, если они присутствуют в теле запроса
    if 'completion_date' in data:
        try:
            completion_date = parse_datetime(data['completion_date'])
            if completion_date:
                self_employed.completion_date = completion_date
            else:
                return Response({"error": "Invalid completion_date format"}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError:
            return Response({"error": "Invalid completion_date"}, status=status.HTTP_400_BAD_REQUEST)

    if 'moderator' in data:
        try:
            moderator = User.objects.get(pk=data['moderator'])
            self_employed.moderator = moderator
        except User.DoesNotExist:
            return Response({"error": "Moderator not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
    if 'fio' in data:
        self_employed.fio = data['fio']  # Обновляем поле FIO из запроса
        

    # Сохранение изменений
    self_employed.save()

    # Сериализуем обновленные данные
    serializer = SelfEmployedSerializer(self_employed)

    return Response({
        'self_employed': serializer.data,
    }, status=status.HTTP_200_OK)





@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_by_creator(request, self_employed_id):
    user = identity_user(request)
    try:
        self_employed = SelfEmployed.objects.get(pk=self_employed_id, user=user)
    except SelfEmployed.DoesNotExist:
        return Response({"error": "Самозанятый не найден"}, status=status.HTTP_404_NOT_FOUND)
    
    moderator_id = request.GET.get('moderator') or request.data.get('moderator') or 3

    # Проверяем, что ID пользователя и модератора были переданы
    try:
        moderator = User.objects.get(pk=moderator_id) if moderator_id else None
    except User.DoesNotExist:
        return Response({"error": "модератор не найден"}, status=status.HTTP_404_NOT_FOUND)

   
    if moderator:
        self_employed.moderator = moderator

    # Проверка обязательных полей у самозанятого
    if  not self_employed.moderator:
        return Response({"error": "Поле 'moderator' обязательно"}, status=status.HTTP_400_BAD_REQUEST)

    # Получаем новое значение статуса из запроса (GET или POST)
    status_value = request.GET.get('status') or request.data.get('status') 
    if not status_value:
        return Response({"error": "Поле 'status' обязательно"}, status=status.HTTP_400_BAD_REQUEST)

    # Проверяем, не завершена ли уже заявка
    if self_employed.status == 'completed':
        return Response({"error": "Заявка уже завершена"}, status=status.HTTP_400_BAD_REQUEST)

    # Обновляем статус
    self_employed.status = status_value

    # Установка текущей даты завершения, если статус "completed"
    if status_value == 'completed':
        self_employed.completion_date = timezone.now()

    # Сохраняем изменения
    self_employed.save()

    # Сериализация и возврат данных
    serializer = SelfEmployedSerializer(self_employed)
    return Response(serializer.data, status=status.HTTP_200_OK)







@api_view(["PUT"])
@permission_classes([IsModerator])
def update_by_moderator(request, self_employed_id):
 

    try:
        self_employed = SelfEmployed.objects.get(pk=self_employed_id)
    except SelfEmployed.DoesNotExist:
        return Response({"error": "Самозанятый не найден"}, status=status.HTTP_404_NOT_FOUND)

    # Проверка обязательных полей
    required_fields = ['status']
    for field in required_fields:
        if field not in request.GET:
            return Response({"error": f"Поле '{field}' обязательно"}, status=status.HTTP_400_BAD_REQUEST)
        
 
    if self_employed.status =='completed':
        return Response({"error": f"Заявка уже завершена"}, status=status.HTTP_400_BAD_REQUEST)    

   
    # Обновление полей
    self_employed.moderator = identity_user(request)
    self_employed.status = request.GET['status']
    
    
    # Установка текущей даты завершения, если статус "завершено" или "отклонено"
    if self_employed.status in ["completed", "rejected"]:
        self_employed.completion_date = timezone.now()

    # Сохраняем изменения
    self_employed.save()

    # Сериализация и возврат обновленных данных
    serializer = SelfEmployedSerializer(self_employed, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)




@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_self_employed(request, self_employed_id):
 
    user = identity_user(request)
    if not SelfEmployed.objects.filter(pk=self_employed_id, user=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    self_employed = SelfEmployed.objects.get(pk=self_employed_id)
    self_employed.status = 'deleted'
    self_employed.save()
    serializer = SelfEmployedSerializer(self_employed, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)











# ex---------------------------------M-M--------------------------------------------------------




@swagger_auto_schema(method='PUT', request_body=SelfEmployedActivitiesSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_importance(request, s_e_id, a_id):
    
    self_employed_id = s_e_id
    activity_id= a_id
    user = identity_user(request)
    
    if not SelfEmployed.objects.get(pk=self_employed_id, user=user) :
        return Response({"error": "Self-employed not found"}, status=status.HTTP_404_NOT_FOUND)

   
    # Проверяем, существует ли связь между самозанятым и активностью
    if not SelfEmployedActivities.objects.filter(self_employed_id=self_employed_id, activity_id=activity_id).exists():
        return Response({"error": "Связь между самозанятым и активностью не найдена."}, status=status.HTTP_404_NOT_FOUND)

    # Получаем связь
    item = SelfEmployedActivities.objects.get(self_employed_id=self_employed_id, activity_id=activity_id)

    # Получаем новое значение importance из запроса
    new_importance = request.data.get('importance')

    # Проверяем наличие значения
    if new_importance is None:
        return Response({"error": "Поле 'importance' обязательно."}, status=status.HTTP_400_BAD_REQUEST)

    # Если новое значение importance = True, сбросим importance для всех других активностей самозанятого
    if new_importance:
        SelfEmployedActivities.objects.filter(self_employed_id=self_employed_id).update(importance=False)

    # Обновляем значение поля
    item.importance = new_importance
    item.save()

    

    # Получаем самозанятого по ID
    self_employed = SelfEmployed.objects.get(pk=self_employed_id)
    serializer = SelfEmployedSerializer(self_employed, many=False)

    # Получаем связанные активности через модель SelfEmployedActivities
    self_employed_activities = SelfEmployedActivities.objects.filter(self_employed=self_employed)
    
    # Создаем список активностей с полем importance
    activities_with_importance = []
    for self_employed_activity in self_employed_activities:
        activity = self_employed_activity.activity  # Получаем связанную активность
        activity_data = ActivitiesSerializer(activity).data  # Сериализуем активность
        
        # Добавляем поле importance из SelfEmployedActivities
        activity_data['importance'] = self_employed_activity.importance  
        
        activities_with_importance.append(activity_data)

    return Response({
        "message": "Поле importance успешно обновлено.",
        'self_employed': serializer.data,
        'activities': activities_with_importance  # Возвращаем активности с полем importance
    })
   





@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_self_employed_activity(request, s_e_id, a_id):
    self_employed_id = s_e_id
    activity_id= a_id
    
    user = identity_user(request)
    if not SelfEmployed.objects.get(pk=self_employed_id, user=user) :
        return Response({"error": "Self-employed not found"}, status=status.HTTP_404_NOT_FOUND)
    
    
    item = SelfEmployedActivities.objects.filter(self_employed_id=self_employed_id, activity_id=activity_id).first()

    if not item:
        return Response({"error": "Связь между самозанятым и активностью не найдена."}, status=status.HTTP_404_NOT_FOUND)

    # Удаляем связь
    item.delete()

    return Response({"message": "Связь успешно удалена."}, status=status.HTTP_204_NO_CONTENT)







#  ex----------------------------------------Функции-------------------------------------------------
# def get_draft_activity():
#     """
#     Возвращает первую запись из таблицы Activities со статусом 'active'.
#     """
#     return Activities.objects.filter(status='active').first()


# def get_user():
#     """
#     Возвращает первого обычного пользователя (не суперпользователя).
#     """
#     return User.objects.filter(is_superuser=False).first()


# def get_moderator():
#     """
#     Возвращает первого суперпользователя.
#     """
#     return User.objects.filter(is_superuser=True).first()






