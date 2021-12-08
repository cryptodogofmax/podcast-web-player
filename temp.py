import pickle
import time
from time import sleep

import emoji
import feedparser
import numpy as np
import pandas as pd
import vlc
from pyfiglet import Figlet
from rich import pretty, print
from tabulate import tabulate
from termcolor import colored, cprint
from urlvalidator import ValidationError, validate_url

COLUMNS = ["Published Date", "Title", "Episode Duration", "MP3 Link"]


def get_mp3_from_links(links):
    mp3_links = []
    for link in links:
        for k, v in link.items():
            if k == "href":
                try:
                    validate_url(v)
                    if v[-4:] == ".mp3":
                        mp3_links.append(v)
                except ValidationError:
                    raise ValidationError("Invalid URL")
    return mp3_links


def get_mp3_link_the_daily(entry):
    links = entry["links"]
    link = [link for link in links if "audio" in link["type"]]
    mp3_link = ""
    if len(link) == 1:
        mp3_link = link[0]["href"]
    return mp3_link


def get_table_for_episodes(data):
    df = pd.DataFrame(data=data, columns=COLUMNS)
    return df


def get_the_daily_episode_info(entry):
    published = entry["published"]
    title = entry["title"]
    mp3_link = get_mp3_link_the_daily(entry=entry)
    itunes_duration = entry["itunes_duration"]
    return [published, title, itunes_duration, mp3_link]


def get_episode_info(entry0):
    podcast_links = entry0["links"]
    mp3_link = get_mp3_from_links(podcast_links)[0]
    published = entry0["published"]
    title = entry0["title"]
    itunes_duration = entry0["itunes_duration"]
    return [published, title, itunes_duration, mp3_link]


def get_all_data():
    N_latest_episodes = 5
    # The Daily
    the_daily_rss_link = "https://feeds.simplecast.com/54nAGcIl"
    Feed_the_daily = feedparser.parse(the_daily_rss_link)
    the_daily_data = [
        get_the_daily_episode_info(entry=entry)
        for entry in Feed_the_daily.entries[:N_latest_episodes]
    ]
    # The NPR Politics Podcast
    the_npr_politics_rss = "https://feeds.npr.org/510310/podcast.xml"
    Feed_the_npr_politics = feedparser.parse(the_npr_politics_rss)
    the_npr_politics_data = [
        get_the_daily_episode_info(entry=entry)
        for entry in Feed_the_npr_politics.entries[:N_latest_episodes]
    ]
    # The Economist Podcast
    THE_ECONOMIST_RSS_LINK = "https://rss.acast.com/theeconomistallaudio"
    Feed_the_economist = feedparser.parse(THE_ECONOMIST_RSS_LINK)
    the_economist_data = [
        get_episode_info(entry0=entry)
        for entry in Feed_the_economist.entries[:N_latest_episodes]
    ]
    total_data = the_daily_data + the_economist_data + the_npr_politics_data
    return total_data


def get_all_episodes_df():
    total_data = get_all_data()
    all_episodes = get_table_for_episodes(data=total_data)
    all_episodes.sort_values(by=["Published Date"])
    #     print(f"All Episodes: \n{all_episodes}")
    return all_episodes


all_episodes = get_all_episodes_df()
print(all_episodes)
# print(tabulate(all_episodes, headers="keys", tablefmt="psql"))
