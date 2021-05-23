from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from django.shortcuts import render, HttpResponse
from urllib.error import URLError
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import csrf_exempt
from checker_app import models
from django.core import serializers
import json

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

def fetch_model():
    m = models.dictionary.objects.all()
    data = serializers.serialize("json", m)
    return data

@xframe_options_exempt
def index(request):
    return render(request, 'index.html')

@xframe_options_exempt
def account(request):
    return render(request, 'account.html')

@xframe_options_exempt
def free(request):
    return render(request, 'free.html')

@csrf_exempt
@xframe_options_exempt
def check_spell(request):
    if request.method == 'POST':
        try:
            url = request.POST['web_url']
            data = scrap_Data(url, hdr)
            if data == False:
                return HttpResponse("error_in_url")
            else:
                soup = BeautifulSoup(data, "html.parser")
                sentence = " ".join(soup.strings)
            data = {}
            data['sentence'] = sentence
            data['prev_data'] = fetch_model()
            data = json.dumps(data, indent=4, sort_keys=True, default=str)
            return HttpResponse(data, content_type='application/json')
        except (EOFError, KeyError):
            return HttpResponse("0")
    else:
        return HttpResponse("<h1>Method Not Allowed</h1>")

def try_with_http(url, header):
    try:
        page = Request('http://'+url, headers=header)
        html = urlopen(page).read().decode("utf-8")
        if html != None:
            return html
        else:
            return False
    except (EOFError, URLError):
        return False

def scrap_Data(url, header):
    if ('https://' in url) or ('http://' in url):
        U = url
    else:
        U = "https://"+url
    try:
        page = Request(U, headers=header)
        html = urlopen(page).read().decode("utf-8")
        if html != None:
            return html
        else:
            try_with_http(url, header)
    except (EOFError, URLError):
        t = try_with_http(url, header)
        return t