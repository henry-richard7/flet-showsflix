from flet import View, AppBar, Text, Column, ScrollMode, Video, VideoMedia
from components import EpisodeItem
from modules import VidstreamScraper

from urllib.parse import parse_qs


class EpisodesPage(View):
    def __init__(self, data: str, mode: str = "kdrama"):
        super().__init__()

        scraper = VidstreamScraper(mode=mode)
        parsed_data = parse_qs(data)

        show_title = parsed_data["title"][0]
        show_image = parsed_data["image"][0]
        href = parsed_data["href"][0]

        episodes = scraper.episodes(href)

        self.route = "/episodes"

        column = Column(expand=1, scroll=ScrollMode.ALWAYS)
        video_player = Video(expand=True, aspect_ratio=16 / 9, filter_quality="high")

        for episode in episodes[::-1]:
            column.controls.append(
                EpisodeItem(
                    title=episode.get("title"),
                    image=episode.get("image"),
                    date=episode.get("date"),
                    href=episode.get("href"),
                    video_player=video_player,
                    mode=mode,
                )
            )

        self.appbar = AppBar(title=Text(show_title))
        # self.expand = 1
        controls = [video_player, column]
        self.controls = controls
