from flet import Text, ListTile, Image, Icon, icons, TextOverflow, Video, VideoMedia

from flet_core import ControlEvent
from modules import VidstreamScraper


class EpisodeItem(ListTile):
    def __init__(
        self,
        title: str,
        image: str,
        date: str,
        href: str,
        mode: str,
        video_player: Video,
    ):
        super().__init__()
        self.title_ = title
        self.image_url = image
        self.href = href
        self.video_player = video_player

        self.scraper = VidstreamScraper(mode=mode)

        self.leading = Image(src=image, error_content=Icon(name=icons.PLAY_CIRCLE_FILL))
        self.title = Text(value=title, overflow=TextOverflow.ELLIPSIS)
        self.subtitle = Text(date, overflow=TextOverflow.ELLIPSIS)

        self.on_click = self.on_click_event

    def on_click_event(self, e: ControlEvent):
        if self.video_player.playlist:
            self.video_player.playlist_remove(0)

        direct_link = self.scraper.default_server(self.href)
        self.video_player.playlist_add(VideoMedia(direct_link["source"][0]["file"]))
        self.video_player.jump_to(0)
