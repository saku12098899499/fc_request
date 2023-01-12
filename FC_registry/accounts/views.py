from django.shortcuts import render
from django.views import generic 
from django.contrib.auth.forms import UserCreationForm  # ユーザのログイン,ログアウトの簡易実装
from django.urls import reverse_lazy  # ページ名からURLを取得
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from fc_request.models import Wallet    # ウォレット情報をimport
from django.http import Http404

class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/signup.html'

def Mypage(request):
    try:
        user_info = get_object_or_404(User,id=request.user.id)
        wallet_info = Wallet.objects.get(id=request.user.id)
        context = {'user_info':user_info,'wallet_info':wallet_info}
        return render(request,'accounts/mypage.html',context)
    except Wallet.DoesNotExist:
        raise Http404("ビットコインウォレットが付与されていません.")