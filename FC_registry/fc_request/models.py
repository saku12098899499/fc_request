from django.db import models
from django.urls import reverse
from django.utils import timezone
#from datetime import timedelta

""" ウォレットアドレスモデル """
class Wallet(models.Model):
    wallet_address = models.CharField(
        verbose_name='ウォレットアドレス', # ビットコインアドレスの長さは27〜34文字
        max_length=50,
        default=''
        ) 

    def __str__(self):  # オブジェクト(allet_address)に対して文字列が要求された際に返す値を定義している.
        return self.wallet_address
        

""" カテゴリーモデル """
class Category(models.Model):
    name = models.CharField(
        verbose_name='カテゴリー',
        max_length=50,  # 50文字制限
        ) 

    def __str__(self):   # __str...は管理画面でデータの判別をしやすくする.
        return self.name
        

""" レーティングモデル """
class Rating(models.Model):
    name = models.CharField(
        verbose_name='レーティング',
        max_length=20,   # 20文字制限
        
        ) 

    def __str__(self):   
        return self.name


""" FCリクエストモデル """
class Request(models.Model):
    title = models.CharField(max_length=100) # 50文字制限.  大小サイズ混合の文字列フィールド
    contributor = models.ForeignKey(         # foreignkeyは一対多(twitterを例にすると一人がツイートした記事に対して複数人が閲覧できる構図)
        'auth.User',
        on_delete = models.PROTECT # id等で接続先のテーブルレコードが削除された場合にPrortectedErrorが発生して紐付いているユーザ情報は削除されない.
    )
    category = models.ForeignKey(
        Category, verbose_name='カテゴリー',
        on_delete = models.PROTECT 
    )
    request_cont = models.TextField(max_length=1000)
    image = models.ImageField(   #  ImageField : 画像ファイルを扱うフィールド
        upload_to ='img/', # アップロードファイルのディレクトリ
        blank = True, # フィールド値の設定は必須でない(空白部分を許可しているため中身がカラでもいい)
        null = True   # データベースにnullが保存されることを許容(空白部分を含めて何もナイ)
    )
    startline = models.DateTimeField(    # インスタンス(オブジェクト指向における実際に作成したもの)で時刻を表示
        verbose_name = '投稿時刻',
        auto_now_add = True
    ) 

    txid_request = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    ########締め切り時刻の指定###############
    deadline = models.DateField(default=timezone.now)
    #########################################
    class Meta:
        ordering = ["-startline"] #　新規日付順に並べ変え

    def __str__(self):
        return self.request_cont

    def get_absolute_url(self):
        return reverse('fc_request:request_detail',kwargs={'pk':self.pk}) # /detail/数字　を返す


""" FCレスポンスモデル """
class Response(models.Model):
    contributor = models.ForeignKey(   # foreignkeyは一対多(twitterを例にすると一人がツイートした記事に対して複数人が閲覧できる構図)
        'auth.User',
        on_delete = models.PROTECT # id等で接続先のテーブルレコードが削除された場合にPrortectedErrorが発生して紐付いているユーザ情報は削除されない.
    )
    response_cont = models.TextField(verbose_name='レスポンス内容', blank=False)
    target = models.ForeignKey(
        Request, 
        on_delete=models.CASCADE, 
        verbose_name='依頼対象'
    )
    rating = models.ForeignKey(
        Rating,verbose_name='レーティング',
        on_delete=models.PROTECT
    )
    startline = models.DateTimeField(    # インスタンス(オブジェクト指向における実際に作成したもの)で時刻を表示
        verbose_name = '投稿時刻',
        auto_now_add = True
    )

    txid_response = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    
    def __str__(self):
        return self.response_cont