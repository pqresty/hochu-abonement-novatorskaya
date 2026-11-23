"""Build editor-sized Tilda markup and versioned assets from the approved preview."""
from pathlib import Path
import hashlib
import json
import re

dest = Path(__file__).resolve().parent
docs = dest.parent / 'docs'
approved = (docs / 'editorial.html').read_text()
asset_root = 'https://pqresty.github.io/hochu-abonement-novatorskaya/'
assets = docs / 'tilda'
assets.mkdir(exist_ok=True)

styles = approved.split('<style>', 2)[2].split('</style>', 1)[0]
body = approved[approved.index('<div class="b b-editorial" id="broot">'):approved.rindex('</body>')]
styles = styles.replace("url('assets/fonts/", "url('../assets/fonts/")
body = body.replace('src="photos/', f'src="{asset_root}photos/')
body = body.replace('href="credits.html"', f'href="{asset_root}credits.html"')
body, form_count = re.subn(r'\s*<form id="bform"[^>]*>.*?</form>', '', body, count=1, flags=re.S)
body, handler_count = re.subn(
    r"    var agree=document.getElementById\('bagree'\).*?(?=    var foot=document.querySelector)",
    '', body, count=1, flags=re.S,
)
assert form_count == handler_count == 1
body = re.sub(
    r'<p class="b-note" id="bnote">.*?</p>',
    '<p class="b-note" id="bnote">Чтобы записаться, позвоните или напишите нам в Telegram.</p>',
    body, count=1, flags=re.S,
)

# Keep page text in the T123 block. Large decorative SVGs and runtime code
# load from static files because the editor limits each block's saved length.
svg_by_placeholder = {}
def externalize_svg(match):
    svg = match[0]
    if len(svg) < 1000:
        return svg
    placeholder = f'novatorskaya-svg-{len(svg_by_placeholder)}'
    svg_by_placeholder[placeholder] = svg
    return f'<!--{placeholder}-->'

body = re.sub(r'<svg\b.*?</svg>', externalize_svg, body, flags=re.S)
scripts = []
def place_script(match):
    if match[1]:
        return match[0].replace('src="assets/', f'src="{asset_root}assets/')
    scripts.append(match[2])
    return ''

body = re.sub(r'<script([^>]*)>(.*?)</script>', place_script, body, flags=re.S)
assert len(scripts) == 4
init, site, widget_skin, mobile_principles = scripts
art = f"""
(function () {{
    const artwork = {json.dumps(svg_by_placeholder, ensure_ascii=False)};
    const comments = document.createTreeWalker(document.getElementById('broot'), NodeFilter.SHOW_COMMENT);
    const placeholders = [];
    while (comments.nextNode()) {{
        if (Object.hasOwn(artwork, comments.currentNode.data)) placeholders.push(comments.currentNode);
    }}
    for (const node of placeholders) {{
        const range = document.createRange();
        range.selectNode(node);
        node.replaceWith(range.createContextualFragment(artwork[node.data]));
    }}
}})();
"""
# Keep version selection in the root so the chosen view is visible before the scripts finish.
body = body.replace('id="broot">', 'id="broot"><script>' + init + '</script>', 1)
body = re.sub(r'<!--(?!novatorskaya-svg-).*?-->', '', body, flags=re.S)
body = re.sub(r'(?m)^[ \t]+(?=<)', '', body)
scope = """
#broot [hidden]{display:none!important}
#broot img{max-width:100%}
#broot .review-credit{font:13px/1.5 Onest,system-ui,sans-serif;margin-top:16px}
#broot .review-credit a{color:inherit}
#broot #btf .t-rec{padding:0!important}
"""
css = styles + '\n' + (docs / 'assets/editorial.css').read_text() + scope
js = art + site + '\n' + widget_skin + '\n' + mobile_principles
release = hashlib.sha256((body + css + js).encode()).hexdigest()[:12]
css_name = f'novatorskaya-{release}.css'
js_name = f'novatorskaya-{release}.js'
(assets / css_name).write_text(css)
(assets / js_name).write_text(js)
fragment = f'<link rel="stylesheet" href="{asset_root}tilda/{css_name}">\n{body}'
fragment += f'\n<script src="{asset_root}tilda/{js_name}" defer></script>\n'
assert fragment.count('id="fitbaseWidgetContainer"') == 1
assert 'id="bform"' not in fragment and 'mailto:novatorskaya@hochuabonement.ru?subject' not in js
assert 'chto_vybrali' in js and len(json.dumps(fragment, ensure_ascii=False)) < 119000
(dest / 'block-T123.html').write_text(fragment)
print(f'T123: {len(fragment):,} chars, assets {release}')
