from flet import View, GridView, AppBar, Text
from components import ShowItem, SearchBar
from modules import VidstreamScraper

from urllib.parse import parse_qs


class SearchResultsPage(View):
    def __init__(self, data: str, mode: str = "kdrama"):
        super().__init__()

        scraper = VidstreamScraper(mode=mode)
        parsed_data = parse_qs(data)

        self.query = parsed_data["query"][0]
        search_results = scraper.search(self.query)

        self.result_length = len(search_results)

        self.route = "/search"

        grid_view = GridView(
            expand=1,
            runs_count=4,
            spacing=5,
            horizontal=False,
        )

        for search_result in search_results:
            grid_view.controls.append(
                ShowItem(
                    title=search_result.get("title"),
                    image=search_result.get("image"),
                    date=search_result.get("date"),
                    href=search_result.get("href"),
                    mode=mode,
                )
            )

        self.appbar = AppBar(
            title=Text(f"Search Results {self.query} ({self.result_length} Results!):")
        )
        controls = [SearchBar(mode=mode), grid_view]
        self.controls = controls
