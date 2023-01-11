from django.shortcuts import render,redirect,get_object_or_404
from .models import Request,Wallet,Response 
from django.views import generic
from django.db.models import Q
from .forms import RequestForm,ResponseForm
from django.views.generic import FormView

import hashlib

""" FCリクエスト  一覧ページ """
class List_request(generic.ListView): # 一覧ページの作成
    model = Request # リスト作成するモデル
    paginate_by = 5

    def get_queryset(self):  # モデルインスタンスの一覧を返すメソッド
        q_word = self.request.GET.get('query') # requestからgetメソッドを使ってデータを取得

        #　以下、チェックボックスにチェックが入っている項目 
        selected_title = self.request.GET.get('title')
        selected_article = self.request.GET.get('article')

        if q_word:
            if selected_title and selected_article:
                object_list = Request.objects.filter(Q(title__icontains=q_word) | Q(content__icontains=q_word))
                # icontainsで大文字,小文字区別無し  |でor文
            elif selected_title:
                object_list = Request.objects.filter(Q(title__icontains=q_word))    
            else:
                object_list = Request.objects.filter(Q(content__icontains=q_word))
        else: # 投稿内容のみ、または両方ともチェックされていないときは投稿内容のみを検索する
            object_list = Request.objects.all()

        return object_list          


""" FCリクエスト  フォームページ """
def Form_request(request):
    if request.method == 'GET': # webブラウザからwebサーバにページを要求.URLに情報が残るのでパスワードはNG
        print('GETリクエスト')
        content = {'form':RequestForm}
        return render (request,'fc_request/request_form.html',context=content)

    if request.method == 'POST':# GETコマンドと同様にページを要求.ただしURLに情報が残らないためパスワードも扱える.
        wallet = Wallet.objects.get(id=request.user.id) # user.id ログインユーザの取得し,idと一致したときwalletを表示
        print(wallet)
        context = {'wallet':wallet}
        print('POSTリクエスト')
        print("///////////////////////////////////////////////////")
        text= str(["タイトル： " + request.POST["title"],"カテゴリー： " + request.POST["category"],"投稿内容 :  " + request.POST["request_cont"]])
        print(text)
        params = {'message':'','form':None}
        form = RequestForm(request.POST) # request.POSTでRequestFormのデータを辞書型で取得する.
        if form.is_valid(): # バリデーション(入力された値が有効であるかを検証する.)を行う.
            image = None
            try:
                image = request.FILES["image"]

                sha256 = hashlib.sha256(image.read()).hexdigest() # 画像のハッシュ化(
                print("///////////////////////////////////////////////")
                print('SHA256ハッシュ値:\n {0}'.format(sha256))
                print("///////////////////////////////////////////////")
                
            except:
                sha256 = None
            
            form.save(user_id=request.user.id,image=image)
            textdata = text + str(" ") + str("画像のハッシュ値:") + str(sha256)
            print("ブロックチェーンへの書き込み：" + textdata)
            walletdata = str(wallet)
            print("ウォレットアドレス：" + walletdata)
            return redirect("/fc_request", context)
        else:
            params['message'] = '再入力して下さい'
            params['form'] = form 


""" FCリクエスト  詳細ページ """
def Detail_request(request,pk):
    object = get_object_or_404(Request,id = pk) #  Requestモデルからidと一致したpkのレコードを取得し,object変数へ格納.
    #response = Response.objects.filter(target_id_id = pk).all()
    context = {'object':object,} # 辞書型で渡す値を指定している.
    return render (request,'fc_request/request_detail.html',context) # renderは指定されたテンプレートをレンダリング(表示用のデータをもとに、内容を整形して表示)してレスポンスを返す.


""" FCレスポンス  フォームページ """
class Response_request(generic.CreateView,FormView):
    template_name = 'fc_request/request_response.html'
    model = Response
    form_class = ResponseForm
    
    #success_url = "/fc_request/1/"
    def post(self, request, *args, **kwargs):
            # ajaxの場合
            post = request.POST
            post_pk = self.kwargs['pk']
            post = get_object_or_404(Request,pk=post_pk)
            print(request.POST["response_cont"],request.POST["rating"])
            obj=Response(response_cont=request.POST["response_cont"],contributor=request.user,target_id=post_pk,rating_id=request.POST["rating"])#request.POST["response_cont"],request.POST["rating"])
            obj.save()
            print("aaaaaaaaaaaaa")
            return redirect('fc_request:request_detail', pk=post_pk)

    # def form_valid(self,form):
    #     post_pk = self.kwargs['pk']
    #     post = get_object_or_404(Request,pk=post_pk)
    #     response = form.save(commit=False)
    #     response.target_id = post
    #     response.save()
    #     print("aaaaaaaaaaaaa")
    #     return redirect('fc_request:request_detail', pk=post_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Request, pk=self.kwargs['pk'])
        return context

            

