"""An isolated layout variant, assembled from the exact current review page."""
from pathlib import Path
import re
import shutil
import hashlib

ROOT = Path(__file__).resolve().parent

def render_variant(page):
    variant = page.replace('class="b" id="broot"', 'class="b b-editorial" id="broot"', 1)
    assert variant != page
    css_version = hashlib.sha256((ROOT / 'src/editorial.css').read_bytes()).hexdigest()[:12]
    variant = variant.replace('</head>', '<link rel="stylesheet" href="assets/editorial.css?v=' + css_version + '">\n</head>', 1)
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
    # Retain the complete original desktop chapter, including its cards and typography.
    # Only add the previously approved mobile accordion.
    new_team = team.replace('</section>', '<div class="b-w e-mobile-principles"><div class="e-principles">' + principles + '</div></div></section>')
    variant = re.sub(team_re, lambda m: new_team, variant, count=1, flags=re.S)

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
