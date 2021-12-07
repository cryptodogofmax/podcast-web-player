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
from termcolor import colored, cprint
from urlvalidator import ValidationError, validate_url

pretty.install()
f = Figlet(font="mini")
color = list(np.random.choice(range(256), size=3))
print_in_color = lambda x: cprint(x, "blue", attrs=["bold"])
print_in_color(emoji.emojize(":headphone: Max Podcast Player :headphone:"))
print_in_color(f.renderText("Max Podcast Player"))
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


def get_published_as_key(published):
    published = published.replace(" ", "")
    published = published.replace(":", "")
    published = published.replace(",", "")
    return published


def get_all_mp3(entries):
    mp3s = []
    for entry in entries:
        links = entry["links"]
        mp3_links = get_mp3_from_links(links)
        mp3s += mp3_links
    return mp3s


def get_played_episodes():
    PLAYED_EPISODES_PICKLE = "played_episodes.pkl"
    try:
        open_file = open(PLAYED_EPISODES_PICKLE, "rb")
        played_episodes = pickle.load(open_file)
        open_file.close()
    except:
        played_episodes = []
    return played_episodes


def get_unplayed_episodes(played_episodes, all_mp3):
    unplayed_episodes = [x for x in all_mp3 if x not in played_episodes]
    return unplayed_episodes


def print_played_episodes(played_episodes):
    for episode in played_episodes:
        print_in_color(episode)


def update_played_episodes(played_episodes, playing_episode_link):
    played_episodes.append(playing_episode_link)
    PLAYED_EPISODES_PICKLE = "played_episodes.pkl"
    open_file = open(PLAYED_EPISODES_PICKLE, "wb")
    pickle.dump(played_episodes, open_file)
    open_file.close()
    print_in_color(f"\n{len(played_episodes)} played episodes:")
    # print_played_episodes(played_episodes=played_episodes)


def playing(sound):
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(sound)
    player.set_media(media)
    player.play()
    sleep(15)  # Or however long you expect it to take to open vlc
    while player.is_playing():
        sleep(1)


def get_episode_info(entry0):
    podcast_links = entry0["links"]
    mp3_link = get_mp3_from_links(podcast_links)[0]
    published = entry0["published"]
    title = entry0["title"]
    itunes_duration = entry0["itunes_duration"]
    return [published, title, itunes_duration, mp3_link]


def get_table_for_episodes(data):
    df = pd.DataFrame(data=data, columns=COLUMNS)
    return df


def save_played_episodes(current_playing):
    played_in_excel = pd.read_excel("played_theeconomist.xlsx", engine="openpyxl")
    played_in_excel = played_in_excel[COLUMNS]
    current_playing = current_playing[COLUMNS]
    played_in_excel.append(current_playing, ignore_index=True)
    played_in_excel.sort_values(by=["Published Date"])
    played_in_excel.to_excel("played_theeconomist.xlsx")
    print_in_color(f"Played Episodes: \n{played_in_excel}")
    return played_in_excel


def get_total_seconds(d1):
    if ":" in d1:
        hh, mm, ss = d1.split(":")
        total_seconds = int(ss) + 60 * int(mm) + 60 * 60 * int(hh)
    else:
        total_seconds = int(d1)
    return total_seconds


def print_total_time(played_episodes_df):
    durations = played_episodes_df["Episode Duration"].tolist()
    seconds_list = [get_total_seconds(d) for d in durations]
    total_in_seconds = sum(seconds_list)
    ss = total_in_seconds % 60
    mm = int((total_in_seconds - ss) / 60 % 60)
    hh = int((total_in_seconds - ss - 60 * mm) / 3600)
    print(f"\nTotal listening time: {hh} hours {mm} minutes {ss} seconds")


def get_mp3_link_the_daily(entry):
    links = entry["links"]
    link = [link for link in links if "audio" in link["type"]]
    mp3_link = ""
    if len(link) == 1:
        mp3_link = link[0]["href"]
    return mp3_link


def get_the_daily_episode_info(entry):
    published = entry["published"]
    title = entry["title"]
    mp3_link = get_mp3_link_the_daily(entry=entry)
    itunes_duration = entry["itunes_duration"]
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
    print(f"All Episodes: \n{all_episodes}")
    return all_episodes


def get_unplayed_episodes_df(episodes, played_episodes):
    unplayed_episodes_df = episodes[~episodes["MP3 Link"].isin(played_episodes)]
    unplayed_episodes_df.sort_values(by=["Published Date"])
    print(f"\nUnplayed Episodes: \n{unplayed_episodes_df}")
    return unplayed_episodes_df


def play_latest_episode():
    all_episodes_df = get_all_episodes_df()
    played_episodes = get_played_episodes()
    unplayed_episodes_df = get_unplayed_episodes_df(
        episodes=all_episodes_df, played_episodes=played_episodes
    )
    current_playing = unplayed_episodes_df.head(1)
    print(f"\nCurrently Playing: \n{current_playing}")
    playing_episode_link = current_playing["MP3 Link"].iloc[0]
    playing_episode_title = current_playing["Title"].iloc[0]
    print(f"\nCurrently playing: \n{playing_episode_title} \n{playing_episode_link}")
    playing(sound=playing_episode_link)
    print(f"\nFinished playing: \n{playing_episode_link} has been played.")
    update_played_episodes(
        played_episodes=played_episodes,
        playing_episode_link=playing_episode_link,
    )
    played_episodes_df = save_played_episodes(current_playing=current_playing)
    print_total_time(played_episodes_df=played_episodes_df)


while True:
    play_latest_episode()
