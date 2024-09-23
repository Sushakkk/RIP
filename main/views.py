from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Activities, SelfEmployedActivities, SelfEmployed

from django.contrib.auth.models import User
from django.db import connection
from django.utils import timezone



def GetActivities(request):
    activities = Activities.objects.filter(status='active')
    query = request.GET.get('activity', '').strip()

    # Получаем корзину
    self_employed = get_self_employed()

    if self_employed is not None:
        basket_activities = self_employed.activities.all()
        count = basket_activities.count()  # Считаем количество активностей
    else:
        basket_activities = Activities.objects.none()  # Если черновика нет
        count = 0

    if query:
        filtered_activities = [
            activity for activity in activities
            if (query.lower() in activity.title.lower() or
                query.lower() in activity.description.lower() or
                query.lower() in activity.category.lower())
        ]
    else:
        filtered_activities = activities

    return render(request, 'index.html', {'data': {
        'activities': filtered_activities,
        'activity': query,
        'count': count,
    }})




def GetActivity(request, id):
    activity = get_object_or_404(Activities, id=id, status='active')
    context = {'service': activity}
    return render(request, 'card.html', context)




    
def add_activity(request, activity_id):
    # Получаем активность по ID
    activity = get_object_or_404(Activities, pk=activity_id)
    self_employed = get_self_employed()

    # Если черновика нет, создаем новый
    if self_employed is None:
        current_user = get_current_user()
        self_employed = SelfEmployed.objects.create(
            user=current_user,  # Указываем пользователя
            status='draft'
        )

    # Проверяем, существует ли уже такая связь
    if SelfEmployedActivities.objects.filter(self_employed=self_employed, activity=activity).exists():
        return redirect("/")

    # Создаем новую запись о деятельности самозанятого
    item = SelfEmployedActivities(
        self_employed=self_employed,
        activity=activity
    )
    item.save()

    return redirect("/")





def get_self_employed():
    return SelfEmployed.objects.filter(status='draft').first()  # Получаем первый черновик

def get_current_user():
    return User.objects.filter(is_superuser=False).first()  # Получаем текущего пользователя, исключая суперпользователя
    
    
    
    
    
    
    
    
    
def GetSelfEmployed(request, self_employed_id=0):
    
 
    current_user = get_current_user()
    
    try:
        # Получаем самозанятого для текущего пользователя
        self_employed = SelfEmployed.objects.get(user=current_user,  status='draft')

        # Получаем все связанные активности через промежуточную таблицу
        activities_with_importance = SelfEmployedActivities.objects.filter(self_employed=self_employed).select_related('activity')

        # Формируем список активностей с полем importance
        activities_data = [
            {
                'activity': item.activity,  # Активность
                'importance': item.importance  # Значение поля importance
            }
            for item in activities_with_importance
        ]


    except SelfEmployed.DoesNotExist:
        # Если самозанятый не найден
        activities_data = []


    # Возвращаем данные в шаблон
    return render(request, 'basket.html', {
        'data': {
            'self_employed':self_employed,
            'activities': activities_data,
        }
    })




# def current_request(request):
#     user = request.user
#     self_employed_request = get_object_or_404(SelfEmployed, user=user, status='draft')
#     activities = self_employed_request.activities.all()
#     return render(request, 'current_request.html', {'request': self_employed_request, 'activities': activities})


def delete_self_employed(request, self_employed_id):
    with connection.cursor() as cursor:
        cursor.execute("UPDATE self_employed SET status = 'deleted' WHERE id = %s", [self_employed_id])

    current_user = get_current_user()
    
    # Инициализируем переменную self_employed значением None
    self_employed = None
    activities_data = []

    try:
        # Получаем самозанятого для текущего пользователя со статусом 'draft'
        self_employed = SelfEmployed.objects.get(user=current_user, status='draft')

        # Получаем все связанные активности через промежуточную таблицу
        activities_with_importance = SelfEmployedActivities.objects.filter(self_employed=self_employed).select_related('activity')

        # Формируем список активностей с полем importance
        activities_data = [
            {
                'activity': item.activity,  # Активность
                'importance': item.importance  # Значение поля importance
            }
            for item in activities_with_importance
        ]

    except SelfEmployed.DoesNotExist:
        # Если самозанятый не найден, activities_data останется пустым
        pass

    # Возвращаем данные в шаблон
    return render(request, 'basket.html', {
        'data': {
            'self_employed': self_employed,
            'activities': activities_data,
        }
    })
