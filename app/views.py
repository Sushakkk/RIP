import requests
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .minio import *
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate





from .models import *
from .serializers import *

#  ex----------------------------------------Функции-------------------------------------------------
def get_draft_activity():
    """
    Возвращает первую запись из таблицы Activities со статусом 'active'.
    """
    return Activities.objects.filter(status='active').first()


def get_user():
    """
    Возвращает первого обычного пользователя (не суперпользователя).
    """
    return User.objects.filter(is_superuser=False).first()


def get_moderator():
    """
    Возвращает первого суперпользователя.
    """
    return User.objects.filter(is_superuser=True).first()



#  ex-----------------------------------------Самозанятые------------------------------------------------




# Исключаем записи со статусом 'deleted' и 'draft'
@api_view(["GET"])
def search_self_employed(request):
    status_value = request.data.get('status')
    
   # Исключаем записи со статусами 'deleted' и 'draft'
    if status_value in ['deleted', 'draft']:
        return Response({"error": "Невозможно получить данные с этим статусом"}, status=status.HTTP_404_NOT_FOUND)
    
        

    if status_value:
        # Если передан массив статусов
        if isinstance(status_value, list):
            self_employed = SelfEmployed.objects.filter(status__in=status_value).order_by('created_date')
        else:
            # Если передан один статус
            self_employed = SelfEmployed.objects.filter(status=status_value).order_by('created_date')
    else:
        # Если статусы не переданы, исключаем удаленные и черновики
        self_employed = SelfEmployed.objects.exclude(status__in=['deleted', 'draft']).order_by('created_date')

    serializer = SelfEmployedSerializer(self_employed, many=True)

    resp = {
        "self_employed": serializer.data,
    }

    return Response(resp)




@api_view(["GET"])
def get_self_employed_by_id(request, self_employed_id):
    # Проверяем, существует ли самозанятый с данным ID
    if not SelfEmployed.objects.filter(pk=self_employed_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Получаем самозанятого по ID
    self_employed = SelfEmployed.objects.get(pk=self_employed_id)
    serializer = SelfEmployedSerializer(self_employed, many=False)

    # Получаем связанные активности через модель SelfEmployedActivities
    activities = Activities.objects.filter(self_employed_activities__self_employed=self_employed)
    activities_serializer = ActivitiesSerializer(activities, many=True)

    return Response({
        'self_employed': serializer.data,
        'activities': activities_serializer.data
    })
    
    
  

from django.utils.dateparse import parse_datetime

@api_view(["PUT"])
def update_self_employed(request, self_employed_id):
    """
    Обновляет данные самозанятого по ID. Если самозанятый не найден — возвращает 404.
    """
    # Проверяем, существует ли самозанятый с данным ID
    try:
        self_employed = SelfEmployed.objects.get(pk=self_employed_id)
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

    # Сохранение изменений
    self_employed.save()

    # Сериализуем обновленные данные
    serializer = SelfEmployedSerializer(self_employed)

    return Response({
        'self_employed': serializer.data,
    }, status=status.HTTP_200_OK)





@api_view(["PUT"])
def update_by_creator(request, self_employed_id):
    """
    Обновляет данные самозанятого создателем. Проверяет обязательные поля.
    Дата завершения автоматически устанавливается текущей.
    """
    try:
        self_employed = SelfEmployed.objects.get(pk=self_employed_id)
    except SelfEmployed.DoesNotExist:
        return Response({"error": "Самозанятый не найден"}, status=status.HTTP_404_NOT_FOUND)

    # Проверка обязательных полей
    required_fields = ['user_id', 'status']
    for field in required_fields:
        if field not in request.GET:
            return Response({"error": f"Поле '{field}' обязательно"}, status=status.HTTP_400_BAD_REQUEST)

    # Получаем user_id и status
    user_id = request.GET.get('user_id')
    status_value = request.GET.get('status')
    
    
    if self_employed.status =='completed':
        return Response({"error": f"Заявка уже завершена"}, status=status.HTTP_400_BAD_REQUEST)
            

    # Получаем объект пользователя по user_id
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

    # Обновляем поля
    self_employed.user = user
    self_employed.status = status_value

    # Установка текущей даты завершения
    self_employed.completion_date = timezone.now()

    # Сохраняем изменения
    self_employed.save()

    # Сериализация и возврат данных
    serializer = SelfEmployedSerializer(self_employed, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)





@api_view(["PUT"])
def update_by_moderator(request, self_employed_id):
    """
    Обновляет данные самозанятого модератором. 
    При завершении или отклонении заявки устанавливается модератор и дата завершения.
    """
    # Проверка существования записи
    try:
        self_employed = SelfEmployed.objects.get(pk=self_employed_id)
    except SelfEmployed.DoesNotExist:
        return Response({"error": "Самозанятый не найден"}, status=status.HTTP_404_NOT_FOUND)

    # Проверка обязательных полей
    required_fields = ['moderator_id', 'status']
    for field in required_fields:
        if field not in request.GET:
            return Response({"error": f"Поле '{field}' обязательно"}, status=status.HTTP_400_BAD_REQUEST)
        
 
    if self_employed.status =='completed':
        return Response({"error": f"Заявка уже завершена"}, status=status.HTTP_400_BAD_REQUEST)    

    # Получаем модератора по ID
    try:
        moderator = User.objects.get(pk=request.GET['moderator_id'])
    except User.DoesNotExist:
        return Response({"error": "Модератор не найден"}, status=status.HTTP_404_NOT_FOUND)

    # Обновление полей
    self_employed.moderator = moderator  # Присваиваем объект User
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
def delete_self_employed(request, self_employed_id):
    """
    Удаляет самозанятого по ID, устанавливая статус 2 (удален). Если не найден — возвращает 404.
    """
    if not SelfEmployed.objects.filter(pk=self_employed_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    self_employed = SelfEmployed.objects.get(pk=self_employed_id)
    self_employed.status = 'deleted'
    self_employed.save()
    serializer = SelfEmployedSerializer(self_employed, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)





#  ex-----------------------------------------Деятельности------------------------------------------------




@api_view(["GET"])
def get_draft_activities_list_for_user(request, user_id):
    """
    Возвращает список деятельностей с id самозанятого-черновика для указанного пользователя, отфильтрованных по дате и статусу.
    """
    # Проверяем, существует ли пользователь
    if not User.objects.filter(pk=user_id).exists():
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    # Находим всех самозанятых пользователя в статусе "черновик", отсортированных по дате создания
    self_employed_drafts = SelfEmployed.objects.filter(user_id=user_id, status='draft').order_by('created_date')

    if not self_employed_drafts.exists():
        return Response({"error": "Самозанятые в статусе черновика не найдены."}, status=status.HTTP_404_NOT_FOUND)

    # Получаем id первого самозанятого черновика (по самой ранней дате)
    first_draft = self_employed_drafts.first()

    # Получаем активности, связанные с самозанятыми-черновиками
    activities = Activities.objects.filter(self_employed_activities__self_employed_id=first_draft.id)

    # Сериализуем активности
    serializer = ActivitiesSerializer(activities, many=True)

    # Формируем ответ с id самозанятого-черновика и списком активностей
    return Response({
        "self_employed_draft_id": first_draft.id,
        "activities": serializer.data
    }, status=status.HTTP_200_OK)






@api_view(["GET"])
def get_activities_with_drafts(request):
    """
    Возвращает список всех деятельностей и ID самозанятых-черновиков, 
    которые связаны с этими деятельностями, отсортированных по дате создания самозанятых.
    """
    # Получаем все самозанятые в статусе 'draft', отсортированные по дате создания
    self_employed_drafts = SelfEmployedActivities.objects.filter(
        self_employed__status='draft'
    ).select_related('self_employed').order_by('self_employed__created_date')

    # Создаем словарь для хранения ID самозанятых-черновиков для каждой деятельности
    activity_draft_ids = {activity.id: [] for activity in Activities.objects.all()}

    # Заполняем словарь ID самозанятых для каждой деятельности
    for self_employed_activity in self_employed_drafts:
        activity_id = self_employed_activity.activity.id
        self_employed_id = self_employed_activity.self_employed.id
        activity_draft_ids[activity_id].append(self_employed_id)

    # Формируем ответ с деятельностями и их ID самозанятых черновиков
    response_data = []
    for activity in Activities.objects.all():
        response_data.append({
            "activity_id": activity.id,
            "activity_title": activity.title,
            "self_employed_draft_ids": activity_draft_ids.get(activity.id, [])  # Получаем связанные ID
        })

    return Response(response_data, status=status.HTTP_200_OK)



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



@api_view(["GET"])
def get_activities(request):
    # Получаем категорию из параметров запроса (используем request.GET для GET-запросов)
    category = request.data.get('category')

    # Фильтруем активности по категории, если категория указана
    if category:
        activities = Activities.objects.filter(category=category)
    else:
        activities = Activities.objects.all()  # Если категории нет, возвращаем все активности

    # Сериализуем активности
    serializer = ActivitiesSerializer(activities, many=True)
    
    # Возвращаем сериализованные данные
    return Response(serializer.data, status=status.HTTP_200_OK)






@api_view(["POST"])
def create_activity(request):
    """
    Создает новую деятельность и загружает изображение в MinIO.
    """


    # Получаем данные из запроса
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




@api_view(["PUT"])
def update_activity(request, activity_id):
    """
    Обновляет данные активности по ID. Если активность не найдена — возвращает 404.
    """
    try:
        activity = Activities.objects.get(pk=activity_id)
    except Activities.DoesNotExist:
        return Response({"error": "Активность не найдена."}, status=status.HTTP_404_NOT_FOUND)

    # Получаем данные из запроса
    title = request.data.get('title')
    description = request.data.get('description')
    category = request.data.get('category')
    status_value = request.data.get('status')
    pic = request.FILES.get('pic')  # Получаем файл изображения

    # Обновление только тех полей, которые присутствуют в запросе
    if title is not None:
        activity.title = title
    if description is not None:
        activity.description = description
    if category is not None:
        activity.category = category
    if status_value is not None and status_value in dict(Activities.STATUS_CHOICES):
        activity.status = status_value  # Обновляем статус активности

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



@api_view(["POST"])
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


@api_view(["DELETE"])
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





@api_view(["POST"])
def create_self_employed_for_user(request, user_id):
    """
    Создает запись самозанятого для пользователя.
    """
    # Проверяем, существует ли пользователь
    if not User.objects.filter(pk=user_id).exists():
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)

    # Проверяем, существует ли уже самозанятый для данного пользователя
    if SelfEmployed.objects.filter(user=user).exists():
        return Response({"error": "Самозанятый для данного пользователя уже существует."}, status=status.HTTP_400_BAD_REQUEST)

    # Создаем нового самозанятого
    self_employed = SelfEmployed.objects.create(
        user=user,
        status='draft',  # Устанавливаем статус на черновик
        created_date=timezone.now()
    )

    return Response({
        "message": "Самозанятый успешно создан.",
        "self_employed_id": self_employed.id,
        "user_id": user.id,
        "status": self_employed.status
    }, status=status.HTTP_201_CREATED)




@api_view(["POST"])
def add_activity(request, user_id, activity_id):
    """
    Создает запись самозанятого для пользователя или добавляет активность к существующему самозанятому.
    """
    # Проверяем, существует ли пользователь
    if not User.objects.filter(pk=user_id).exists():
        return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)

    # Проверяем, существует ли уже самозанятый для данного пользователя
    self_employed, created = SelfEmployed.objects.get_or_create(
        user=user,
        defaults={
            'status': 'draft',  # Устанавливаем статус на черновик
            'created_date': timezone.now()
        }
    )

    # Проверяем, существует ли активность
    if not Activities.objects.filter(pk=activity_id).exists():
        return Response({"error": "Активность не найдена."}, status=status.HTTP_404_NOT_FOUND)

    activity = Activities.objects.get(pk=activity_id)

    # Проверяем, существует ли связь между активностью и самозанятым
    if SelfEmployedActivities.objects.filter(activity=activity, self_employed=self_employed).exists():
        return Response({"error": "Эта активность уже добавлена к самозанятому."}, status=status.HTTP_400_BAD_REQUEST)

    # Добавляем активность к самозанятому
    SelfEmployedActivities.objects.create(activity=activity, self_employed=self_employed)
      # Сериализация и возврат обновленных данных
    # serializer = ActivitiesSerializer(activity)
    
    
    
    all_activities = Activities.objects.filter(self_employed_activities__self_employed=self_employed)

    # Сериализация всех активностей
    activities_serializer = ActivitiesSerializer(all_activities, many=True)

    return Response({
        "message": "Активность успешно добавлена к самозанятому.",
        "self_employed_id": self_employed.id,
        "user_id": user.id,
        "user_name": user.username,
        "status": self_employed.status,
        "activities": activities_serializer.data,  # Добавляем информацию о добавленной активности
    }, status=status.HTTP_200_OK)





# ex-----------------------------------------Пользователь------------------------------------------------


@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response({"message": "Пользователь не найден!"},status=status.HTTP_401_UNAUTHORIZED)

    return Response({
        "message": "Пользователь авторизован!"},status=status.HTTP_200_OK)


@api_view(["POST"])
def logout(request):
    return Response({
        "message": "Пользователь вышел!"},status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    # Проверяем, существует ли пользователь
    if not User.objects.filter(pk=user_id).exists():
        return Response({"message": "Пользователь не найден!"}, status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, many=False, partial=True)

    # Проверка на валидность данных
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    # Сохраняем обновленные данные пользователя
    serializer.save()

    # Возвращаем сообщение об успешном обновлении и данные пользователя
    return Response({
        "message": "Пользователь обновлен!",
        "data": serializer.data  # Добавляем сериализованные данные
    }, status=status.HTTP_200_OK)











# ex---------------------------------M-M--------------------------------------------------------





@api_view(["PUT"])
def update_importance(request, self_employed_id, activity_id):
    """
    Обновляет значение поля importance для связи между самозанятым и активностью.
    У одного самозанятого может быть только одна главная деятельность (importance=True).
    """
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

    # Получаем все активности для данного самозанятого
    updated_activities = SelfEmployedActivities.objects.filter(self_employed_id=self_employed_id)
    
    # Сериализуем обновленные данные
    serializer = SelfEmployedActivitiesSerializer(updated_activities, many=True)

    # Возвращаем обновленные данные и сообщение
    return Response({
        "message": "Поле importance успешно обновлено.",
        "updated_activities": serializer.data
    }, status=status.HTTP_200_OK)






@api_view(["DELETE"])
def delete_self_employed_activity(request, self_employed_id, activity_id):
    """
    Удаляет связь между самозанятым и активностью по их ID. Если не найдено — возвращает 404.
    """
    # Проверяем, существует ли связь между самозанятым и активностью
    item = SelfEmployedActivities.objects.filter(self_employed_id=self_employed_id, activity_id=activity_id).first()

    if not item:
        return Response({"error": "Связь между самозанятым и активностью не найдена."}, status=status.HTTP_404_NOT_FOUND)

    # Удаляем связь
    item.delete()

    return Response({"message": "Связь успешно удалена."}, status=status.HTTP_204_NO_CONTENT)












# @api_view(["GET"])
# def get_activity_image(request, activity_id):
#     """
#     Получает изображение активности по ID. Если активность не найдена — возвращает 404.
#     """
#     if not Activities.objects.filter(pk=activity_id).exists():
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     activity = Activities.objects.get(pk=activity_id)
#     response = requests.get(activity.image.url.replace("localhost", "minio"))

#     return HttpResponse(response, content_type="image/png")


# @api_view(["POST"])
# def update_activity_image(request, activity_id):
#     """
#     Обновляет изображение активности по ID. Если активность не найдена — возвращает 404.
#     """
#     if not Activities.objects.filter(pk=activity_id).exists():
#         return Response(status=status.HTTP_404_NOT_FOUND)

#     activity = Activities.objects.get(pk=activity_id)
#     image = request.data.get("image")
    
#     if image is not None:
#         activity.image = image
#         activity.save()

#     serializer = ActivitiesSerializer(activity)

#     return Response(serializer.data)


# @api_view(["GET"])
# def search_activities(request):
#     """
#     Выполняет поиск активностей по статусу и дате создания. Фильтрует по статусу и диапазону дат.
#     """
#     status = int(request.GET.get("status", 0))
#     date_start = request.GET.get("date_start")
#     date_end = request.GET.get("date_end")

#     activities = Activities.objects.exclude(status__in=[1, 5])

#     if status > 0:
#         activities = activities.filter(status=status)

#     if date_start and parse_datetime(date_start):
#         activities = activities.filter(date_created__gte=parse_datetime(date_start))

#     if date_end and parse_datetime(date_end):
#         activities = activities.filter(date_created__lt=parse_datetime(date_end))

#     serializer = ActivitiesSerializer(activities, many=True)

#     return Response(serializer.data)







# ex-----------------------------------------------------------------------------------------





