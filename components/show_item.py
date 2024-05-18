from urllib.parse import quote_plus
from flet import (
    Text,
    Column,
    MainAxisAlignment,
    CrossAxisAlignment,
    FontWeight,
    Container,
    ImageFit,
    TextOverflow,
    colors,
    border,
)

from flet_core import ControlEvent


class ShowItem(Container):
    def __init__(self, title: str, image: str, date: str, href: str, mode: str):
        super().__init__()
        self.title = title
        self.image_url = image
        self.href = href
        self.on_click = self.click_handler
        self.border_radius = 5
        self.border = border.all(2, colors.WHITE10)
        self.mode = mode
        self.image_src = image
        self.image_fit = ImageFit.COVER
        self.image_opacity = 0.6
        self.padding = 10

        self.content = Column(
            controls=[
                Text(
                    title,
                    overflow=TextOverflow.ELLIPSIS,
                    weight=FontWeight.W_900,
                    color=colors.WHITE,
                    size=16,
                ),
                Text(date, overflow=TextOverflow.ELLIPSIS, weight=FontWeight.W_500),
            ],
            horizontal_alignment=CrossAxisAlignment.STRETCH,
            alignment=MainAxisAlignment.SPACE_BETWEEN,
        )

    def click_handler(self, e: ControlEvent):
        title_ = quote_plus(self.title.rstrip(" "))
        image_ = quote_plus(self.image_url)
        href_ = quote_plus(self.href)
        url_build = (
            f"/episodes&title={title_}&image={image_}&href={href_}&mode={self.mode}"
        )
        self.page.go(url_build)
