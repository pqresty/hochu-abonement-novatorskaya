"""An isolated layout variant, assembled from the exact current review page."""
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent

def render_variant(page):
    variant = page.replace('class="b" id="broot"', 'class="b b-editorial" id="broot"', 1)
    assert variant != page
    variant = variant.replace('</head>', '<link rel="stylesheet" href="assets/editorial.css">\n</head>', 1)
    variant = variant.replace('Версия для обсуждения. Расписание и контакты студии действующие.',
        'Вариант оформления · <a href="compare.html">Было — стало</a> · <a href="index.html#full">Прежний сайт</a>')
    variant = variant.replace('<div class="b-post">', '<div class="b-post e-notes">', 1)

    # Keep texts byte-for-byte; change only their arrangement.
    team_re = r'<section\b[^>]*\bid="komanda"[^>]*>.*?</section>'
    team = re.search(team_re, variant, re.S).group()
    title = re.search(r'<h2 class="b-d1">(.*?)</h2>', team, re.S)[1]
    intro = re.search(r'<p class="b-p b-mut">(.*?)</p>', team, re.S)[1]
    items = re.findall(r'<div><h3>(.*?)</h3><p>(.*?)</p></div>', team, re.S)
    assert len(items) == 6
    principles = ''.join(
        '<details class="e-principle" open><summary><h3>' + h + '</h3><span aria-hidden="true"></span></summary><div><p>' + p + '</p></div></details>'
        for h, p in items)
    new_team = ('<section class="b-s e-team" id="komanda"><div class="b-w e-teamgrid">'
        '<div class="b-head"><h2 class="b-d1">' + title + '</h2><p class="b-p b-mut">' + intro + '</p></div>'
        '<div class="e-principles">' + principles + '</div></div></section>')
    variant = re.sub(team_re, lambda m: new_team, variant, count=1, flags=re.S)

    footers = list(re.finditer(r'<footer class="b-w">.*?</footer>', variant, re.S))
    assert len(footers) == 2
    map_link = re.search(r'href="(https://yandex.ru/maps[^\"]+)"', variant)[1]
    max_link = re.search(r'href="(https://max.ru/[^\"]+)"', variant)[1]
    replacements = []
    for i, match in enumerate(footers):
        old = match.group()
        doc_links = re.findall(r'<a href="(https://disk.yandex.ru/[^\"]+)"[^>]*>(.*?)</a>', old, re.S)
        assert len(doc_links) == 4
        theme = re.search(r'<button class="b-thm b-thm--txt".*?</button>', old, re.S).group()
        schedule = '#s-rasp' if i == 0 else '#raspisanie'
        documents = ''.join('<a href="' + href + '" target="_blank" rel="noopener">' + label + '</a>' for href, label in doc_links)
        new = f'''<footer class="e-footer"><div class="b-w">
          <div class="e-footbrand">
            <a class="b-logo e-footlogo" href="#" data-go="fork" aria-label="Хочу абонемент, к началу сайта"><svg class="b-mark" aria-hidden="true" focusable="false"><use href="#hb-mark"/></svg></a>
            {theme}
          </div>
          <div class="e-footgrid">
            <section><h2>Как дойти</h2><p class="e-footlead">Москва,<br>Ленинский проспект, 95Б</p><p>Метро Новаторская,<br>выход №7, минута пешком</p><a class="e-footlink" href="{map_link}" target="_blank" rel="noopener">Открыть маршрут</a></section>
            <section><h2>Когда прийти</h2><p class="e-foothours">9:00–22:00</p><p>Занятия по<br>предварительной записи</p><a class="b-btn e-footschedule" href="{schedule}">Расписание</a></section>
            <section><h2>Связаться</h2><a class="e-footphone" href="tel:+79660863057">+7 966 086 30 57</a><div class="e-footmessengers"><a href="https://t.me/FlowAndCore" target="_blank" rel="noopener">Telegram</a><a href="{max_link}" target="_blank" rel="noopener">MAX</a></div><a class="e-footemail" href="mailto:novatorskaya@hochuabonement.ru">novatorskaya@hochuabonement.ru</a><div class="e-footstores"><a href="https://apps.apple.com/us/app/flexifit/id1619190163" target="_blank" rel="noopener">App Store</a><a href="https://play.google.com/store/apps/details?id=io.fitbase.flexifit" target="_blank" rel="noopener">Google Play</a></div></section>
            <section class="e-footdocs"><h2>Документы</h2>{documents}</section>
          </div>
          <div class="e-footlegal"><p>ИП Малышев Михаил Евгеньевич<br>ИНН 773601148434 · ОГРНИП 326508100266347</p><a href="credits.html">Авторы пиктограмм и шрифтов</a></div>
        </div></footer>'''
        replacements.append((match.start(), match.end(), new))
    for start, end, new in reversed(replacements):
        variant = variant[:start] + new + variant[end:]

    # Native accordion on phones; all principles open on desktop.
    script = '''<script>
    (function(){
      var media=matchMedia('(max-width:760px)');
      var rows=[].slice.call(document.querySelectorAll('.e-principle'));
      function layout(){ rows.forEach(function(row,i){row.open=!media.matches||i===0;}); }
      rows.forEach(function(row){
        row.querySelector('summary').addEventListener('click',function(e){if(!media.matches)e.preventDefault();});
        row.addEventListener('toggle',function(){if(media.matches&&row.open)rows.forEach(function(other){if(other!==row)other.open=false;});});
      });
      if(media.addEventListener)media.addEventListener('change',layout);else media.addListener(layout);
      layout();
    })();
    </script>'''
    variant = variant.replace('</body>', script + '\n</body>', 1)
    (ROOT / 'docs/editorial.html').write_text(variant)
    shutil.copy2(ROOT / 'src/editorial.css', ROOT / 'docs/assets/editorial.css')
    print('Built docs/editorial.html:', len(variant.encode()), 'bytes.')
