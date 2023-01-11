from django.views.generic import RedirectView
from django.contrib import admin
from django.urls import include,path
from django.conf import settings  # FC_registryのsettingsで定義された変数(MEDIA_URL等)
from django.conf.urls.static import static 

urlpatterns = [
    path('',RedirectView.as_view(url='/fc_request/')),
    path('admin/', admin.site.urls),
    path('fc_request/',include('fc_request.urls')), # URL：htttps://.../fc_request/に,fc_requestのurls.pyが紐づく
    path('accounts/',include('accounts.urls')),  # URL：/accounts/にurls.pyが紐づく
    path('accounts/',include('django.contrib.auth.urls')), # 上記と同様にurls.pyに紐づける.
]

if settings.DEBUG: # debug：バグの原因を探して取り除く
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # static(静的ファイルの配信URL,静的ファイルの保存先を指定)