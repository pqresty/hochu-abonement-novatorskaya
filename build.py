"""Build the review copy from the preserved Claude v42 fragment. Python 3, no dependencies."""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parent
SRC, OUT = ROOT / 'src', ROOT / 'docs'
source = (SRC / 'site.html').read_text()
docs = json.loads((SRC / 'documents.json').read_text())

def exactly(text, old, new, count=1):
    assert text.count(old) == count, (old[:80], text.count(old), count)
    return text.replace(old, new)

page = re.sub(r'\{\{DOC:(\w+)\}\}', lambda m: html.escape(docs[m[1]], quote=True), source)
page = re.sub(r'<link[^>]+(?:fonts.googleapis.com|fonts.gstatic.com)[^>]*>\s*', '', page)
css = (OUT / 'assets/fonts/full.css').read_text()
fonts = []
for family, weights in [('Onest', '200 500'), ('Unbounded', '200 600')]:
    cyr = re.search(r"/\* cyrillic \*/\s*@font-face\s*\{[^}]*font-family:\s*'" + family + r"'[^}]*unicode-range:\s*([^;]+);", css)[1]
    for subset, ranges in [('cyrillic', cyr), ('latinsym', (OUT / f'assets/fonts/{family}-latinsym.range').read_text().strip())]:
        fonts.append("@font-face{font-family:'%s';font-style:normal;font-weight:%s;font-display:swap;src:url('assets/fonts/%s-%s.woff2') format('woff2');unicode-range:%s}" % (family, weights, family, subset, ranges))
page = exactly(page, '<style>', '<style>\n' + '\n'.join(fonts) + '\n')
page = exactly(page, '<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>', '<script src="assets/vendor/qrcode.min.js"></script>')
page = exactly(page, '<!--WIDGET-->', (SRC / 'widget.html').read_text())
page = exactly(page, '<!--WIDGET2-->', '')
map_html = '<iframe src="https://yandex.ru/map-widget/v1/?ll=37.524206%2C55.672853&amp;z=16&amp;pt=37.524206%2C55.672853%2Cpm2rdm" title="Студия на карте: Москва, Ленинский проспект, 95Б" loading="lazy" allowfullscreen></iframe>'
page = exactly(page, '<!--MAP-->', map_html, 2)

# The review host has no Tilda form receiver. Describe the actual action honestly.
page = exactly(page, 'id="bsubmit" disabled>Отправить заявку', 'id="bsubmit" disabled>Подготовить письмо')
page = re.sub(r'(<p class="b-note" id="bnote">).*?(</p>)', r'\1После заполнения откроется ваша почтовая программа. Отправьте письмо, чтобы студия получила заявку. Также можно позвонить или написать в Telegram.\2', page, count=1, flags=re.S)

page = re.sub(r'<title>.*?</title>', '', page, count=1, flags=re.S)
head = '''<!doctype html>
<html lang="ru"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow,noarchive">
<meta name="description" content="Студия пилатеса и женского фитнеса на Новаторской. Версия сайта для обсуждения.">
<meta name="theme-color" content="#F2ECE2">
<title>Хочу абонемент · Новаторская — версия для обсуждения</title>
<style>body{margin:0}img{max-width:100%}[hidden]{display:none!important}
.review-notice{font:14px/1.45 Onest,system-ui,sans-serif;padding:10px 18px;background:#E0D2BF;color:#161310;text-align:center}
.review-credit{font:13px/1.5 Onest,system-ui,sans-serif;margin-top:16px}.review-credit a{color:inherit}
</style>
'''
cut = page.index('<div class="b" id="broot">')
page = head + page[:cut] + '</head><body>\n<aside class="review-notice">Версия для обсуждения. Расписание и контакты студии действующие.</aside>\n' + page[cut:]
page = page.replace('</footer>', '<p class="review-credit"><a href="credits.html">Авторы пиктограмм и шрифтов</a></p></footer>')
tail = (SRC / 'widget-tail.html').read_text()
page += '\n' + tail
assert not any(x in page for x in ['{{DOC:', '<!--WIDGET', '<!--MAP', 'fonts.googleapis.com', 'cdnjs.cloudflare.com'])
assert page.count('id="fitbaseWidgetContainer"') == 1
assert page.count('<html ') == page.count('</html>') == 1
(OUT / 'index.html').write_text(page)
(OUT / '.nojekyll').touch()
(OUT / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
print('Built docs/index.html:', len(page.encode()), 'bytes. Original v42 source preserved.')
