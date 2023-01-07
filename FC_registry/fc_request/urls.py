from django.urls import path # Httpレスポンスから送られてきたurlにマッチするpathをurls.pyから探す
from . import views # 階層の同ディレクトリ(カレントパス(相対パス) form . import (ディレクトリ名))のviewをimport 

app_name = 'fc_request' # 以下ルーティング設定

urlpatterns = [
    path('',views.List_request.as_view(),name='request_list'),
    path('request_form/' ,views.Form_request ,name='request_form'),
    path('<int:pk>/' ,views.Detail_request ,name='request_detail'),
    path('<int:pk>/response_form/',views.Response_request.as_view(), name='response_form'),
]