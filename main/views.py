# main/views.py
from django.shortcuts import render, get_object_or_404
from datetime import datetime


services = [
   {
            'id': 1,
            'title': 'Услуги по предоставлению письменных консультаций по направлению Социальная работа',
            'img_url': 'http://127.0.0.1:9000/flexwork/1.jpeg',
            'price': '500',
            'description': 'Письменные консультации по вопросам социальной работы. Опытные специалисты помогут вам разобраться в сложных вопросах.',
            'company': 'Социальные Решения',
            'category': 'Консультации',
            'start_date': datetime.strptime('2024-09-10T00:00:00', '%Y-%m-%dT%H:%M:%S'),
            'end_date': datetime.strptime('2024-09-15T18:00:00', '%Y-%m-%dT%H:%M:%S'),
            'address': 'г. Москва, ул. Примерная, д. 1'
        },
    {
        'id': 2,
        'title': 'Юридическая консультация по семейным делам',
        'img_url': 'http://127.0.0.1:9000/flexwork/2.jpeg',
        'price': '1000',
        'description': 'Юридическая помощь по вопросам семейного права, включая разводы, опеку, алименты и другие аспекты.',
        'company': 'ЮрПомощь',
        'category': 'Юридические услуги',
        'start_date': datetime.strptime('2024-09-12T09:00:00', '%Y-%m-%dT%H:%M:%S'),
        'end_date': datetime.strptime('2024-09-20T17:00:00', '%Y-%m-%dT%H:%M:%S'),
        'address': 'г. Санкт-Петербург, ул. Юридическая, д. 5'
    },
    {
        'id': 3,
        'title': 'Финансовое планирование и консультации',
        'img_url': 'http://127.0.0.1:9000/flexwork/3.jpg',
        'price': '1500',
        'description': 'Профессиональные услуги по финансовому планированию, инвестициям и управлению личными финансами.',
        'company': 'ФинансГрупп',
        'category': 'Финансовые услуги',
         'start_date': datetime.strptime('2024-09-12T09:00:00', '%Y-%m-%dT%H:%M:%S'),
        'end_date': datetime.strptime('2024-09-20T17:00:00', '%Y-%m-%dT%H:%M:%S'),
        'address': 'г. Новосибирск, ул. Финансовая, д. 10'
    },
    {
        'id': 4,
        'title': 'Консультации по медицинским вопросам',
        'img_url': 'http://127.0.0.1:9000/flexwork/4.webp',
        'price': '800',
        'description': 'Консультации и рекомендации по медицинским вопросам от опытных врачей и специалистов.',
        'company': 'МедЦентр',
        'category': 'Медицинские услуги',
        'start_date': datetime.strptime('2024-09-12T09:00:00', '%Y-%m-%dT%H:%M:%S'),
        'end_date': datetime.strptime('2024-09-20T17:00:00', '%Y-%m-%dT%H:%M:%S'),
        'address': 'г. Екатеринбург, ул. Медицинская, д. 12'
    },
    {
        'id': 5,
        'title': 'Курсы по программированию для начинающих',
        'img_url': 'http://127.0.0.1:9000/flexwork/5.jpg',
        'price': '2000',
        'description': 'Обучение основам программирования с нуля. Практические занятия и теоретические знания для старта в IT.',
        'company': 'IT Академия',
        'category': 'Образование',
         'start_date': datetime.strptime('2024-09-12T09:00:00', '%Y-%m-%dT%H:%M:%S'),
        'end_date': datetime.strptime('2024-09-20T17:00:00', '%Y-%m-%dT%H:%M:%S'),
        'address': 'г. Казань, ул. Академическая, д. 15'
    },
    {
        'id': 6,
        'title': 'Профессиональные тренинги по лидерству',
        'img_url': 'http://127.0.0.1:9000/flexwork/6.png',
        'price': '2500',
        'description': 'Интенсивные тренинги по развитию лидерских качеств и управленческих навыков.',
        'company': 'ЛидерШкола',
        'category': 'Тренинги',
         'start_date': datetime.strptime('2024-09-12T09:00:00', '%Y-%m-%dT%H:%M:%S'),
        'end_date': datetime.strptime('2024-09-20T17:00:00', '%Y-%m-%dT%H:%M:%S'),
        'address': 'г. Ростов-на-Дону, ул. Лидерская, д. 22'
    },
]


def GetServices(request):
    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if query:
            filtered_services = [
                service for service in services
                if query.lower() in service['title'].lower() or query.lower() in service['description'].lower()
            ]
        else:
            filtered_services = services
        return render(request, 'index.html', {'services': filtered_services})
    else:
        return render(request, 'index.html', {'services': services})
    
    

def GetService(request, id):
    service = next((item for item in services if item['id'] == id), None)
    if service is None:
        # Обработка случая, когда услуга не найдена
        return render(request, '404.html', status=404)
    context = {'service': service}
    return render(request, 'card.html', context)


def GetBasket(request):
    
    context = {'services': services}
    return render(request, 'basket.html', context)

