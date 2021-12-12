import pickle
import time
from time import sleep

import emoji
import feedparser
import numpy as np
import pandas as pd
import vlc
from dateutil import parser
from pyfiglet import Figlet
from rich import pretty, print
from tabulate import tabulate
from termcolor import colored, cprint
from urlvalidator import ValidationError, validate_url

# pd.options.display.max_rows = None

pretty.install()
f = Figlet(font="mini")
color = list(np.random.choice(range(256), size=3))
print_in_color = lambda x: cprint(x, "blue", attrs=["bold"])
print_in_color(emoji.emojize(":headphone: Max Podcast Player :headphone:"))
print_in_color(f.renderText("Max Podcast Player"))
COLUMNS = ["Published Date", "Title", "Episode Duration", "MP3 Link"]
the_bankless_rss = "http://podcast.banklesshq.com/rss"
the_daily_rss_link = "https://feeds.simplecast.com/54nAGcIl"
the_npr_politics_rss = "https://feeds.npr.org/510310/podcast.xml"
THE_ECONOMIST_RSS_LINK = "https://rss.acast.com/theeconomistallaudio"
the_sheng_espresso_rss = "https://feeds.fireside.fm/sheng-espresso/rss"
the_contrary_rss = "https://onthecontrary.libsyn.com/rss"
the_failure_rss = "https://anchor.fm/s/60d69380/podcast/rss"
the_3_things_rss = "https://www.spreaker.com/show/5008053/episodes/feed"
the_lunhuan_rss = "https://lunhuan.typlog.io/episodes/feed.xml"
the_hbr_rss = "http://feeds.harvardbusiness.org/harvardbusiness/ideacast"
the_exponential_rss = (
    "http://feeds.harvardbusiness.org/harvardbusiness/exponential-view"
)
# podcast_channels = [the_hbr_rss, the_exponential_rss]
podcast_channels = [
    the_bankless_rss,
    the_daily_rss_link,
    the_npr_politics_rss,
    THE_ECONOMIST_RSS_LINK,
    the_sheng_espresso_rss,
    the_contrary_rss,
    the_failure_rss,
    the_3_things_rss,
    the_lunhuan_rss,
    the_hbr_rss,
    the_exponential_rss,
]


def get_mp3_link_from_feed_entry(entry):
    links = entry["links"]
    link = [link for link in links if "audio" in link["type"]]
    mp3_link = ""
    if len(link) == 1:
        mp3_link = link[0]["href"]
    return mp3_link


def get_common_episode_info(entry):
    published = entry["published"]
    title = entry["title"]
    mp3_link = get_mp3_link_from_feed_entry(entry=entry)
    itunes_duration = entry["itunes_duration"]
    return [published, title, itunes_duration, mp3_link]


def get_data_from_rss(rss_link, top_N):
    Feed = feedparser.parse(rss_link)
    if top_N > 100:
        the_data = [get_common_episode_info(entry=entry) for entry in Feed.entries]
    else:
        the_data = [
            get_common_episode_info(entry=entry) for entry in Feed.entries[:top_N]
        ]
    return the_data


def get_played_episodes_filtering_rss_feed(rss_link, played_episodes_list):
    Feed = feedparser.parse(rss_link)
    the_data = [
        get_common_episode_info(entry=entry)
        for entry in Feed.entries
        if get_mp3_link_from_feed_entry(entry=entry) in played_episodes_list
    ]
    return the_data


def get_played_episodes_data_from_rss(played_episodes_list):
    total_played_data = []
    for rss in podcast_channels:
        data = get_played_episodes_filtering_rss_feed(
            rss_link=rss, played_episodes_list=played_episodes_list
        )
        total_played_data += data
    return total_played_data


def get_all_data_from_rss():
    total_data = []
    for rss in podcast_channels:
        data = get_data_from_rss(rss_link=rss, top_N=101)
        total_data += data
    return total_data


def get_all_episodes_df_from_rss(total_data):
    total_data = get_topN_episodes_data_from_all_rss()
    all_episodes = get_table_for_episodes(data=total_data)
    all_episodes.sort_values(by=["Published Date"])
    return all_episodes


def get_played_episodes_df(episodes, played_episodes):
    played_episodes_df = episodes[episodes["MP3 Link"].isin(played_episodes)]
    played_episodes_df = played_episodes_df.sort_values(
        by=["Published Date"], ascending=False
    )
    print(f"\nUnplayed Episodes: \n{played_episodes_df}")
    print_in_color("Total time to listen: ")
    print_total_time(played_episodes_df=played_episodes_df)
    return played_episodes_df


def print_total_time(played_episodes_df):
    durations = played_episodes_df["Episode Duration"].tolist()
    seconds_list = [get_total_seconds(d) for d in durations]
    total_in_seconds = sum(seconds_list)
    ss = total_in_seconds % 60
    mm = int((total_in_seconds - ss) / 60 % 60)
    hh = int((total_in_seconds - ss - 60 * mm) / 3600)
    print(f"Total listening time: {hh} hours {mm} minutes {ss} seconds")
    print_in_color(
        emoji.emojize(
            ":headphone: :headphone: ================================================================= :headphone: :headphone:"
        )
    )


def save_played_to_excel():
    played_episodes_list = get_played_episodes_from_pickle()
    total_played_data = get_played_episodes_data_from_rss(
        played_episodes_list=played_episodes_list
    )
    played_episodes_df = get_table_for_episodes(data=total_played_data)
    played_episodes_df["Published Date"] = played_episodes_df["Published Date"].apply(
        lambda t: pd.to_datetime(t).date()
    )
    played_episodes_df.to_excel("played_theeconomist.xlsx")
    print_in_color(f"\nPlayed Episodes: \n{played_episodes_df}\n")
    print_total_time(played_episodes_df=played_episodes_df)
    return played_episodes_df


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


def get_played_episodes_from_pickle():
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


def update_played_episodes_list_to_pickle(played_episodes, playing_episode_link):
    played_episodes.append(playing_episode_link)
    played_episodes_set = set(played_episodes)
    played_episodes = list(played_episodes_set)
    PLAYED_EPISODES_PICKLE = "played_episodes.pkl"
    open_file = open(PLAYED_EPISODES_PICKLE, "wb")
    pickle.dump(played_episodes, open_file)
    open_file.close()
    print_in_color(f"\n{len(played_episodes)} played episodes:")
    print_played_episodes(played_episodes=played_episodes)


def playing(audio_link):
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(audio_link)
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
    df["Published Date"] = df["Published Date"].apply(parser.parse)
    df = df.sort_values(by=["Published Date"], ascending=False)
    return df


def get_total_seconds(d1):
    if ":" in d1:
        t = d1.split(":")
        if len(t) == 3:
            hh, mm, ss = t
            total_seconds = int(ss) + 60 * int(mm) + 60 * 60 * int(hh)
        elif len(t) == 2:
            mm, ss = t
            total_seconds = int(ss) + 60 * int(mm)
    else:
        total_seconds = int(d1)
    return total_seconds


def get_topN_episodes_data_from_all_rss(topN=5):
    total_data = []
    for rss in podcast_channels:
        data = get_data_from_rss(rss_link=rss, top_N=topN)
        total_data += data
    return total_data


def get_all_episodes():
    total_data = get_topN_episodes_data_from_all_rss()
    all_episodes = get_table_for_episodes(data=total_data)
    print(f"All Episodes: \n{all_episodes}")
    return all_episodes


def get_unplayed_episodes_df(episodes, played_episodes_list):
    unplayed_episodes_df = episodes[~episodes["MP3 Link"].isin(played_episodes_list)]
    unplayed_episodes_df = unplayed_episodes_df.sort_values(
        by=["Published Date"], ascending=False
    )
    print(f"\nUnplayed Episodes: \n{unplayed_episodes_df}")
    print_in_color("Total time to listen: ")
    print_total_time(played_episodes_df=unplayed_episodes_df)
    return unplayed_episodes_df


def play_latest_episode():
    all_episodes_df = get_all_episodes()
    played_episodes_list = get_played_episodes_from_pickle()
    played_episodes_df = save_played_to_excel()
    unplayed_episodes_df = get_unplayed_episodes_df(
        episodes=all_episodes_df, played_episodes_list=played_episodes_list
    )
    if len(unplayed_episodes_df) > 0:
        current_playing = unplayed_episodes_df.head(1)
        print(f"\nCurrently Playing: \n{current_playing}")
        playing_episode_link = current_playing["MP3 Link"].iloc[0]
        playing_episode_title = current_playing["Title"].iloc[0]
        print(
            f"\nCurrently playing: \n{playing_episode_title} \n{playing_episode_link}"
        )
        playing(audio_link=playing_episode_link)
        print(f"\nFinished playing: \n{playing_episode_link} has been played.")
        update_played_episodes_list_to_pickle(
            played_episodes=played_episodes_list,
            playing_episode_link=playing_episode_link,
        )
        played_episodes_df = save_played_to_excel()
        print_total_time(played_episodes_df=played_episodes_df)
    return unplayed_episodes_df


def run():
    unplayed_episodes_df = play_latest_episode()
    while len(unplayed_episodes_df) > 0:
        play_latest_episode()


run()
