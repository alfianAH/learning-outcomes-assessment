from django.http import Http404, HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django_q.tasks import result
from django.urls import reverse
from .utils import request_nusoap


def home_view(request: HttpRequest):
    if request.user.is_authenticated:
        return render(request, 'home-view.html')
    
    return redirect(reverse('accounts:login'))


def dosen_json_response(request: HttpRequest):
    search_text = request.GET.get('search', '')
    json = request_nusoap(search_text)
    
    return JsonResponse(json)


@login_required
def get_task_result(request: HttpRequest):
    task_id = request.GET.get('task_id')
    if task_id is None:
        return JsonResponse({'result': None})
    
    task_result = result(task_id)
    return JsonResponse({'result': task_result}, safe=False)


@login_required
def get_admin_only_view(request: HttpRequest):
    user = request.user
    if user.role != 'a':
        raise Http404
    
    contents = [
        ['Program studi restricted mode', reverse('accounts:prodi-restricted', kwargs={'prodi_id': user.prodi.id_neosia})]
    ]

    context = {
        'objects': contents
    }
    
    return render(request, 'admin-only/home.html', context=context)

