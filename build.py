# -*- coding: utf-8 -*-
"""Generate the static Shunzi site."""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
POSTS = ROOT / "posts"

POSTS_META = [
    {
        "slug": "thinking-above-tools",
        "file": "thinking-above-tools.md",
        "date": "08.23.26",
        "iso": "2026-08-23",
        "excerpt": "桌上是一款已经做完的工业选型产品。我想从它被做成的样子里，摸到制作时的底层思维。",
        "origin": "https://www.superlinear.academy/c/share-your-projects/industry-select-product",
        "cover": "formula",
    },
    {
        "slug": "two-aha-moments",
        "file": "two-aha-moments.md",
        "date": "08.13.26",
        "iso": "2026-08-13",
        "excerpt": "程序跑对了，账却可能错了。两个 aha 之后，我开始问谁负责到底，以及什么必须留下名字。",
        "origin": "https://www.superlinear.academy/c/share-your-projects/aha-moment",
        "cover": "two",
    },
    {
        "slug": "hello",
        "file": "hello.md",
        "date": "08.08.26",
        "iso": "2026-08-08",
        "excerpt": "一年医疗器械算法工程师，正在走进 AI 全栈。用作品集跟社区见面。",
        "origin": "https://www.superlinear.academy/c/say-hello/03-ai-being-ing",
        "cover": "hello",
    },
    {
        "slug": "ai-wrote-the-code",
        "file": "ai-wrote-the-code.md",
        "date": "08.08.26",
        "iso": "2026-08-08",
        "excerpt": "我问过「npm 是做什么的」。代码几乎都是 AI 写的，串账和一分钱尾差是我留下的判断。",
        "origin": "https://www.superlinear.academy/c/share-your-projects/100-ai",
        "cover": "grid",
    },
]


def prefix_for(depth: int) -> str:
    return "" if depth == 0 else "../" * depth


def mark_svg(size: int = 28) -> str:
    return f"""<svg class="mark" width="{size}" height="{size}" viewBox="0 0 28 28" aria-hidden="true">
  <rect width="28" height="28" rx="9" fill="#163428"/>
  <path d="M14 4.8C16.8 4.8 20.6 10.4 21.5 16.2C22.2 21.6 18.3 24.3 14 24.3C9.7 24.3 5.8 21.6 6.5 16.2C7.4 10.4 11.2 4.8 14 4.8Z" fill="#fcfaf2" stroke="#d7c4f2" stroke-width="1.1"/>
  <path d="M11.2 10c1.15-1.2 3.2-1.1 3.6.4" fill="none" stroke="#d7c4f2" stroke-width="1.2" stroke-linecap="round"/>
</svg>"""


def bounce_egg_svg() -> str:
    return """<svg class="bounce-egg" viewBox="6 4.5 16 20.2" aria-hidden="true">
        <path d="M14 4.8C16.8 4.8 20.6 10.4 21.5 16.2C22.2 21.6 18.3 24.3 14 24.3C9.7 24.3 5.8 21.6 6.5 16.2C7.4 10.4 11.2 4.8 14 4.8Z" fill="#fcfaf2" stroke="#d7c4f2" stroke-width="1.1"/>
        <path d="M11.2 10c1.15-1.2 3.2-1.1 3.6.4" fill="none" stroke="#d7c4f2" stroke-width="1.2" stroke-linecap="round"/>
      </svg>"""


def cover_svg(kind: str) -> str:
    if kind == "formula":
        return """<svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect width="320" height="200" fill="#efe8d8"/>
  <path d="M24 160 L96 40 L168 160" fill="none" stroke="#163428" stroke-width="1.6"/>
  <circle cx="232" cy="88" r="44" fill="none" stroke="#163428" stroke-width="1.6"/>
  <line x1="24" y1="168" x2="296" y2="168" stroke="#163428" stroke-width="1.1"/>
</svg>"""
    if kind == "two":
        return """<svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect width="320" height="200" fill="#efe8d8"/>
  <circle cx="128" cy="100" r="54" fill="none" stroke="#163428" stroke-width="1.6"/>
  <circle cx="192" cy="100" r="54" fill="none" stroke="#d7c4f2" stroke-width="1.8"/>
</svg>"""
    if kind == "hello":
        return """<svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect width="320" height="200" fill="#efe8d8"/>
  <rect x="86" y="46" width="148" height="108" rx="28" fill="none" stroke="#163428" stroke-width="1.6"/>
  <rect x="110" y="70" width="100" height="60" rx="18" fill="none" stroke="#163428" stroke-width="1.6"/>
</svg>"""
    return """<svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect width="320" height="200" fill="#efe8d8"/>
  <g fill="none" stroke="#163428" stroke-width="1.3">
    <rect x="28" y="28" width="60" height="60" rx="14"/>
    <rect x="130" y="28" width="60" height="60" rx="14"/>
    <rect x="232" y="28" width="60" height="60" rx="14"/>
    <rect x="28" y="112" width="60" height="60" rx="14"/>
    <rect x="130" y="112" width="60" height="60" rx="14"/>
    <rect x="232" y="112" width="60" height="60" rx="14"/>
  </g>
</svg>"""


def chrome(
    active: str,
    depth: int,
    title: str,
    description: str,
    extra: str = "",
    *,
    home: bool = False,
) -> tuple[str, str]:
    p = prefix_for(depth)
    nav = f"""<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="{p}index.html">{mark_svg()}SHUNZI</a>
    <button class="menu-toggle" type="button" aria-expanded="false">Menu</button>
    <nav class="nav-links" aria-label="Primary">
      <a href="{p}index.html"{' class="is-active"' if active == 'home' else ''}>Home</a>
      <a href="{p}work.html"{' class="is-active"' if active == 'work' else ''}>Work</a>
      <a href="{p}writings.html"{' class="is-active"' if active == 'writings' else ''}>Writings</a>
      <a href="{p}contact.html"{' class="is-active"' if active == 'contact' else ''}>Contact</a>
    </nav>
    <a class="pill pill-cta" href="https://github.com/AMappama" target="_blank" rel="noreferrer">GitHub</a>
  </div>
</header>"""
    footer = f"""<footer class="site-footer">
  <div>
    <div class="wordmark">Shunzi</div>
  </div>
  <div>
    <h3>Elsewhere</h3>
    <a href="https://github.com/AMappama" target="_blank" rel="noreferrer">GitHub</a>
    <a href="https://www.superlinear.academy/u/a72b9dac" target="_blank" rel="noreferrer">Superlinear</a>
    <a href="mailto:xieshz@88.com">xieshz@88.com</a>
  </div>
  <div>
    <h3>Index</h3>
    <a href="{p}index.html">Home</a>
    <a href="{p}work.html">Work</a>
    <a href="{p}writings.html">Writings</a>
    <a href="{p}contact.html">Contact</a>
  </div>
  <div>
    <h3>Note</h3>
    <p>Writings first published on Superlinear Academy.</p>
  </div>
</footer>"""
    head = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;1,9..144,500;1,9..144,600&family=Noto+Serif+SC:wght@500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="icon" href="{p}assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="{p}assets/site.css">
</head>
<body{' class="is-home"' if home else ''}>
<a class="skip" href="#main">Skip to content</a>
<div class="shell">
{nav}
<main class="stage" id="main">
{extra}"""
    tail = f"""{'' if home else footer}
</main>
</div>
<script src="{p}assets/site.js"></script>
</body>
</html>"""
    return head, tail


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    return text


def md_to_html(md: str) -> tuple[str, str]:
    lines = md.replace("\r\n", "\n").split("\n")
    title = "Untitled"
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip()
        lines = lines[1:]
    body: list[str] = []
    i = 0
    in_code = False
    code_lines: list[str] = []
    para: list[str] = []
    list_kind = None

    def flush_para() -> None:
        nonlocal para
        if para:
            body.append("<p>" + inline_md(" ".join(para).strip()) + "</p>")
            para = []

    def flush_list() -> None:
        nonlocal list_kind
        if list_kind:
            body.append(f"</{list_kind}>")
            list_kind = None

    while i < len(lines):
        raw = lines[i]
        if raw.startswith("```"):
            flush_para()
            flush_list()
            if in_code:
                body.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        if in_code:
            code_lines.append(raw)
            i += 1
            continue
        if raw.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-:\s|]+\|$", lines[i + 1].strip()):
            flush_para()
            flush_list()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if re.match(r"^\|[-:\s|]+\|$", lines[i].strip()):
                    i += 1
                    continue
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                rows.append(cells)
                i += 1
            if rows:
                head_row = rows[0]
                body.append("<table><thead><tr>" + "".join(f"<th>{inline_md(c)}</th>" for c in head_row) + "</tr></thead>")
                body.append("<tbody>")
                for row in rows[1:]:
                    body.append("<tr>" + "".join(f"<td>{inline_md(c)}</td>" for c in row) + "</tr>")
                body.append("</tbody></table>")
            continue
        if not raw.strip():
            flush_para()
            flush_list()
            i += 1
            continue
        if raw.strip() == "---":
            flush_para()
            flush_list()
            body.append("<hr>")
            i += 1
            continue
        if raw.startswith("### "):
            flush_para()
            flush_list()
            body.append(f"<h3>{inline_md(raw[4:].strip())}</h3>")
            i += 1
            continue
        if raw.startswith("## "):
            flush_para()
            flush_list()
            body.append(f"<h2>{inline_md(raw[3:].strip())}</h2>")
            i += 1
            continue
        if raw.startswith("> "):
            flush_para()
            flush_list()
            quote = []
            while i < len(lines) and lines[i].startswith("> "):
                quote.append(lines[i][2:])
                i += 1
            body.append("<blockquote><p>" + inline_md(" ".join(quote)) + "</p></blockquote>")
            continue
        m_ol = re.match(r"^(\d+)\.\s+(.*)$", raw)
        if m_ol:
            flush_para()
            if list_kind != "ol":
                flush_list()
                body.append("<ol>")
                list_kind = "ol"
            body.append(f"<li>{inline_md(m_ol.group(2))}</li>")
            i += 1
            continue
        if raw.startswith("- "):
            flush_para()
            if list_kind != "ul":
                flush_list()
                body.append("<ul>")
                list_kind = "ul"
            body.append(f"<li>{inline_md(raw[2:])}</li>")
            i += 1
            continue
        para.append(raw.strip())
        i += 1
    flush_para()
    flush_list()
    return title, "\n".join(body)


def wrap_cover(kind: str, cls: str) -> str:
    return f'<div class="{cls}">{cover_svg(kind)}</div>'


def cards_html(prefix: str, in_rail: bool = True) -> str:
    chunks = []
    for post in POSTS_META:
        href = f"{prefix}posts/{post['slug']}.html"
        if in_rail:
            chunks.append(
                f'<a class="card" href="{href}">{wrap_cover(post["cover"], "card-cover")}'
                f"<h3>{html.escape(title_of(post))}</h3><time datetime=\"{post['iso']}\">{post['date']}</time></a>"
            )
        else:
            chunks.append(
                f'<a class="list-row" href="{href}">'
                f"<div><h2>{html.escape(title_of(post))}</h2><p>{html.escape(post['excerpt'])}</p></div>"
                f"<time datetime=\"{post['iso']}\">{post['date']}</time></a>"
            )
    return "\n".join(chunks)


TITLES: dict[str, str] = {}


def title_of(post: dict) -> str:
    return TITLES.get(post["slug"], post["slug"])


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def load_titles() -> dict[str, tuple[str, str]]:
    rendered: dict[str, tuple[str, str]] = {}
    for post in POSTS_META:
        md = (CONTENT / post["file"]).read_text(encoding="utf-8")
        title, body = md_to_html(md)
        TITLES[post["slug"]] = title
        rendered[post["slug"]] = (title, body)
    return rendered


def build_posts() -> None:
    POSTS.mkdir(exist_ok=True)
    rendered = load_titles()
    for post in POSTS_META:
        title, body = rendered[post["slug"]]
        others = [p for p in POSTS_META if p["slug"] != post["slug"]][:3]
        related = "".join(
            f'<a class="card" href="{p["slug"]}.html"><div class="card-cover">{cover_svg(p["cover"])}</div>'
            f"<h3>{html.escape(title_of(p))}</h3>"
            f"<time>{p['date']}</time></a>"
            for p in others
        )
        extra = f"""<article class="article">
  <div class="article-kicker">Writings</div>
  <h1>{html.escape(title)}</h1>
  <div class="article-meta">{post['date']} · Shunzi</div>
  <div class="prose">{body}</div>
  <p class="origin">First published on <a href="{post['origin']}">Superlinear Academy</a>.</p>
</article>
<section class="related">
  <div class="section-head"><h2>More <em>writings.</em></h2></div>
  <div class="rail">{related}</div>
</section>
"""
        head, tail = chrome("writings", 1, f"{title} · Shunzi", post["excerpt"], extra)
        write(POSTS / f"{post['slug']}.html", head + tail)


def build_home() -> None:
    extra = f"""<section class="landing">
  <div class="scene" data-scene aria-hidden="true">
    <span class="blob blob-a"></span>
    <span class="blob blob-b"></span>
    <span class="blob blob-c"></span>
    <span class="dust"></span>
    <svg class="halo halo-spin" viewBox="0 0 640 640">
      <circle cx="320" cy="320" r="248" fill="none" stroke="#163428" stroke-width="0.7" stroke-dasharray="2 14" opacity="0.28"/>
    </svg>
    <svg class="halo halo-orbit" viewBox="0 0 640 640">
      <circle cx="320" cy="320" r="188" fill="none" stroke="#d7c4f2" stroke-width="1.1" opacity="0.55"/>
    </svg>
  </div>
  <div class="landing-copy">
    <h1><em><span class="zh">从</span> Builder<br><span class="zh">到</span> Orchestrator</em></h1>
    <p>不再执着于重复制造每一个零部件，而是学会把现成的高质量能力，调度成只为自己目标服务的交响乐。</p>
    <nav class="landing-gates" aria-label="前往其他页面">
      <a class="pill pill-cta" href="work.html">Work</a>
      <a class="pill pill-ghost" href="writings.html">Writings</a>
      <a class="pill pill-ghost" href="contact.html">Contact</a>
    </nav>
  </div>
  <div class="egg-stage is-bounce" data-bounce-stage>
    <span class="bounce-floor" aria-hidden="true"></span>
    <svg class="bounce-route" aria-hidden="true">
      <path class="route-line" data-route-line></path>
      <g data-route-apexes></g>
    </svg>
    <button class="bounce-sphere" type="button" data-bounce-ball aria-label="鸡蛋" draggable="false">
      {bounce_egg_svg()}
      <span class="egg-shadow"></span>
    </button>
  </div>
</section>
"""
    head, tail = chrome(
        "home",
        0,
        "Shunzi",
        "谢顺子。从 Builder 到 Orchestrator。",
        extra,
        home=True,
    )
    write(ROOT / "index.html", head + tail)


def build_writings() -> None:
    extra = f"""<div class="page">
  <div class="page-title">
    <h1>Writings.</h1>
    <p>先发表在 Superlinear。这里是同一批判断，换一个能慢慢读的地方。</p>
  </div>
  <div class="list">
{cards_html("", in_rail=False)}
  </div>
</div>
"""
    head, tail = chrome("writings", 0, "Writings · Shunzi", "谢顺子在 Superlinear 发表的文章。", extra)
    write(ROOT / "writings.html", head + tail)


def build_work() -> None:
    extra = """<div class="page">
  <div class="page-title">
    <h1>Work.</h1>
    <p>工业选型、医疗应收、IVD 现场。代码几乎由 AI 写出；规格和判断是我留下的。</p>
  </div>
  <div class="work-grid">
    <article class="work-item">
      <div class="n">Product</div>
      <h2>选销易</h2>
      <p>工业零部件选型。微信小程序给工程师选型号、出图纸和订货单，NestJS 提供接口，Vue 做运营后台。先拆选型作业，再让三端按规格铺开。</p>
      <p><a href="https://github.com/AMappama/industry-select-product">github.com/AMappama/industry-select-product</a></p>
    </article>
    <article class="work-item">
      <div class="n">Console</div>
      <h2>MedRWA</h2>
      <p>医疗应收收益权运营台 Demo。资产登记、审核、映射、认购、回款、对账、凭证、审计。串账校验和一分钱尾差是我留下的判断。</p>
      <p><a href="https://github.com/AMappama/med-rwa-demo">github.com/AMappama/med-rwa-demo</a></p>
    </article>
    <article class="work-item">
      <div class="n">Field</div>
      <h2>IVD 算法工程</h2>
      <p>一年医疗器械算法工程师。临床样本、标注、色谱可视化、跨平台迁移。后来把现场里的来源核对，带进了对账规则。</p>
    </article>
  </div>
</div>
"""
    head, tail = chrome("work", 0, "Work · Shunzi", "选销易、MedRWA、IVD 算法。", extra)
    write(ROOT / "work.html", head + tail)


def build_contact() -> None:
    extra = """<div class="page">
  <div class="page-title">
    <h1>写信。</h1>
    <p>深圳。看仓库，或者到 Superlinear 主页继续读。</p>
  </div>
  <div class="contact-block">
    <a href="mailto:xieshz@88.com">Email<span>xieshz@88.com</span></a>
    <a href="https://github.com/AMappama">GitHub<span>github.com/AMappama</span></a>
    <a href="https://www.superlinear.academy/u/a72b9dac">Superlinear<span>superlinear.academy/u/a72b9dac</span></a>
  </div>
</div>
"""
    head, tail = chrome("contact", 0, "Contact · Shunzi", "联系谢顺子。", extra)
    write(ROOT / "contact.html", head + tail)


def main() -> None:
    build_posts()
    build_home()
    build_writings()
    build_work()
    build_contact()


if __name__ == "__main__":
    main()
