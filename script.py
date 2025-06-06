import tomllib
from dataclasses import dataclass, field
from typing import List, Optional
from tinyhtml import html, h, frag, raw


@dataclass
class Item:
    title: str
    description: Optional[str] = None
    url: Optional[str] = None
    icon: Optional[str] = None
    embed_url: Optional[str] = None
    embed_height: str = "315"
    text_color: Optional[str] = None
    hover_color: Optional[str] = None
   


@dataclass
class Section:
    title: str
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_size: str = "24px"
    direction: str = "column"
    
    item_style: str = "outline"
    items: List[Item] = field(default_factory=list)
    text_color: Optional[str] = None
    hover_color: Optional[str] = None


@dataclass
class Data:
    name: str
    base_url: str
    sections: List[Section] = field(default_factory=list)
    description: Optional[str] = None
    keywords: Optional[str] = None
    image: Optional[str] = None
    theme: str = "dark"
    primary_color: str = "#546e7a"
    text_align: str = "center"
    gtag_id: Optional[str] = None


def load_data(file_path):
    with open(file_path, "rb") as f:
        raw_data = tomllib.load(f)

    return Data(
        name=raw_data.get("name", ""),
        description=raw_data.get("description"),
        keywords=raw_data.get("keywords"),
        base_url=raw_data.get("base_url", ""),
        image=raw_data.get("image"),
        theme=raw_data.get("theme", "dark"),
        primary_color=raw_data.get("primary_color", "#546e7a"),
        text_align=raw_data.get("text_align", "center"),
        gtag_id=raw_data.get("gtag_id"),
        sections=[
            Section(
                title=section.get("title"),
                description=section.get("description"),
                icon=section.get("icon"),
                icon_size=section.get("icon_size", "24px"),
                direction=section.get("direction", "column"),
                item_style=section.get("item_style", "outline"),
                text_color=section.get("text_color"),
                hover_color=section.get("hover_color"),
                items=[
                    Item(
                        title=item.get("title"),
                        description=item.get("description"),
                        url=item.get("url"),
                        icon=item.get("icon"),
                        embed_url=item.get("embed_url"),
                        embed_height=item.get("embed_height", "315"),
                        text_color=item.get("text_color"),
                        hover_color=item.get("hover_color"),
                    )
                    for item in section.get("items", [])
                ],
            )
            for section in raw_data.get("sections", [])
        ],
    )


def create_section(section: Section):
    items = frag(
        (
            h("style")(
                f"""
                .item-{abs(hash(item.title))} {{
                    transition: transform 0.25s ease, box-shadow 0.25s ease;
                    transform-origin: center;
                }}
                .item-{abs(hash(item.title))}:hover {{
                    transform: scale(1.05);
                    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
                    {"border-color" if section.item_style == "outline" else "background-color"}: {(item.hover_color or section.hover_color)};
                }}
                """
            )
            if (item.hover_color or section.hover_color)
            else None,
            h(
                "div",
                klass="item",
                style=f"width: {'100%' if section.direction == 'column' else 'unset'}",
            )(
                h(
                    "a",
                    role="button",
                    klass=f"item-{abs(hash(item.title))} {'outline' if section.item_style == 'outline' else ''}",
                    href=item.url,
                    target="_blank",
                )(
                    h(
                        "img",
                        klass="icon",
                        src=item.icon,
                        alt=item.title,
                        style=f"width: {section.icon_size};",
                    ) if item.icon else None,
                    h("hgroup")(
                        h("h4", style=f"color: {item.text_color or section.text_color};")(item.title),
                        h("h5", style=f"color: {item.text_color or section.text_color};")(raw(item.description.replace("\n", "<br>"))) if item.description else None,

                    ),
                )
            )
        )
        for item in section.items
    )

    return h("div", klass="section", style=f"color: {section.text_color};" if section.text_color else None)(
        h("hgroup")(
            h("h3")(section.title),
            h("p")(section.description),
        ),
        h("div", klass="items", style=f"flex-direction: {section.direction}")(items),
    )



def create_meta_tags(data: Data):
    return frag(
        h("title")(data.name),
        h("meta", name="description", content=data.description),
        h("meta", name="keywords", content=data.keywords),
        h("meta", name="viewport", content="width=device-width, initial-scale=1"),
        h("meta", charset="utf-8"),
        h("meta", property="og:title", content=data.name),
        h("meta", property="og:description", content=data.description),
        h("meta", property="og:image", content=f"{data.base_url}/img/{data.image}"),
        h("meta", name="twitter:title", content=data.name),
        h("meta", name="twitter:description", content=data.description),
        h("meta", name="twitter:image", content=f"{data.base_url}/img/{data.image}"),
        h("meta", name="twitter:card", content="summary_large_image"),
    )


def create_head(data: Data):
    return h("head")(
        create_meta_tags(data),
        h("link", rel="stylesheet", href="css/pico.min.css"),
        h("link", rel="stylesheet", href="css/style.css"),
        
        # Google Analytics via gtag.js
        raw(
            """
            <!-- Google tag (gtag.js) -->
            <script async src="https://www.googletagmanager.com/gtag/js?id=G-87LHKLZ7DY"></script>
            <script>
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-87LHKLZ7DY');
            </script>
            """
        ),

# GTM Script (in HEAD)
        raw(
            f"""
            <!-- Google Tag Manager -->
            <script>
            (function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
            new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
            j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
            'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
            }})(window,document,'script','dataLayer','{data.gtag_id}');
            </script>
            <!-- End Google Tag Manager -->
            """
         ) if data.gtag_id else None,


#New BG
h("style")(
    f"""
        [data-theme="dark"] {{
            --primary: {data.primary_color} !important;
        }}
        body {{
            background-color: #000000 !important;
            color: #ffffff;
        }}
        * {{
            text-align: {data.text_align};
        }}
    """
),

#OLD BG
        #h("style", rel="stylesheet")(
         #   f"""
          #      [data-theme="dark"], [data-theme="light"] {{
           #         --primary: {data.primary_color} !important;
            #    }}
             #   * {{
              #      text-align: {data.text_align};
               # }}
           # """
       # ),
    
    )


def create_header(data: Data):
    return h("header", klass="container")(
        h("hgroup")(
            h("img", klass="avatar", src=f"img/{data.image}", alt="avatar", style="width: 200px; height: auto;"),
            h("h1")(data.name),
            h("p")(data.description) if data.description else None,
        )
    )


def create_footer():
    return h("footer", klass="container")(
        h("small")("Copyright of "),
        h("a", klass="", href="https://gthgotohealth.github.io/GoToHealth.github.io/", target="_blank")(
            "Go-To Health"
        ),
    )


def generate_html(data: Data):
    sections = frag(create_section(section) for section in data.sections)
    return html(lang="en", data_theme=data.theme)(

 
        create_head(data),
        h("body")(
            # ✅ GTM noscript iframe goes here
            raw("""
                <!-- Google Tag Manager (noscript) -->
                <noscript>
                  <iframe src="https://www.googletagmanager.com/ns.html?id=GTM-55D6RKC6"
                          height="0" width="0" style="display:none;visibility:hidden"></iframe>
                </noscript>
                <!-- End Google Tag Manager (noscript) -->
            """)
            if data.gtag_id else None,
            create_header(data),
            h("main", klass="container")(sections),
            create_footer(),
        ),
    ).render()


def main():
    data = load_data("data.toml")
    output = generate_html(data)
    with open("dist/index.html", "w") as f:
        f.write(output)


if __name__ == "__main__":
    main()
