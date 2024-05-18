from flet import View, GridView, AppBar, Text, PopupMenuButton, PopupMenuItem, icons
from components import ShowItem, SearchBar
from modules import VidstreamScraper


class RecentlyAddedPage(View):
    def __init__(self, mode: str = "kdrama"):
        super().__init__()

        scraper = VidstreamScraper(mode=mode)
        recently_added = scraper.recently_added()

        self.route = "/"

        grid_view = GridView(
            expand=1,
            runs_count=4,
            spacing=5,
            horizontal=False,
        )

        for item in recently_added["dramas"]:
            grid_view.controls.append(
                ShowItem(
                    title=item.get("title"),
                    image=item.get("image"),
                    date=item.get("date"),
                    href=item.get("href"),
                    mode=mode,
                )
            )
        self.appbar = AppBar(
            title=Text("Recently Added Shows"),
            actions=[
                PopupMenuButton(
                    items=[
                        PopupMenuItem(
                            text="Watch Anime",
                            icon=icons.ANIMATION_ROUNDED,
                            on_click=lambda _: self.page.go("/home&mode=anime"),
                        ),
                        PopupMenuItem(
                            text="Watch Kdrama",
                            icon=icons.TV,
                            on_click=lambda _: self.page.go("/home&mode=kdrama"),
                        ),
                    ]
                ),
            ],
        )
        controls = [SearchBar(mode=mode), grid_view]
        self.controls = controls
