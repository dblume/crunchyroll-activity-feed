#!/usr/bin/env python3
from __future__ import annotations
import os
import sys
import requests
from argparse import ArgumentParser
import cfgreader
import logging
from xml.sax.saxutils import escape
import time
from typing import List
from dataclasses import dataclass
import dateutil.parser
import crunchyroll
import session


@dataclass
class Title:
    title: str
    description: str
    type: str
    duration_ms: int
    episode: int
    season: int
    series: str
    slug: str


@dataclass
class Viewing:
    timestamp: int
    id: str
    show: Title

    def __init__(self, ts: int, id_: str, title: str, desc: str, type_: str,
        dur_ms: int=0, ep: int=0, season: int=0, series: str='', slug: str=''):
        self.timestamp = ts
        self.id = id_
        self.show = Title(title, desc, type_, dur_ms, ep, season, series, slug)

    def __lt__(self, other: Viewing) -> bool:
        return self.timestamp < other.timestamp

    def __str__(self) -> str:
        return f'{self.ts}: {self.id} {self.title}'

    @property
    def rss(self) -> str:
        """Returns an RSS <item></item>"""
        date = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(self.timestamp))
        url = f'https://crunchyroll.com/watch/{self.id}/{self.show.slug}'
        dur = ''
        if self.show.duration_ms is not None and self.show.duration_ms != 0:
            dur = f' ({int(self.show.duration_ms / 1000 / 60)}m)'

        title = ''
        if self.show.type == 'episode':
            if self.show.series is None or self.show.series == '':
                title = f'{self.show.title} (an {self.show.type})'
            else:
                title = f'{self.show.series} S{self.show.season}:E{self.show.episode} {self.show.title}{dur}'
        else:
            title = f'{self.show.title} (a {self.show.type}){dur}'

        return (f"<item>"
                f"<title>{escape(title)}</title>"
                f"<pubDate>{date}</pubDate>"
                f"<link>{escape(url)}</link>"
                f"<guid isPermaLink=\"false\">{self.timestamp}</guid>"
                f"<description><![CDATA[{self.show.description}]]></description>"
                f"</item>\n")


def make_viewing(jsn) -> Viewing:
    """Make a Viewing object from the json."""
    ts = int(dateutil.parser.parse(jsn["date_played"]).timestamp())
    try:
        if "panel" not in jsn:
            type_ = "episode" if jsn["parent_type"] == "series" else "movie"  # 'movie_listing' vs 'series'
            return Viewing(ts, jsn["id"], jsn["id"], "", type_)
        panel = jsn["panel"]
        t = Title
        t.title = panel["title"]
        t.description = panel["description"]
        t.type = panel["type"]
        t.slug = panel["slug_title"]
        if t.type == "episode":
            m = panel["episode_metadata"]
            t.duration_ms = int(m["duration_ms"])
            try:
                t.episode = int(m["episode_number"])
            except TypeError:
                t.episode = 0
            t.season = int(m["season_number"])
            t.series = m["series_title"]
        elif t.type == "movie":
            m = panel["movie_metadata"]
            t.duration_ms = int(m["duration_ms"])
            t.episode = 0
            t.season = 0
            t.series = ''
        return Viewing(ts, jsn["id"], t.title, t.description, t.type, t.duration_ms, t.episode, t.season, t.series, t.slug)
    except KeyError as e:
        logging.warning(f'KeyError making a Viewing: {e}')
        return None


def write_feed(viewings: Sequence[Viewings], cfg) -> str:
    update_status = "OK"
    now = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
    with open(cfg.feed.filename, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n'
                '<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">\n')
        f.write(f'<channel>\n'
                f'<atom:link href="{cfg.feed.href}" rel="self" type="application/rss+xml" />'
                f'<title>{cfg.feed.title}</title>'
                f'<link>https://www.crunchyroll.com/user/dblume</link><pubDate>{now}</pubDate>'
                f'<description>{cfg.feed.title}</description><language>en-us</language>\n')
        for v in viewings:
            # TODO: Don't hardcode series to ignore
            if v.show.series.startswith('Dragon Ball Z'):
                logging.debug(f'Skipping {v.timestamp} {v.show.series}')
                continue
            f.write(v.rss)
        f.write("</channel></rss>\n")
    return update_status


def main() -> None:
    """The main function, does the whole thing."""
    start_time = time.time()
    cfg = cfgreader.CfgReader(__file__.replace('.py', '.cfg'))

    try:
        cr = crunchyroll.crunchyroll()
        if not cr.logged_in():
            login(cfg.main.username, cfg.main.password)
            logging.debug("Logged in.")
        history_json = cr.history(50)
    except BaseException as e:
        logging.error(f"{e}")
        raise
    if len(history_json) == 0:
        logging.warning("No history returned from Crunchyroll API.")
    viewings: List[Viewing] = []
    for i in history_json:
        viewing = make_viewing(i)
        if viewing is not None:
            viewings.append(viewing)

    viewings.sort(reverse=True)
    update_status = write_feed(viewings, cfg)
    logging.info(f"{time.time() - start_time:2.0f}s {update_status}")


if __name__ == '__main__':
    parser = ArgumentParser(description="Make a Crunchyroll activity feed.")
    parser.add_argument('-o', '--outfile')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    if args.outfile is None:
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler(args.outfile)
    logging.basicConfig(handlers=(handler,),
                        format='%(asctime)s %(message)s',
                        datefmt='%Y-%m-%d %H:%M',
                        level=logging.DEBUG if args.verbose else logging.INFO)
    main()
