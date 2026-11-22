"""Build the first-visit experiment beside the approved review page."""
from pathlib import Path
import re

root = Path(__file__).resolve().parent
page = (root / 'docs/editorial.html').read_text()
title = 'Пилатес и женский фитнес <span class="b-em">у метро Новаторская</span>'
lead = '<p class="b-lede">Неважно, сколько вам лет и занимались ли вы раньше.</p><p class="trial-line">Пробное на коврике · 1 000 ₽ · 55 минут</p>'
for hero in ['b-hero2', 'b-hero']:
    match = re.search(r'<section class="[^"]*\b' + hero + r'">.*?</section>', page, re.S)
    body = re.sub(r'(<h[12] class="b-d1[^"]*">).*?(</h[12]>)', lambda m:m[1]+title+m[2], match[0], flags=re.S)
    body = re.sub(r'<p class="b-lede[^"]*">.*?</p>(?:\s*<p class="b-lede[^"]*">.*?</p>)?', lead, body, count=1, flags=re.S)
    section = 's-try' if hero=='b-hero2' else 'probnye'
    body = re.sub(r'<button class="b-btn" type="button" data-open-sheet data-offer="Пробное занятие">.*?</button>', f'<a class="b-btn" href="#{section}">Выбрать пробное</a>', body, count=1)
    page = page[:match.start()] + body + page[match.end():]

chooser = """<div class="visit-choice">
<h2 class="b-d1">С чего начать знакомство</h2>
<div class="visit-grid"><div><div class="formats" role="group" aria-label="Формат пробного">
<button type="button" data-format="mat" aria-pressed="true">На коврике</button><button type="button" data-format="ref" aria-pressed="false">На реформере</button></div>
<p class="visit-desc"></p></div>
<div class="visit-order"><fieldset><legend>Количество занятий</legend><div class="counts"></div></fieldset>
<div aria-live="polite"><strong class="visit-price"></strong><p class="visit-terms"></p></div>
<button type="button" class="b-btn" data-open-sheet>Записаться на пробное</button></div></div></div>"""
for section in ['s-try','probnye']:
    m = re.search(r'<section[^>]*id="'+section+r'".*?</section>',page,re.S)
    start=m[0].index('<div class="b-head">')
    result=m[0][:start]+chooser+'</div></section>'
    if section=='s-try':
        result=result.replace('b-mblk b-s','b-s',1)
        page=page[:m.start()]+'</div>'+result+page[m.end():].replace('</div>','',1)
    else:
        page=page[:m.start()]+result+page[m.end():]
page=page.replace("'#pervoe .b-steps',",'').replace('#probnye .b-trylab','#probnye .visit-choice')
page=page.replace('Вариант оформления · <a href="compare.html">Было — стало</a> · <a href="index.html#full">Прежний сайт</a>', 'Пробный вариант · <a href="editorial.html#full">Было</a>')
# Keep the mat selection explicit when the existing form updates its quantity.
for count, label in enumerate(['1 пробное занятие', '2 пробных занятия', '3 пробных занятия'], 1):
    old = f"'{count}':'{label}, {count} 000 ₽'"
    page = page.replace(old, old.replace(', ', ' на коврике, '))
for tag, filename, closing in [('style','visit.css','</head>'),('script','visit.js','</body>')]:
    page=page.replace(closing,f'<{tag}>\n'+(root/'src'/filename).read_text()+f'\n</{tag}>'+closing)
(root/'docs/visit.html').write_text(page)
