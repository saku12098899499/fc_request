from django import forms
from .models import Request,Response
from django.contrib.auth.models import User # ユーザモデル(Djangoアプリの認証で使われるモデル)クラスをimport

""" ファクトチェック依頼　フォーム """
class RequestForm(forms.ModelForm): # django.forms.ModelForm：models.py で定義したものと同じ場合に使用できるフィールド.
    class Meta: # メタクラスは「class文の持つ定義する機能」を定義する機能(クラスに対して追加の情報や機能を差し挟みやすくしてくれる)
        model = Request
        fields = ("title","category","request_cont","image","deadline") # モデルで定義したものから使用するものをフィールドに追加
        labels = {                           # 表示するラベルを指定.
            "title":"タイトル",
            "category":"カテゴリー",
            "request_cont":"内容",
            "image":"画像",
            "deadline":"終了時刻"
    
            # ////////////締め切り時間deadlineを組み込む.////////////////////////
            
        }
     
    
    def save(self,user_id,image=None):
        data = self.cleaned_data    #　バリデート(フォーム内に適切なものが入力されたかを確認)後に適切と判断されたデータが入る.
        user = User.objects.get(id=user_id)
        post = Request(title=data['title'],contributor=user,category=data['category'],request_cont=data['request_cont'],image=image)
        post.save()


""" ファクトチェック請負　フォーム """
class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        exclude = ('target', 'startline')