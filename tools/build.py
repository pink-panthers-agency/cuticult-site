#!/usr/bin/env python3
"""Builds the extra pages from index.html (the source of truth).

  python3 tools/build.py

Writes ru/index.html (Russian copy of the home page) and one folder per
service landing page (see PAGES below). Re-run after every index.html edit.
"""
import html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ru import RU, RU_ATTR  # noqa: E402
from pages import PAGES  # noqa: E402

SITE = "https://cuticult.com.ua"
BOOK = "https://n1381058.alteg.io"
SRC = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()


def cut(start, end, s=SRC):
    i = s.index(start)
    return s[i:s.index(end, i)]


STYLE = cut('<link rel="preconnect"', "</head>")
HEADER = cut("  <!-- NAV -->", "  <!-- HERO -->")
OFFER = cut("  <!-- OFFER BAND -->", "  <!-- WHY -->")
CONTACTS = cut("  <!-- FINAL CTA + CONTACTS -->", "</div>\n\n<script>")
SCRIPT = cut("<script>document", "</body>")
ICONS = cut('<link rel="icon"', "<script")


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", rel, len(text))


# ---------- Russian home page ----------
def ru_text(m):
    raw = m.group(1)
    t = raw.strip()
    if not t:
        return m.group(0)
    new = RU.get(t)
    if new is None:
        new = re.sub(r"^Перлина (\d+)$", r"Жемчужина \1", t)
    return ">" + raw.replace(t, new) + "<"


def ru_attr(m):
    name, val = m.group(1), m.group(2)
    if val in RU_ATTR:
        val = RU_ATTR[val]
    else:
        r = re.match(r"Маршрут від (.+) до CUTI CULT$", val)
        if r:
            who = r.group(1)
            who = RU.get(who, re.sub(r"^Перлина (\d+)$", r"Жемчужина \1", who))
            val = "Маршрут от %s до CUTI CULT" % who
    return '%s="%s"' % (name, val)


def build_ru():
    s = SRC
    head, body = s.split("<body>", 1)
    body_main, tail = body.split("<script>document", 1)
    body_main = re.sub(r">([^<>]+)<", ru_text, body_main)
    body_main = re.sub(r'(alt|aria-label)="([^"]+)"', ru_attr, body_main)
    body_main = body_main.replace('src="img/', 'src="/img/')
    body_main = body_main.replace('<a href="/ru/" lang="ru" style="color: rgba(244,236,230,.7)">Русская версия</a>', '<a href="/" lang="uk" style="color: rgba(244,236,230,.7)">Українська версія</a>')
    body_main = body_main.replace('<a class="lang" href="/ru/" hreflang="ru" lang="ru" title="Русская версия"', '<a class="lang" href="/" hreflang="uk" lang="uk" title="Українська версія"').replace('>RU</a>', '>UA</a>', 1)
    # "засматриваются" is longer than "задивляються": smaller hero heading
    body_main = body_main.replace("font-size: clamp(52px, 7.2vw, 104px)", "font-size: clamp(42px, 5.8vw, 86px)", 1)
    body_main = body_main.replace('<span lang="ru">', '<span lang="uk">', 1)
    body_main = re.sub(r'<span lang="uk">.*?</span>',
                       '<span lang="uk"><a href="/" style="color: inherit">Українською</a></span>', body_main, count=1, flags=re.S)
    body = body_main + "<script>document" + tail
    head = head.replace('<html lang="uk">', '<html lang="ru">')
    head = re.sub(r"<title>.*?</title>", "<title>Маникюр и педикюр в Одессе, Аркадия · CUTI CULT возле Жемчужины Kadorr</title>", head)
    head = re.sub(r'<meta name="description" content="[^"]*">',
                  '<meta name="description" content="Маникюр и педикюр в Аркадии, Одесса: студия CUTI CULT в ЖК «Элегия Парк», напротив Kadorr Mall, в нескольких минутах от Жемчужин Kadorr и Гольфстрима. Ежедневно 9:00–21:00, онлайн-запись. −200 ₴ на первый визит.">', head)
    head = re.sub(r'<meta name="keywords" content="[^"]*">',
                  '<meta name="keywords" content="маникюр Одесса, педикюр Одесса, маникюр Аркадия, педикюр Аркадия, маникюр Жемчужина Kadorr, наращивание ногтей Одесса, японский маникюр Одесса, маникюр Гольфстрим">', head)
    head = head.replace('content="CUTI CULT · манікюр і педикюр в Аркадії, Одеса"', 'content="CUTI CULT · маникюр и педикюр в Аркадии, Одесса"')
    head = head.replace('content="Nail care studio. Курортний провулок 1а, щодня 9:00–21:00. Онлайн-запис."', 'content="Nail care studio. Курортный переулок 1а, ежедневно 9:00–21:00. Онлайн-запись."')
    head = head.replace('content="uk_UA"', 'content="ru_UA"')
    head = head.replace('<link rel="canonical" href="https://cuticult.com.ua/">', '<link rel="canonical" href="https://cuticult.com.ua/ru/">')
    head = head.replace('<meta property="og:url" content="https://cuticult.com.ua/">', '<meta property="og:url" content="https://cuticult.com.ua/ru/">')
    head = re.sub(r'<meta name="(?:facebook-domain|google-site)-verification"[^>]*>\n', "", head)
    # JSON-LD: Russian description + FAQ rebuilt from the translated FAQ
    blocks = re.findall(r'<script type="application/ld\+json">\n(.*?)\n</script>', head, re.S)
    biz = json.loads(blocks[0])
    biz["description"] = "Студия маникюра, педикюра и бровей в Одессе, в ЖК «Элегия Парк», напротив ТЦ Kadorr Mall"
    biz["address"]["streetAddress"] = "Курортный переулок, 1а"
    biz["address"]["addressLocality"] = "Одесса"
    biz["url"] = SITE + "/ru/"
    faqs = re.findall(r"<summary[^>]*>(.*?)<span class=\"pl\".*?</summary>\s*<p[^>]*>(.*?)</p>", body, re.S)
    faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q.strip(), "acceptedAnswer": {"@type": "Answer", "text": re.sub("<[^>]+>", "", a).strip()}} for q, a in faqs]}
    new_ld = "".join('<script type="application/ld+json">\n%s\n</script>\n' % json.dumps(x, ensure_ascii=False) for x in (biz, faq))
    head = re.sub(r'(<script type="application/ld\+json">\n.*?\n</script>\n?)+', lambda m: new_ld, head, count=1, flags=re.S)
    if "hreflang=" not in head:
        head = head.replace("</title>", "</title>\n" + HREFLANG, 1)
    out = head + "<body>" + body
    # untranslated Ukrainian check
    left = [t.strip() for t in re.findall(r">([^<>]+)<", body_main) if re.search("[ІіЇїЄєҐґ]", t)]
    if left:
        print("RU: untranslated?", left[:10])
    write("ru/index.html", out)


HREFLANG = ('<link rel="alternate" hreflang="uk" href="https://cuticult.com.ua/">\n'
            '<link rel="alternate" hreflang="ru" href="https://cuticult.com.ua/ru/">\n'
            '<link rel="alternate" hreflang="x-default" href="https://cuticult.com.ua/">')


# ---------- service landing pages ----------
H2 = "margin: 0 0 %s; font-family: 'Cormorant Garamond', Georgia, serif; font-weight: 400; font-size: clamp(40px, 5vw, 64px); line-height: 1.02"
EYEBROW = "margin: 0 0 14px; font-size: 12px; letter-spacing: .32em; text-transform: uppercase; font-weight: 700; color: %s"
ROW = '<div style="display: flex; justify-content: space-between; gap: 16px; padding: 12px 0; border-bottom: 1px solid rgba(216,180,138,.18)"><span>%s</span><span style="font-weight: 600">%s</span></div>'
FAQ_ITEM = '''        <details style="border-bottom: 1px solid #DCCBC1; padding: 22px 0">
          <summary style="display: flex; justify-content: space-between; gap: 16px; font-family: 'Cormorant Garamond', Georgia, serif; font-size: 24px">%s<span class="pl" style="color: #73583A; font-family: Manrope, sans-serif; transition: transform .2s">+</span></summary>
          <p style="margin: 12px 0 0; color: #6E5C55; max-width: 620px">%s</p>
        </details>
'''


def e(t):
    return html.escape(t, quote=False)


def page_html(p):
    url = "%s/%s/" % (SITE, p["slug"])
    others = [o for o in PAGES if o["slug"] != p["slug"]]
    gal = "".join('<figure%s><img loading="lazy" decoding="async" src="/img/%s" alt="%s"><figcaption>%s</figcaption></figure>'
                  % (' class="big"' if i == 0 and len(p["photos"]) == 5 else "", f, html.escape(a), e(c)) for i, (f, a, c) in enumerate(p["photos"]))
    cards = "".join('''        <div style="border-top: 1px solid #1A120E; padding-top: 22px">
          <h3 style="margin: 0 0 8px; font-family: 'Cormorant Garamond', Georgia, serif; font-weight: 500; font-size: 26px">%s</h3>
          <p style="margin: 0; font-size: 15px; color: #6E5C55">%s</p>
        </div>
''' % (e(h), e(t)) for h, t in p["points"])
    prices = "".join(ROW % (e(n), e(v)) for n, v in p["prices"])
    text = "".join('<p style="margin: 0 0 18px; font-size: 17px; color: #6E5C55; max-width: 760px">%s</p>' % t for t in p["text"])
    links = "".join('<a class="btn line" href="/%s/" style="color: #1A120E; border-color: #DCCBC1">%s</a>' % (o["slug"], e(o["link"])) for o in others)
    faq = "".join(FAQ_ITEM % (e(q), e(a)) for q, a in p["faq"])
    ld = [
        {"@context": "https://schema.org", "@type": "Service", "name": p["service"], "serviceType": p["service"], "url": url,
         "areaServed": [{"@type": "Place", "name": n} for n in p["area"]],
         "provider": {"@type": "NailSalon", "name": "CUTI CULT", "url": SITE + "/", "telephone": "+380663646484",
                      "address": {"@type": "PostalAddress", "streetAddress": "Курортний провулок, 1а", "addressLocality": "Одеса", "postalCode": "65000", "addressCountry": "UA"}},
         "offers": {"@type": "Offer", "price": p["price_from"], "priceCurrency": "UAH", "url": BOOK}},
        {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "CUTI CULT", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": p["crumb"], "item": url}]},
        {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]},
    ]
    ld_html = "".join('<script type="application/ld+json">\n%s\n</script>\n' % json.dumps(x, ensure_ascii=False) for x in ld)
    header = (HEADER.replace('href="#top"', 'href="/"')
              .replace('href="#services"', 'href="/#services"').replace('href="#works"', 'href="/#works"')
              .replace('href="#prices"', 'href="/#prices"').replace('href="#contacts"', 'href="#contacts"'))
    return f'''<!doctype html>
<html lang="uk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p["title"])}</title>
<meta name="description" content="{html.escape(p["description"])}">
<meta property="og:title" content="{html.escape(p["title"])}">
<meta property="og:description" content="{html.escape(p["description"])}">
<meta property="og:type" content="website">
<meta property="og:locale" content="uk_UA">
<link rel="canonical" href="{url}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/img/{p["photos"][0][0]}">
{ICONS}{ld_html}{STYLE}</head>
<body>

<div class="cc" style="font-family: Manrope, 'Segoe UI', system-ui, sans-serif; color: #F4ECE6; background: #120D0B; line-height: 1.6; font-size: 16px">

{header}
  <!-- HERO -->
  <section id="top" style="position: relative; overflow: hidden">
    <div class="wrap" style="padding-top: 64px; padding-bottom: 80px">
      <nav aria-label="Навігація" style="font-size: 13px; color: rgba(244,236,230,.55); margin-bottom: 26px"><a href="/" style="color: inherit">CUTI CULT</a> / <span>{e(p["crumb"])}</span></nav>
      <p style="{EYEBROW % '#D8B48A'}">{e(p["eyebrow"])}</p>
      <h1 style="margin: 0; max-width: 900px; font-family: 'Cormorant Garamond', Georgia, serif; font-weight: 400; font-size: clamp(46px, 6.4vw, 92px); line-height: 1; letter-spacing: -.01em; text-wrap: balance">{p["h1"]}</h1>
      <p style="margin: 28px 0 0; max-width: 620px; font-size: 18px; color: rgba(244,236,230,.74)">{e(p["lead"])}</p>
      <div style="display: flex; flex-wrap: wrap; gap: 14px; margin-top: 38px">
        <a class="btn gold" href="{BOOK}" target="_blank" rel="noopener">Обрати час онлайн</a>
        <a class="btn line" href="#prices">Дивитися ціни</a>
      </div>
    </div>
  </section>

{OFFER}
  <!-- POINTS -->
  <section style="background: #F6F0EB; color: #1A120E">
    <div class="wrap" style="padding-top: 96px; padding-bottom: 96px">
      <h2 style="{H2 % '44px'}">{p["points_title"]}</h2>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(240px, 100%), 1fr)); gap: 32px">
{cards}      </div>
    </div>
  </section>

  <!-- PRICES -->
  <section id="prices" style="background: #1A120E">
    <div class="wrap" style="padding-top: 96px; padding-bottom: 96px">
      <p style="{EYEBROW % '#D8B48A'}">Прайс · жовтень 2026</p>
      <h2 style="{H2 % '40px'}">{p["prices_title"]}</h2>
      <div style="max-width: 640px; font-variant-numeric: tabular-nums">{prices}</div>
      <p style="margin: 22px 0 0; font-size: 14px; color: rgba(244,236,230,.6)">Перший візит: −200 ₴ на одну послугу. В онлайн-записі буде повна ціна, знижку зробить адміністратор при оплаті (кодове слово CUTI200).</p>
      <a class="btn gold" href="{BOOK}" target="_blank" rel="noopener" style="margin-top: 36px">Записатися онлайн</a>
    </div>
  </section>

  <!-- WORKS -->
  <section id="works" style="background: #120D0B">
    <div class="wrap" style="padding-top: 96px; padding-bottom: 96px">
      <p style="{EYEBROW % '#D8B48A'}">Справжні фото зі студії</p>
      <h2 style="{H2 % '40px'}">{p["works_title"]}</h2>
      <div class="gal">{gal}</div>
    </div>
  </section>

  <!-- TEXT -->
  <section style="background: #F6F0EB; color: #1A120E">
    <div class="wrap" style="padding-top: 96px; padding-bottom: 80px">
      <h2 style="{H2 % '30px'}">{p["text_title"]}</h2>
      {text}
      <p style="{EYEBROW % '#73583A'}; margin-top: 40px">Ще у CUTI CULT</p>
      <div style="display: flex; flex-wrap: wrap; gap: 12px">{links}<a class="btn line" href="/" style="color: #1A120E; border-color: #DCCBC1">Усі послуги</a></div>
    </div>
  </section>

  <!-- FAQ -->
  <section style="background: #F6F0EB; color: #1A120E; border-top: 1px solid #DCCBC1">
    <div class="wrap" style="display: flex; flex-wrap: wrap; gap: 48px; padding-top: 96px; padding-bottom: 96px">
      <h2 style="flex: 1 1 280px; {H2 % '0'}">Часті питання</h2>
      <div style="flex: 2 1 480px; min-width: 0">
{faq}      </div>
    </div>
  </section>

{CONTACTS}</div>

{SCRIPT}</body>
</html>
'''


def build_pages():
    for p in PAGES:
        write(p["slug"] + "/index.html", page_html(p))


if __name__ == "__main__":
    build_ru()
    build_pages()
