import pickle
import time
from time import sleep

import feedparser
import pandas as pd
import vlc
from urlvalidator import ValidationError, validate_url


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
        print(episode)


def update_played_episodes(played_episodes, playing_episode_link):
    played_episodes.append(playing_episode_link)
    PLAYED_EPISODES_PICKLE = "played_episodes.pkl"
    open_file = open(PLAYED_EPISODES_PICKLE, "wb")
    pickle.dump(played_episodes, open_file)
    open_file.close()
    print(f"\nPlayed episodes ({len(played_episodes)}):")
    print_played_episodes(played_episodes=played_episodes)


def playing(sound):
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(sound)
    player.set_media(media)
    player.play()
    sleep(5)  # Or however long you expect it to take to open vlc
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
    df = pd.DataFrame(
        data=data, columns=["Published Date", "Title", "Episode Duration", "MP3 Link"]
    )
    return df


def save_played_episodes(entries):
    all_episodes = [get_episode_info(entry) for entry in entries]
    all_episodes_df = get_table_for_episodes(data=all_episodes)
    played_episodes = get_played_episodes()
    played_episodes_df = all_episodes_df[
        all_episodes_df["MP3 Link"].isin(played_episodes)
    ]
    played_episodes_df.to_excel("played_theeconomist.xlsx")


def play_latest_episode():
    Feed = feedparser.parse(THE_ECONOMIST_RSS_LINK)
    all_mp3 = get_all_mp3(entries=Feed.entries)
    played_episodes = get_played_episodes()
    unplayed_episodes = get_unplayed_episodes(
        played_episodes=played_episodes, all_mp3=all_mp3
    )
    playing_episode_link = unplayed_episodes[0]
    playing(sound=playing_episode_link)
    print(f"{playing_episode_link} has been played.")
    update_played_episodes(
        played_episodes=played_episodes,
        playing_episode_link=playing_episode_link,
    )
    save_played_episodes(entries=Feed.entries)


THE_ECONOMIST_RSS_LINK = "https://rss.acast.com/theeconomistallaudio"

while True:
    play_latest_episode()
