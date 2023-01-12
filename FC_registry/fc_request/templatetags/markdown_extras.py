from django import template
from django.template.defaultfilters import stringfilter  #  文字列のみをフィルタリング  stringfilterで文字列に変換された入力値がフィルタに渡される
import markdown as md

register = template.Library() # djangoのテンプレートタグライブラリ

@register.filter() # フィルター用のデコレータを呼び出し
@stringfilter # 文字列のフィルター用デコレータ

def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])
