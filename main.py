import flet as ft
from flet_core import TemplateRoute
from pages import RecentlyAddedPage, EpisodesPage, SearchResultsPage
from urllib.parse import parse_qs


def main(page: ft.Page):
    page.title = "Shows Flix"

    def route_change(route):
        router = TemplateRoute(page.route)
        parsed_parameters = parse_qs(route.route)
        mode = parsed_parameters.get("mode", None)

        mode = mode[0] if mode else None

        if router.match("/home*"):
            page.views.clear()
            page.views.append(RecentlyAddedPage(mode=mode))
        elif router.match("/episodes*"):
            page.views.append(EpisodesPage(mode=mode, data=route.route))
        elif router.match("/search*"):
            page.views.append(SearchResultsPage(mode=mode, data=route.route))

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go("/home&mode=kdrama")


ft.app(main)
