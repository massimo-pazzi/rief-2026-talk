"""Собирает страницу кейса index.html из report/case.md и расчётов scripts/model.py.

Места для инфографики отмечены в тексте комментариями <!-- fig:имя -->.
Данные для инфографики — в этом файле, у каждой цифры указан источник (список внизу страницы).
Запуск:  .venv/bin/python scripts/build_page.py
"""

import base64
import sys
from pathlib import Path

import json
import re
import markdown

ROOT = Path(__file__).resolve().parent.parent

MD = ROOT / "report" / "case.md"
OUT = ROOT / "index.html"
REPO = "https://github.com/massimo-pazzi/rief-2026-talk"
NEWS = "https://nanosemantics.ai/blog/807"


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def num(x):
    return f"{x:,.0f}".replace(",", " ")


def figure(title, body, note=""):
    n = f'<p class="note">{note}</p>' if note else ""
    return f'<figure class="chart"><figcaption class="chart-title">{title}</figcaption>{body}{n}</figure>'


def table(head, rows, cls=""):
    return (f'<div class="table-wrap"><table class="{cls}"><thead><tr>' + "".join(f"<th>{h}</th>" for h in head) +
            "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows) +
            "</tbody></table></div>")


def link(text, url):
    return f'<a href="{url}" target="_blank" rel="noopener">{text}</a>'




# ---------------------------------------------------------------- инфографика

def fig_photo():
    return ('<figure class="chart photo"><img src="assets/img/stage.jpg" alt="Максим Поципух выступает с докладом '
            '«Интерфейс энергетики будущего» на РМЭФ-2026" loading="lazy" width="1050" height="1400">'
            '<p class="note">Конференция «Взгляд в будущее: инновационные технологии и стартапы в энергетике», '
            f'РМЭФ-2026, Санкт-Петербург, 23 апреля 2026 года. {link("Новость о выступлении", NEWS)}.</p></figure>')


def slide(n, alt, note=""):
    def f():
        nt = f'<p class="note">{note}</p>' if note else ""
        return (f'<figure class="chart slide"><img src="assets/img/slide-{n}.jpg" alt="Слайд доклада: {esc(alt)}" '
                f'loading="lazy" width="1400" height="787">{nt}</figure>')
    return f


def fig_human():
    return ('<figure class="chart"><div class="callout"><p>Мы общаемся через <strong>речь, интонацию, мимику, жесты, '
            'контекст и паузы</strong>. Это и есть наш «родной интерфейс».</p>'
            '<p>По оценке Рэя Бёрдвистелла, невербальные каналы несут <strong>65–70% информации</strong> в живом общении. '
            'Это оценка, а не измерение, но вывод от процентов не зависит: человеческое общение мультимодально по своей природе.</p>'
            '</div></figure>')


def fig_value():
    return ('<figure class="chart"><div class="callout"><p><strong>Ключевой аргумент:</strong> чем больше объём автоматизации, '
            'тем выше концентрация ответственности у оставшихся людей — и тем критичнее качество их взаимодействия с системой.'
            '</p></div></figure>')


def fig_speech():
    rows = [("Классическая цепочка: распознать → понять → сгенерировать → озвучить", "800–2000+ мс",
             "Заметная, некомфортная пауза до первого звука ответа"),
            ("Аудио-нативные модели", "40–250 мс",
             "Ответ формируется по ходу фразы, намерение понимается по первым 300–500 мс речи"),
            ("Комфортный порог паузы в естественном разговоре", "менее 500 мс",
             "Средняя пауза между репликами у людей — около 200 мс")]
    return figure("Задержка до первого звука ответа", table(["", "Задержка", "Что это значит"], rows, "num txtlast"),
                  f'По слайду доклада; ориентиры — отраслевые обзоры голосовых моделей 2025–2026 годов '
                  f'({link("Inworld, март 2026", "https://inworld.ai/resources/best-speech-to-speech-apis")}) и '
                  f'{link("Stivers et al., PNAS, 2009", "https://www.pnas.org/doi/10.1073/pnas.0903616106")} о паузах между репликами.')


FIGS = {"photo": fig_photo,
        "slide03": slide("03", "сто лет эволюции интерфейса"),
        "slide04": slide("04", "поколения интерфейса 1–3"),
        "slide05": slide("05", "четвёртое поколение — цифровая эра и переход к ИИ-слою"),
        "human": fig_human,
        "slide07": slide("07", "мультимодальный интерфейс на объекте энергетики"),
        "value": fig_value,
        "speech": fig_speech,
        "slide11": slide("11", "контуры интерфейса пятого поколения"),
        "slide12": slide("12", "вызовы и барьеры"),
        "slide13": slide("13", "заключение"),
        "refs": None}


REFS = [
    ("Минэнерго о доле компаний ТЭК, применяющих ИИ (РИА Новости, 22.04.2025)", "https://ria.ru/20250422/predprijatija-2012798075.html"),
    ("«Коммерсантъ»: ИИ в энергетике, 30.10.2025", "https://www.kommersant.ru/doc/8161430"),
    ("«Коммерсантъ»: в условиях дефицита кадров, 22.12.2025", "https://www.kommersant.ru/doc/8294072"),
    ("«Страна Росатом»: к 2030 году в Росатоме будет 230 роботов на 10 тысяч сотрудников, 23.12.2025",
     "https://strana-rosatom.ru/2025/12/23/k-2030-godu-v-rosatome-budet-230-robotov-na-10/"),
    ("АО «СО ЕЭС»: история оперативно-диспетчерского управления", "https://www.so-ups.ru/about/history/1921-2002/"),
    ("АО «СО ЕЭС»: как менялись диспетчерские щиты", "https://www.so-ups.ru/news/smi/press-view/news/1517/"),
    ("Рэй Бёрдвистелл и оценка доли невербальной информации", "https://en.wikipedia.org/wiki/Ray_Birdwhistell"),
    ("Inworld: обзор голосовых моделей, март 2026", "https://inworld.ai/resources/best-speech-to-speech-apis"),
    ("Stivers et al. (2009): паузы между репликами в разговоре", "https://www.pnas.org/doi/10.1073/pnas.0903616106"),
    ("Kyutai Moshi: аудио-нативная голосовая модель", "https://arxiv.org/abs/2410.00037"),
    ("ФСТЭК о проверках объектов КИИ в 2025–2026 годах",
     "https://cisoclub.ru/fstjek-priznala-ujazvimost-bolshinstva-obektov-kriticheskoj-infrastruktury-i-gotovitsja-uzhestochit-kontrol"),
    ("«Наносемантика» на РМЭФ-2026", NEWS),
]


def fig_refs():
    return ('<ol class="sources">' + "".join(f"<li>{link(esc(t), u)}</li>" for t, u in REFS) + "</ol>"
            '<p class="note">Слайды — из презентации доклада. Цифры, которых нет на слайдах, сверены с первоисточниками.</p>')


FIGS["refs"] = fig_refs


def author_block():
    img = base64.b64encode((ROOT / "assets/img/author.jpg").read_bytes()).decode()
    return (f'<div class="author"><a href="https://massimo-pazzi.github.io/" title="Все кейсы автора"><img src="data:image/jpeg;base64,{img}" alt="Максим Поципух" width="64" height="64"></a>'
            '<span class="author-txt"><a class="author-name" href="https://massimo-pazzi.github.io/" title="Все кейсы автора">Максим Поципух</a><span class="author-links">Maxim Potsipukh · '
            '<a href="https://t.me/maxim_potsipukh" target="_blank" rel="noopener">Telegram</a> · '
            '<a href="https://max.ru/u/f9LHodD0cOI-rqGbPaCc2EshAXaEgw4ABwO8e2-ng4zK-otGeBnO04IzH5g" target="_blank" rel="noopener">Max</a></span></span></div>')

CSS = """
:root{
  --bg:#f5f6f7; --surface:#ffffff; --ink:#18202a; --ink-2:#4b5662; --muted:#6c7782;
  --rule:#d9dee3; --accent:#1f5fae; --accent-soft:#e6eef8; --neutral:#aab2bb;
  --s1:#2a78d6; --s2:#eb6834; --s3:#1baf7a; --s4:#a07800; --ok:#1b8a5a; --warn:#a36b00; --no:#8a929b;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){ color-scheme:dark;
    --bg:#11161c; --surface:#171d24; --ink:#e7ebef; --ink-2:#b5bec7; --muted:#8c96a0;
    --rule:#2c343d; --accent:#79a9e8; --accent-soft:#1c2632; --neutral:#5d6670;
    --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --ok:#3fbf86; --warn:#e0a640; --no:#7d8791; }
}
:root[data-theme="dark"]{ color-scheme:dark;
  --bg:#11161c; --surface:#171d24; --ink:#e7ebef; --ink-2:#b5bec7; --muted:#8c96a0;
  --rule:#2c343d; --accent:#79a9e8; --accent-soft:#1c2632; --neutral:#5d6670;
  --s1:#3987e5; --s2:#d95926; --s3:#199e70; --s4:#c98500; --ok:#3fbf86; --warn:#e0a640; --no:#7d8791; }
body{margin:0; background:var(--bg); color:var(--ink); font-family:"Golos Text",system-ui,-apple-system,"Segoe UI",sans-serif;
  font-size:17px; line-height:1.62; padding-inline:16px; padding-block:40px 64px;}
.page{max-width:48rem; margin:0 auto;} a{color:var(--accent);}
.eyebrow{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12.5px; letter-spacing:.06em; text-transform:uppercase; color:var(--accent); margin:0 0 14px;}
h1{font-size:clamp(1.7rem,4.2vw,2.3rem); line-height:1.18; font-weight:700; letter-spacing:-.01em; text-wrap:balance; margin:0 0 16px;}
h2{font-size:1.28rem; line-height:1.3; font-weight:650; text-wrap:balance; margin:46px 0 12px; padding-top:22px; border-top:1px solid var(--rule);}
.author{display:flex; align-items:center; gap:12px; margin:4px 0 16px; font-weight:600; font-size:15px;}
.author img{width:64px; height:64px; border-radius:50%; object-fit:cover; border:1px solid var(--rule);}
.author-txt{display:flex; flex-direction:column; gap:2px;} .author-name{color:inherit; text-decoration:none;} .author-name:hover{color:var(--accent); text-decoration:underline;} .author a img{display:block;} .author-links{font-weight:400; font-size:13.5px; color:var(--muted);} .author-links a{color:var(--accent);}
.author + p em{color:var(--ink-2); font-size:15px;}
p{margin:0 0 14px;} strong{font-weight:620;} hr{display:none;}
.chart{margin:16px 0 22px; background:var(--surface); border:1px solid var(--rule); border-radius:6px; padding:14px 16px 12px;}
.chart-title{font-weight:600; font-size:14.5px; margin-bottom:10px; line-height:1.4;}
.note{font-size:12.5px; color:var(--muted); margin:10px 0 0; line-height:1.5;}
.flow{display:grid; grid-template-columns:1fr auto 1fr auto 1fr auto 1fr; gap:8px; align-items:stretch;}
.flow-col{border:1px solid var(--rule); border-radius:6px; padding:10px 12px; font-size:13px; line-height:1.45;} .flow-col p{margin:0;}
.flow-h{font-weight:650; font-size:12.5px; text-transform:uppercase; letter-spacing:.04em; color:var(--ink-2); margin-bottom:6px;}
.flow-col.core{background:var(--accent-soft); border-color:var(--accent);} .flow-col.core .flow-h{color:var(--accent);}
.arrow{align-self:center; color:var(--muted); font-size:20px;}
@media (max-width:700px){ .flow{grid-template-columns:1fr;} .arrow{transform:rotate(90deg); justify-self:center;} }
.funnel{display:grid; gap:8px;}
.fn-row{display:grid; grid-template-columns:1fr 1fr; gap:12px; align-items:center;}
.fn-bar{box-sizing:border-box; max-width:100%; background:var(--s1); color:#fff; border-radius:4px; padding:7px 10px; font-weight:600; font-size:14px; min-width:9em; justify-self:end;}
.fn-row:last-child .fn-bar{background:var(--s2);}
.fn-l{font-size:13.5px; line-height:1.35;} .fn-l span{display:block; color:var(--muted); font-size:12.5px;}
.table-wrap{overflow-x:auto;}
table{border-collapse:collapse; width:100%; font-size:14px;}
th,td{text-align:left; padding:8px 10px 8px 0; border-bottom:1px solid var(--rule); vertical-align:top;}
th{font-weight:600; color:var(--ink-2); font-size:12.5px;}
.matrix td:first-child{font-weight:550; min-width:11em;} .matrix th:last-child,.matrix td:last-child{background:var(--accent-soft); padding-left:8px;}
.price td:last-child{text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap;}
.y{color:var(--ok); font-weight:600;} .p{color:var(--warn); font-weight:600;} .n{color:var(--no);}
.steps{margin:0; padding-left:1.4em; columns:2; column-gap:28px; font-size:14px;} .steps li{margin-bottom:6px; break-inside:avoid;}
@media (max-width:640px){ .steps{columns:1;} }
.pairs{display:grid; gap:12px;}
.pair{display:grid; grid-template-columns:minmax(9em,13em) 1fr; gap:12px; align-items:center; font-size:13.5px;}
.pr-l span{display:block; color:var(--muted); font-size:12px;}
.pr-bars{display:grid; gap:4px;}
.pb{display:flex; align-items:center; gap:8px; font-size:12.5px; font-variant-numeric:tabular-nums;} .pb span{white-space:nowrap;}
.bar{height:14px; border-radius:3px; min-width:3px;} .bar.s1{background:var(--s1);} .bar.s2{background:var(--s2);}
.legend{display:flex; flex-wrap:wrap; gap:6px 16px; font-size:12.5px; color:var(--ink-2); margin-top:12px;}
.legend span{display:inline-flex; align-items:center; gap:6px;} .sw{display:inline-block; width:11px; height:11px; border-radius:2px;}
.sw.s1{background:var(--s1);} .sw.s2{background:var(--s2);}
.chart-scroll{overflow-x:auto;} .chart svg{display:block; width:100%; min-width:560px; height:auto;}
.grid{stroke:var(--rule); stroke-width:1;} .tick{fill:var(--muted); font-size:11px; font-family:"IBM Plex Mono",ui-monospace,monospace;}
.target{stroke:var(--ink-2); stroke-width:1.2; stroke-dasharray:5 4;} .median{stroke:var(--muted); stroke-width:1; stroke-dasharray:2 3;}
.band-label{fill:var(--muted); font-size:11px;} .label{fill:var(--ink); font-size:12px;}
.line{fill:none; stroke-width:2.2;} .line.s1{stroke:var(--s1);} .line.s2{stroke:var(--s2);} .line.s3{stroke:var(--s3);} .line.s4{stroke:var(--s4);}
.dot{stroke:var(--surface); stroke-width:2;} .dot.s1{fill:var(--s1);} .dot.s2{fill:var(--s2);} .dot.s3{fill:var(--s3);} .dot.s4{fill:var(--s4);}
.kpis{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:10px; margin-bottom:12px;}
.kpi{border:1px solid var(--rule); border-radius:6px; padding:12px 14px;}
.kpi-v{font-size:1.4rem; font-weight:700; font-variant-numeric:tabular-nums;} .kpi-l{font-size:13px; color:var(--ink-2); margin-top:4px; line-height:1.4;}
.gap{height:14px;}
.rel{margin-bottom:14px;} .rel-h{font-weight:620; font-size:13.5px; margin:4px 0 8px; color:var(--accent);} .rel0 .rel-h{color:var(--ink-2);}
.num td:not(:first-child),.num th:not(:first-child){text-align:right; font-variant-numeric:tabular-nums;}
.txtlast td:last-child,.txtlast th:last-child{text-align:left;}
.dl-link{margin:-12px 0 22px; font-size:13.5px;}
.chart.live iframe{display:block; width:100%; border:0; border-radius:4px; background:#fff;}
.sources{font-size:14.5px; line-height:1.55; padding-left:1.5em;}
@media (max-width:520px){ body{font-size:16px; padding-block:24px 48px;} .pair,.fn-row{grid-template-columns:1fr;} .fn-bar{justify-self:start;} }
.ranges{display:grid; gap:7px;}
.rg{display:grid; grid-template-columns:minmax(10em,16em) 1fr; gap:12px; align-items:center; font-size:13.5px;}
.rg-bar{display:flex; align-items:center; gap:0; font-size:12.5px; font-variant-numeric:tabular-nums;}
.rg-lo{height:14px; background:var(--s1); border-radius:3px 0 0 3px;} .rg-hi{height:14px; background:var(--s1); opacity:.35; border-radius:0 3px 3px 0;}
.rg-bar span{margin-left:8px; white-space:nowrap;} .sw.s1l{background:var(--s1); opacity:.35;}
.cols3{display:grid; grid-template-columns:repeat(3,1fr); gap:10px;}
.c3{border:1px solid var(--rule); border-radius:6px; padding:10px 12px; font-size:13.5px; line-height:1.45;}
.c3 ul{margin:0; padding-left:1.1em;} .c3 li{margin-bottom:4px;}
.c3.core{background:var(--accent-soft); border-color:var(--accent);} .c3.core .flow-h{color:var(--accent);}
.tiles{display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:10px;}
.tile{border:1px solid var(--rule); border-radius:6px; padding:10px 12px; font-size:13px; line-height:1.4;}
.tile-n{font-size:1.5rem; font-weight:700; color:var(--accent); font-variant-numeric:tabular-nums;}
.tile-h{font-weight:620; margin:2px 0;} .tile-s{color:var(--ink-2); font-size:12.5px;} .tile-e{color:var(--muted); font-size:12px; margin-top:4px;}
.num td:not(:first-child),.num th:not(:first-child){text-align:right; font-variant-numeric:tabular-nums;}
.txtlast td:last-child,.txtlast th:last-child{text-align:left;}
@media (max-width:640px){ .cols3{grid-template-columns:1fr;} .rg{grid-template-columns:1fr; gap:4px;} }
.photo img,.slide img{display:block; width:100%; height:auto; border-radius:4px;}
.slide{padding:8px;}
.callout{background:var(--accent-soft); border-radius:6px; padding:14px 16px; font-size:15px;} .callout p{margin:0 0 8px;} .callout p:last-child{margin:0;}
.gens{display:grid; grid-template-columns:repeat(3,1fr); gap:10px;}
.gen{border:1px solid var(--rule); border-radius:6px; padding:10px 12px; font-size:13px; line-height:1.45;} .gen p{margin:4px 0 0;}
.gen-n{font-size:1.5rem; font-weight:700; color:var(--accent); font-variant-numeric:tabular-nums;}
.gen-y{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:11.5px; color:var(--muted);}
.gen-h{font-weight:650; text-transform:uppercase; letter-spacing:.04em; font-size:12.5px; margin-top:4px;}
.gen.next{background:var(--accent-soft); border-color:var(--accent);} .gen.next .gen-h{color:var(--accent);}
.cards{display:grid; grid-template-columns:repeat(3,1fr); gap:10px;} .cards5{grid-template-columns:repeat(5,1fr);}
.card{border:1px solid var(--rule); border-radius:6px; padding:10px 12px; font-size:13px; line-height:1.45;} .card p{margin:0;}
.rg-lo.fc{opacity:.45;} .muted{color:var(--muted); font-size:12px;}
.talk{list-style:none; margin:0; padding:0; display:grid; gap:6px;}
.talk li{display:grid; grid-template-columns:5.5em 11em 1fr; gap:12px; font-size:13.5px; padding:6px 0; border-bottom:1px solid var(--rule);}
.tk-m{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:12px; color:var(--accent);} .tk-h{font-weight:620;}
@media (max-width:760px){ .cards5{grid-template-columns:repeat(2,1fr);} }
@media (max-width:640px){ .gens,.cards,.cards5{grid-template-columns:1fr;} .talk li{grid-template-columns:1fr; gap:2px;} }
"""


# Блок «Другие кейсы автора» — одинаковый во всех кейсах портфолио, ставится над источниками.
OTHER_CASES = [
    ("hotel-market-case", "Анализ рынка", "Рост цен в отелях Петербурга перестал окупаться"),
    ("housing-digital-twin-case", "Новый продукт", "Цифровой двойник жилого фонда Москвы: от аварийного ремонта к прогнозу поломок"),
    ("b2b-value-case", "Обоснование проекта", "Как доказать окупаемость ИИ-проекта, не зная маржи заказчика"),
    ("fastfood-assistant-case", "Продукт с ИИ", "ИИ-ассистент для федеральной сети быстрого питания: как спроектировать продукт не имея данных заказчика"),
    ("rief-2026-talk", "Стратегия и аналитика рынка", "Интерфейс энергетики будущего: доклад на РМЭФ-2026"),
    ("wine-ai-case", "Категорийный маркетинг", "ИИ-сомелье для сети супермаркетов: при каких условиях он может окупиться"),
]


def other_cases(current):
    tiles = "".join(
        f'<a class="oc-tile" href="https://massimo-pazzi.github.io/{slug}/"><span class="oc-tag">{tag}</span>'
        f'<span class="oc-title">{title}</span><span class="oc-go">Открыть кейс →</span></a>'
        for slug, tag, title in OTHER_CASES if slug != current)
    style = ("<style>.oc-grid{display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:10px; margin:12px 0 8px;}"
             ".oc-tile{display:flex; flex-direction:column; gap:6px; padding:14px 16px; background:var(--surface); border:1px solid var(--rule);"
             " border-radius:6px; text-decoration:none; color:inherit;} .oc-tile:hover{border-color:var(--accent);}"
             ".oc-tag{font-size:12px; letter-spacing:.04em; text-transform:uppercase; color:var(--accent);}"
             ".oc-title{font-weight:600; font-size:15px; line-height:1.35;} .oc-go{margin-top:auto; font-size:13px; color:var(--accent);}</style>")
    return f'{style}<h2>Другие кейсы автора</h2><div class="oc-grid">{tiles}</div>\n'


# SEO: заголовок, описание, автор, canonical, Open Graph и JSON-LD — одинаково во всех кейсах портфолио.
AUTHOR = {"@type": "Person", "name": "Максим Поципух", "alternateName": "Maxim Potsipukh",
          "sameAs": ["https://t.me/maxim_potsipukh",
                     "https://max.ru/u/f9LHodD0cOI-rqGbPaCc2EshAXaEgw4ABwO8e2-ng4zK-otGeBnO04IzH5g",
                     "https://github.com/massimo-pazzi"]}
OG_IMAGE = "https://massimo-pazzi.github.io/rief-2026-talk/assets/img/og.jpg"
SEO = {
    "hotel-market-case": ("Гостиничный рынок Петербурга — Максим Поципух",
                          "Рост цен в отелях Петербурга перестал окупаться",
                          "Исследование Максима Поципуха по открытым данным: почему рост цен в отелях Петербурга "
                          "перестал окупаться — спрос и номерной фонд, сезонность, сегменты, города и прогноз."),
    "housing-digital-twin-case": ("Цифровой двойник ЖКХ — Максим Поципух",
                                  "Цифровой двойник жилого фонда Москвы: от аварийного ремонта к прогнозу поломок",
                                  "Продуктовый кейс Максима Поципуха: цифровой двойник жилого фонда Москвы и прогноз "
                                  "отказов инженерных систем домов — для кого продукт, метрики, прототип, этапы внедрения."),
    "b2b-value-case": ("Окупаемость без маржи — Максим Поципух",
                       "Как доказать окупаемость ИИ-проекта, не зная маржи заказчика",
                       "Кейс Максима Поципуха: обоснование ИИ-проекта для грузовой авиакомпании — цена бездействия, "
                       "две картины ценности и пороговая маржа, которую заказчик проверяет сам."),
    "fastfood-assistant-case": ("ИИ-ассистент без данных — Максим Поципух",
                                "ИИ-ассистент для федеральной сети быстрого питания: как спроектировать продукт не имея данных заказчика",
                                "Продуктовый кейс Максима Поципуха: ИИ-ассистент в приложении федеральной сети быстрого "
                                "питания — темы обращений, границы продукта, очерёдность релизов, нагрузка, экономика и риски."),
    "wine-ai-case": ("ИИ-сомелье для сети супермаркетов — Максим Поципух",
                     "ИИ-сомелье для сети супермаркетов: при каких условиях он может окупиться",
                     "Кейс Максима Поципуха по категорийному маркетингу: ИИ-консультант по вину для сети супермаркетов — "
                     "объём категории, эффект в выручке и в марже с учётом охвата, порог окупаемости, правовые ограничения и MVP."),
    "rief-2026-talk": ("Интерфейс энергетики будущего — Максим Поципух",
                       "Интерфейс энергетики будущего: доклад на РМЭФ-2026",
                       "Доклад Максима Поципуха на Российском международном энергетическом форуме 2026: как "
                       "искусственный интеллект меняет взаимодействие человека с энергетической инфраструктурой."),
}


def seo_head(slug):
    title, headline, desc = SEO[slug]
    url = f"https://massimo-pazzi.github.io/{slug}/"
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": headline, "description": desc,
          "inLanguage": "ru", "url": url, "mainEntityOfPage": url, "image": OG_IMAGE, "author": AUTHOR}
    q = lambda t: t.replace("&", "&amp;").replace('"', "&quot;")
    return (f'<title>{title}</title>\n'
            f'<meta name="description" content="{q(desc)}">\n'
            f'<meta name="author" content="Максим Поципух (Maxim Potsipukh)">\n'
            f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="article">\n'
            f'<meta property="og:locale" content="ru_RU">\n'
            f'<meta property="og:site_name" content="Максим Поципух — портфолио">\n'
            f'<meta property="og:title" content="{q(title)}">\n'
            f'<meta property="og:description" content="{q(desc)}">\n'
            f'<meta property="og:url" content="{url}">\n'
            f'<meta property="og:image" content="{OG_IMAGE}">\n'
            f'<meta name="twitter:card" content="summary_large_image">\n'
            f'<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>')


def apply_seo(page, slug):
    """Заменяет <title> и description страницы на SEO-блок."""
    page = re.sub(r'<meta name="description" content="[^"]*">\n?', "", page)
    return re.sub(r"<title>[^<]*</title>", lambda m: seo_head(slug), page, count=1)


def main():
    html = markdown.markdown(MD.read_text(encoding="utf-8"), extensions=["tables"])
    title, rest = html.split("</h1>", 1)
    html = title + "</h1>\n" + author_block() + rest
    for name, fn in FIGS.items():
        marker = f"<!-- fig:{name} -->"
        assert marker in html, f"нет места для блока {name}"
        html = html.replace(marker, fn())
    page = f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Интерфейс энергетики будущего</title>
<meta name="description" content="Портфолио-кейс по стратегии и аналитике рынка: аналитическая записка и доклад на РМЭФ-2026 о том, как ИИ меняет интерфейс между человеком и энергетической инфраструктурой">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Golos+Text:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
</head>
<body>
<main class="page">
<p class="eyebrow">Портфолио-кейс: стратегия и аналитика рынка · Максим Поципух · Апрель 2026</p>
{html}
</main>
</body>
</html>
"""
    page = page.replace("<h2>Источники</h2>", other_cases("rief-2026-talk") + "<h2>Источники</h2>", 1)
    page = apply_seo(page, "rief-2026-talk")
    OUT.write_text(page, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(page) // 1024} КБ, блоков: {len(FIGS)}")


if __name__ == "__main__":
    main()
