import os

from asgiref.sync import sync_to_async
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie

from gradProject import settings
from gradProject.settings import MEDIA_ROOT
from project.forms import UploadFileForm, ForecastForm
from project.models import Forecast, Saved
from project.utils import parse_excel, handle_uploaded_file, data_processing, make_report


def home(request):
    return render(request, 'project/home.html')

def make_forecast(request):
    if request.method == 'POST' and request.FILES['file']:
        myfile = request.FILES['file']
        # fs = FileSystemStorage(os.path.join(MEDIA_ROOT, "excel/"))
        filename = myfile.name
        forecast, clean_df, graph_url = data_processing(myfile, filename)

        forecast = forecast.reset_index()
        cols_fc = forecast.columns.tolist()
        forecast[cols_fc[0]] = forecast[cols_fc[0]].dt.date
        forecast = forecast[1:]
        forecast = forecast.values.tolist()

        clean_df = clean_df.reset_index()
        cols_df = clean_df.columns.tolist()
        clean_df[cols_df[0]] = clean_df[cols_df[0]].dt.date
        clean_df = clean_df.values.tolist()

        pdf_url = make_report(filename, cols_df, clean_df, forecast, graph_url)

        project = Forecast.objects.create(
            file_name=filename,
            excel=myfile,
            image=graph_url,
            pdf=pdf_url,
        )

        context = {
            'cols_fc': cols_fc,
            'forecast': forecast,
            'cols_df': cols_df,
            'clean_df': clean_df,
            'project': project,
        }
        return render(request, 'project/results.html', context)
    context = {
        'error': 'Загрузите файл',
    }
    return render(request, 'project/make_forecast.html')


def add_to_profile(request, pk):
    forecast = Forecast.objects.get(pk=pk)
    if request.user.is_authenticated:
        saved = Saved.objects.filter(user=request.user, forecast=forecast)
        if saved.exists():
            return render(request, 'users/profile.html')
        else:
            Saved.objects.create(user=request.user, forecast=forecast)
            user_forecasts = Saved.objects.filter(user=request.user)
            context = {
                'user_forecasts': user_forecasts,
            }
            return render(request, 'users/profile.html', context)
    return render(request, 'users/login.html')
