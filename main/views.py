# importance/views.py
from django.shortcuts import render
from datetime import datetime


activities = [
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



self_employed= {
    'fio': 'Самойловская Екатерина Михайловна',
    'activities':[
        {
            'id': 1,
            'id_activity':1,
            'importance': True,
        },
     {
            'id': 2,
            'id_activity':5,
            'importance': False,
        },
   
     {
            'id': 3,
            'id_activity':4,
            'importance':False,
        },
        
    ]
    
}






def GetSelfEmployedActivities(self_employed, activities):
    importance = 0
    id_activities = {}
    self_employed= self_employed['activities']

    for item in self_employed:
        if item.get('importance') == True:
            importance = item['id_activity']
        if item['id_activity'] not in id_activities:
            id_activities[item['id_activity']] = 1
    
    # Фильтруем услуги, которые есть в корзине
    basket_activities = [service for service in activities if service['id'] in id_activities]
    


    return [basket_activities, len(id_activities), importance]



def GetActivities(request):
    if request.method == 'GET':
        query = request.GET.get('activity', '').strip()
        _, count, _ = GetSelfEmployedActivities(self_employed, activities)
        
        if query:
            filtered_activities = [
                service for service in activities
                if query.lower() in service['title'].lower() or query.lower() in service['description'].lower() or query.lower() in service['category'].lower()
            ]
        else:
            filtered_activities = activities
            
        return render(request, 'index.html', {'data' : {
        'activities': filtered_activities,
        'activity': query,
        'count': count,
        }})
    
    else:
       return render(request, 'index.html', {'data' : {
        'activities': activities,
        'count': count,
        }})
    
    

def GetActivity(request, id):
    activity = next((item for item in activities if item['id'] == id), None)
    if activity is None:
        # Обработка случая, когда услуга не найдена
        return render(request, '404.html', status=404)
    context = {'service': activity}
    return render(request, 'card.html', context)


def GetSelfEmployed(request, count=0):

    basket_activities, _, importance = GetSelfEmployedActivities(self_employed, activities)
    return render(request, 'basket.html', {'data': {
        'activities': basket_activities,
        'count': count,
        'importance': importance,
    }})
