# main/views.py
from django.shortcuts import render
from datetime import datetime


services = [
     {
        'id': 1,
        'title': 'Маникюр и педикюр',
        'img_url': 'http://127.0.0.1:9000/flexwork/1.png',
        'description': 'Оказание профессиональных услуг маникюра и педикюра, комплексный уход за руками и ногами, создание стильных и современных дизайнов ногтей.',
        'category': 'Красота и здоровье',
    },
    
   {
            'id': 2,
            'title': 'Услуги косметолога',
            'img_url': 'http://127.0.0.1:9000/flexwork/2.jpg',
            'description': 'Комплексные услуги по уходу за кожей лица и тела, направленные на улучшение состояния кожи и решение конкретных проблем, таких как акне, пигментация, возрастные изменения и сухость кожи.',
            'category': 'Красота и здоровье',
        },
   
    {
        'id': 3,
        'title': 'Ремонт бытовой техники',
        'img_url': 'http://127.0.0.1:9000/flexwork/3.jpg',
        'description': 'Оказание услуг по ремонту бытовой техники на дому с быстрым и качественным решением проблем с техникой.',
        'category': 'Бытовые услуги',
  
    },
    {
        'id': 4,
        'title': 'Консультации по медицинским вопросам',
        'img_url': 'http://127.0.0.1:9000/flexwork/4.webp',
       
        'description': 'Консультации и рекомендации по медицинским вопросам от опытных врачей и специалистов.',
       
        'category': 'Красота и здоровье',
    },
    {
        'id': 5,
        'title': 'Репетитор по Английскому языку',
        'img_url': 'http://127.0.0.1:9000/flexwork/5.png',
       
        'description': 'Проведение индивидуальных и групповых занятий по английскому языку для детей, подростков и взрослых. ',
       
        'category': 'Образование',


    },
    {
        'id': 6,
        'title': 'Уборка и клининг',
        'img_url': 'http://127.0.0.1:9000/flexwork/6.webp',
       
        'description': 'Предоставление профессиональных услуг по уборке и клинингу жилых и коммерческих помещений с использованием качественных чистящих средств и современного оборудования. Услуги включают как разовые генеральные уборки, так и регулярное поддержание чистоты.',
        'category': 'Бытовые услуги',
    },
]

basket=[ 
   {
            'id': 1,
            'fio': 'Самойловская Екатерина Михайловна',
            'service_id':1,
            'main':'main',
        },
     {
            'id': 2,
            'fio': 'Самойловская Екатерина Михайловна',
            'service_id':5,
            'main':'',
        },
   
     {
            'id': 3,
            'fio': 'Самойловская Екатерина Михайловна',
            'service_id':4,
            'main':'',
        },
]


def GetName(basket):
    for item in basket:
        return item['fio']


def GetBasketServices(basket, services):
    main = 0
    service_ids = {}

    for item in basket:
        if item.get('main') == 'main':
            main = item['service_id']
        if item['service_id'] not in service_ids:
            service_ids[item['service_id']] = 1
        # else:
        #     service_ids[item['service_id']] += 1

    # Фильтруем услуги, которые есть в корзине
    basket_services = [service for service in services if service['id'] in service_ids]

    return [basket_services, len(service_ids), main]



def GetServices(request):
    if request.method == 'GET':
        query = request.GET.get('selected_services', '').strip()
        if query:
            filtered_services = [
                service for service in services
                if query.lower() in service['title'].lower() or query.lower() in service['description'].lower() or query.lower() in service['category'].lower()
            ]
        else:
            filtered_services = services
        return render(request, 'index.html', {'data' : {
        'services': filtered_services,
        'selected_services': query,
        }})
    
    else:
       return render(request, 'index.html', {'data' : {
        'services': services,
        }})
    
    

def GetService(request, id):
    service = next((item for item in services if item['id'] == id), None)
    if service is None:
        # Обработка случая, когда услуга не найдена
        return render(request, '404.html', status=404)
    context = {'service': service}
    return render(request, 'card.html', context)


def GetBasket(request):
  # Передаем переменные basket и services в функцию GetBasketServices
    basket_services, count, main = GetBasketServices(basket, services)
    return render(request, 'basket.html', {'data': {
        'fio': GetName(basket),
        'services': basket_services,
        'count': count,
        'main': main,
    }})
