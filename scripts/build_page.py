"""Собирает страницу кейса index.html из report/case.md и расчётов scripts/model.py.

Места для инфографики отмечены в тексте комментариями <!-- fig:имя -->.
Данные для инфографики — в этом файле, у каждой цифры указан источник (список внизу страницы).
Запуск:  .venv/bin/python scripts/build_page.py
"""

import base64
import sys
from pathlib import Path

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
            '<p class="note">Доклад на конференции «Взгляд в будущее: инновационные технологии и стартапы в энергетике», '
            f'РМЭФ-2026, Санкт-Петербург, 23 апреля 2026 года. {link("Новость о выступлении", NEWS)}.</p></figure>')


GENERATIONS = [
    ("0", "до конца 1920-х", "Присутствие", "Человек у установки: стрелочные приборы, бумажный журнал, доклад голосом или телеграфом"),
    ("1", "1920-е — 1950-е", "Пространство", "Телефон, частотомер и первый диспетчерский щит из фанеры с мнемосхемой: система видна целиком"),
    ("2", "1960-е — 1980-е", "Время", "Мозаичные щиты, ОАСУ «Энергия» (1971), первые АСУ ТП: архив и динамика вместо моментального снимка"),
    ("3", "1990-е — 2010-е", "Гибкость", "Экранный интерфейс и SCADA, видеостены: картину можно перестроить под задачу за секунды"),
    ("4", "2010-е — сейчас", "Интеллект", "Предиктивная аналитика, цифровые двойники: система находит аномалии и подсказывает действия"),
    ("5", "горизонт 5–10 лет", "Диалог", "С системой разговаривают голосом и показывают ей оборудование — слой поверх всех предыдущих"),
]


def fig_generations():
    html = '<div class="gens">' + "".join(
        f'<div class="gen{" next" if n == "5" else ""}"><div class="gen-n">{n}</div><div class="gen-y">{esc(y)}</div>'
        f'<div class="gen-h">{esc(h)}</div><p>{esc(t)}</p></div>' for n, y, h, t in GENERATIONS) + "</div>"
    return figure("Пять поколений интерфейса энергосистемы и шестое на горизонте: что добавило каждое", html,
                  "По материалам АО «СО ЕЭС» об истории диспетчерского управления; поколение 5 — прогноз доклада.")


def cards(items, cls="cards"):
    return f'<div class="{cls}">' + "".join(
        f'<div class="card"><div class="flow-h">{esc(h)}</div><p>{esc(t)}</p></div>' for h, t in items) + "</div>"


def fig_tasks():
    return figure("Три задачи, под которые SCADA не проектировалась", cards([
        ("Кадровый разрыв", "Опытных диспетчеров всё меньше, подготовка нового занимает годы. SCADA показывает процесс, но не учит."),
        ("Работа в поле", "На подстанции, на высоте, в шумном цеху нет экрана и свободных рук — только бумажный чек-лист и рация."),
        ("Смысловая связка систем", "API связывают платформы технически, но соединить сигнал аналитики со складом запчастей и графиком ремонтов "
                                    "по-прежнему приходится человеку."),
    ]))


def fig_channels():
    return figure("Мультимодальный интерфейс на объекте энергетики: пять каналов", cards([
        ("Голос", "Основной канал запроса: «Покажи состояние турбины № 4 за последние 6 часов»."),
        ("Слух", "Ответ звучит в гарнитуре во время обхода, когда руки заняты, а глаза смотрят на оборудование."),
        ("Зрение", "Камера смартфона или AR-очков узнаёт агрегат и накладывает историю и прогноз."),
        ("Контекст", "Система знает роль спрашивающего и место, откуда задан вопрос."),
        ("Диалог", "Не команды, а разговор: «А что там было в августе?» понимается в контексте прошлого вопроса."),
    ], "cards cards5"))


ADOPTION = [("2021", 29, False), ("2024", 58, False), ("2027", 70, True)]
KOMMERSANT = "https://www.kommersant.ru/doc/8161430"


def fig_adoption():
    html = '<div class="ranges">' + "".join(
        f'<div class="rg"><div class="rg-l">{y}{" — прогноз" if f else ""}</div><div class="rg-bar">'
        f'<div class="rg-lo{" fc" if f else ""}" style="width:{v}%; border-radius:3px"></div><span>{v}%</span></div></div>'
        for y, v, f in ADOPTION) + "</div>"
    return figure("Доля компаний ТЭК, которые применяют ИИ", html,
                  f'Минэнерго России, по данным «{link("Коммерсанта", KOMMERSANT)}» (30.10.2025) и '
                  f'{link("РИА Новости", "https://ria.ru/20250422/predprijatija-2012798075.html")} (22.04.2025).')


def fig_scenarios():
    rows = [("<strong>Диалоговая надстройка в диспетчерской</strong>",
             "«Покажи объекты с аномалиями за сутки и отсортируй по приоритету» — поверх SCADA, аналитики и учёта",
             "Siemens Industrial Copilot: больше 100 промышленных клиентов к октябрю 2024 года, голосовой режим в Simatic eaSie. "
             "Росатом: система поддержки оператора на блоке № 6 Нововоронежской АЭС в опытной эксплуатации с июля 2025 года — 360 систем, прогноз на 30 минут",
             "пилоты"),
            ("<strong>Ассистент полевого инженера</strong>",
             "Узнаёт оборудование через камеру, ведёт по шагам, принимает голосовой отчёт",
             "СИБУР в 2021 году сообщал об AR-консультантах на предприятиях клиентов. Boeing — до 25% экономии времени "
             "на сборке жгутов с AR, по данным поставщика решения",
             "пилоты"),
            ("<strong>Цифровой наставник</strong>",
             "Обучение и аттестация нового персонала на оборудовании конкретной станции",
             "«Газпром нефть шельф» — VR-тренажёр для обучения (2023); BIOCAD — AR-приложение для обучения работе "
             "с лиофильной сушилкой",
             "пилоты"),
            ("<strong>Контакт-центр энергосбыта</strong>",
             "Голосовой ассистент принимает показания, консультирует по тарифам и платежам",
             "Голосовые роботы в контакт-центрах уже работают — это самый зрелый сценарий и опора для остальных",
             "работает")]
    return figure("Четыре сценария пятого поколения и что их подтверждает уже сегодня",
                  table(["Сценарий", "Что делает", "Подтверждения", "Зрелость"], rows))


def fig_barriers():
    rows = [("Кибербезопасность КИИ",
             "187-ФЗ, приказы ФСТЭК № 31 и № 239, постановление № 127. В 2025 году — больше 400 дел о нарушении "
             "категорирования. Голос можно подделать, команду — внедрить через запрос",
             "Контур «информирование и рекомендации», а не «управление»; подтверждение оператором, журнал каждого запроса, "
             "сегментация сетей, однонаправленные шлюзы"),
            ("Галлюцинации моделей",
             "В апреле 2025 года OpenAI сообщила, что o3 ошибается в 33% вопросов теста PersonQA — вдвое чаще o1. "
             "Полностью устранить галлюцинации нельзя",
             "Модель — интерпретатор доверенных данных (RAG), а не источник истины; ссылка на источник в каждом ответе"),
            ("Отраслевые данные",
             "Общие модели плохо знают терминологию, маркировки и аббревиатуры энергетики",
             "Дообучение на данных заказчика, терминологические базы, проверка распознавания речи в шуме"),
            ("Технологический суверенитет",
             "Siemens и ABB ушли, Schneider Electric продала бизнес, GE свернула деятельность; на значимых объектах КИИ "
             "иностранное ПО запрещено с 2025 года",
             "Развёртывание в контуре заказчика — норма, а не опция"),
            ("Кадры и культура",
             "Для части персонала ИИ-ассистент непривычен; молодые сотрудники ждут голосовых помощников, как дома",
             "Проект управления изменениями: пилотные группы с опытными диспетчерами, прозрачность, от информирования к рекомендациям"),
            ("Регулирование",
             "Отраслевых стандартов нет; приказ ФСТЭК № 117 с 1 марта 2026 года впервые задал требования к ИИ, но для "
             "государственных систем; законопроект о сертификации ИИ высокого риска — в работе",
             "Опережающее внедрение: первые получают опыт и влияют на стандарты"),
            ("Экономика",
             "Эффект комплексный: время операций, ошибки, скорость обучения. Методик оценки нет",
             "Обоснование через стратегическую готовность отрасли, а не ROI одного проекта")]
    return figure("Семь барьеров и практический вывод по каждому", table(["Барьер", "В чём сложность", "Вывод"], rows))


TALK = [("0–2", "Вступление", "Диспетчер 1921 года с телефоном и диспетчер 2026 года с видеостеной. Что будет через 10 лет?"),
        ("2–6", "История", "Пять поколений: каждое расширяло возможности человека, а не заменяло его"),
        ("6–9", "«Последняя миля» — честно", "Не «SCADA устарела», а «появились новые задачи»"),
        ("9–12", "Природа человека", "Интерфейс будущего не изобретается, а возвращается к естественной форме"),
        ("12–16", "Образ будущего", "Пятое поколение и четыре сценария с подтверждениями сегодняшнего дня"),
        ("16–19", "Барьеры", "Каждый — с практическим выводом"),
        ("19–20", "Финал", "Почему у России есть основания и возврат к образу диспетчера")]


def fig_talk():
    html = '<ol class="talk">' + "".join(
        f'<li><span class="tk-m">{m} мин</span><span class="tk-h">{esc(h)}</span><span class="tk-t">{esc(t)}</span></li>'
        for m, h, t in TALK) + "</ol>"
    return figure("Структура доклада: 20 минут", html)


REFS = [
    ("АО «СО ЕЭС»: история оперативно-диспетчерского управления", "https://www.so-ups.ru/about/history/1921-2002/"),
    ("АО «СО ЕЭС»: как менялись диспетчерские щиты", "https://www.so-ups.ru/news/smi/press-view/news/1517/"),
    ("НИИПТ: АСУ ТП Выборгской преобразовательной подстанции", "https://isup.ru/articles/2/424/"),
    ("«Коммерсантъ»: ИИ в энергетике, данные Минэнерго", KOMMERSANT),
    ("РИА Новости: Минэнерго о применении ИИ в ТЭК", "https://ria.ru/20250422/predprijatija-2012798075.html"),
    ("Отчёт комиссии Кемени об аварии на Три-Майл-Айленд", "http://www.pddoc.com/tmi2/kemeny/wednesday_march_28_1979.htm"),
    ("Alarm floods and plant incidents (ISA-18.2)", "https://www.digitalrefining.com/article/1000558/alarm-floods-and-plant-incidents"),
    ("Microsoft и Siemens: Industrial Copilot", "https://news.microsoft.com/source/2024/10/24/siemens-and-microsoft-scale-industrial-ai/"),
    ("Siemens: ИИ-агенты и голосовой режим", "https://press.siemens.com/global/en/pressrelease/siemens-introduces-ai-agents-industrial-automation"),
    ("«Российская газета»: цифровой помощник оператора на Нововоронежской АЭС",
     "https://rg.ru/2025/07/04/reg-cfo/na-novovoronezhskoj-aes-zarabotal-unikalnyj-cifrovoj-pomoshchnik-operatora.html"),
    ("Kyutai Moshi: задержка голосовой модели", "https://arxiv.org/abs/2410.00037"),
    ("Mistral: Voxtral", "https://mistral.ai/news/voxtral"),
    ("OpenAI: gpt-realtime", "https://openai.com/index/introducing-gpt-realtime/"),
    ("Deloitte TMT Predictions 2025: ИИ-агенты",
     "https://www.deloitte.com/us/en/insights/industry/technology/technology-media-and-telecom-predictions/2025/autonomous-generative-ai-agents-still-under-development.html"),
    ("TechCrunch: галлюцинации o3 и o4-mini", "https://techcrunch.com/2025/04/18/openais-new-reasoning-ai-models-hallucinate-more/"),
    ("Xu и др. (2024): неизбежность галлюцинаций", "https://arxiv.org/abs/2401.11817"),
    ("Меграбян о границах своей формулы", "https://www.kaaj.com/psych/smorder.html"),
    ("ФСТЭК о проверках КИИ в 2025–2026 годах",
     "https://cisoclub.ru/fstjek-priznala-ujazvimost-bolshinstva-obektov-kriticheskoj-infrastruktury-i-gotovitsja-uzhestochit-kontrol"),
    ("Приказ ФСТЭК № 117: требования к ИИ", "https://www.anti-malware.ru/analytics/Technology_Analysis/FSTEC-Order-No-117"),
    ("Указ № 166 об отечественном ПО на значимых объектах КИИ", "https://base.garant.ru/403784114/"),
    ("Европейский AI Act: ИИ в энергетике — высокий риск",
     "https://www.bakerbotts.com/thought-leadership/publications/2026/may/ai-regulatory-update-for-energy-new-timelines-in-the-eu-new-standards-in-the-us"),
    ("«Коммерсантъ»: цель Национальной стратегии развития ИИ — 11,2 трлн рублей", "https://www.kommersant.ru/doc/7267191"),
    ("СИБУР: AR-консультанты (CNews, 2020)", "https://www.cnews.ru/news/line/2020-07-10_sibur_zapustil_arservis"),
    ("Boeing и Upskill: AR в сборке жгутов", "https://arinsider.co/2021/08/24/case-study-boeing-cuts-production-time-with-ar/"),
    ("«Наносемантика» на РМЭФ-2026", NEWS),
]


def fig_refs():
    return ('<ol class="sources">' + "".join(f"<li>{link(esc(t), u)}</li>" for t, u in REFS) + "</ol>"
            '<p class="note">Аналитическая записка к докладу не публикуется целиком; факты из неё сверены с источниками '
            'выше, цифры приведены по первоисточникам.</p>')


def author_block():
    img = base64.b64encode((ROOT / "assets/img/author.jpg").read_bytes()).decode()
    return (f'<div class="author"><img src="data:image/jpeg;base64,{img}" alt="Максим Поципух" width="64" height="64">'
            '<span class="author-txt"><span>Максим Поципух</span><span class="author-links">'
            '<a href="https://t.me/maxim_potsipukh" target="_blank" rel="noopener">Telegram</a> · '
            '<a href="https://max.ru/u/f9LHodD0cOI-rqGbPaCc2EshAXaEgw4ABwO8e2-ng4zK-otGeBnO04IzH5g" target="_blank" rel="noopener">Max</a></span></span></div>')

FIGS = {"photo": fig_photo, "generations": fig_generations, "tasks": fig_tasks, "channels": fig_channels,
        "adoption": fig_adoption, "scenarios": fig_scenarios, "barriers": fig_barriers, "talk": fig_talk, "refs": fig_refs}

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
.author-txt{display:flex; flex-direction:column; gap:2px;} .author-links{font-weight:400; font-size:13.5px; color:var(--muted);} .author-links a{color:var(--accent);}
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
.photo img{display:block; width:100%; height:auto; border-radius:4px;}
.gens{display:grid; grid-template-columns:repeat(3,1fr); gap:10px;}
.gen{border:1px solid var(--rule); border-radius:6px; padding:10px 12px; font-size:13px; line-height:1.45;} .gen p{margin:4px 0 0;}
.gen-n{font-size:1.5rem; font-weight:700; color:var(--accent); font-variant-numeric:tabular-nums;}
.gen-y{font-family:"IBM Plex Mono",ui-monospace,monospace; font-size:11.5px; color:var(--muted);}
.gen-h{font-weight:650; text-transform:uppercase; letter-spacing:.04em; font-size:12.5px; margin-top:4px;}
.gen.next{background:var(--accent-soft); border-color:var(--accent);} .gen.next .gen-h{color:var(--accent);}
.cards{display:grid; grid-template-columns:repeat(3,1fr); gap:10px;} .cards5{grid-template-columns:repeat(5,1fr);}
.card{border:1px solid var(--rule); border-radius:6px; padding:10px 12px; font-size:13px; line-height:1.45;} .card p{margin:0;}
.rg-lo.fc{opacity:.45;}
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
    OUT.write_text(page, encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(page) // 1024} КБ, блоков: {len(FIGS)}")


if __name__ == "__main__":
    main()
