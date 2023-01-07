from django.contrib import admin
from .models import Wallet,Category,Rating,Request,Response

admin.site.register(Wallet)   # adminサイトにWalletモデルを追加
admin.site.register(Category) # adminサイトにCategoryモデルを追加
admin.site.register(Rating)  # adminサイトにRatingモデルを追加
admin.site.register(Request)  # adminサイトにRequestモデルを追加
admin.site.register(Response) # adminサイトにResponseモデルを追加