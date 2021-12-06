import pickle
import time
from time import sleep

import feedparser
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
    print(f"Played episodes: {len(played_episodes)}")
    return set(played_episodes)


def get_unplayed_episodes(played_episodes, all_mp3):
    unplayed_episodes = [x for x in all_mp3 if x not in played_episodes]
    return unplayed_episodes


def update_played_episodes(played_episodes, playing_episdoe_link):
    played_episodes_set = set(played_episodes)
    played_episodes_set.add(playing_episdoe_link)
    PLAYED_EPISODES_PICKLE = "played_episodes.pkl"
    open_file = open(PLAYED_EPISODES_PICKLE, "wb")
    played_episodes_list = list(played_episodes_set)
    print(f"Played episodes: {len(played_episodes_list)}, {played_episodes_list}")
    pickle.dump(played_episodes_list, open_file)
    open_file.close()
    print(f"Played episodes: {len(played_episodes_set)}")


def playing(sound):
    vlc_instance = vlc.Instance()
    player = vlc_instance.media_player_new()
    media = vlc_instance.media_new(sound)
    player.set_media(media)
    player.play()
    sleep(5)  # Or however long you expect it to take to open vlc
    while player.is_playing():
        sleep(1)


def play_latest_episode():
    Feed = feedparser.parse(THE_ECONOMIST_RSS_LINK)
    all_mp3 = get_all_mp3(entries=Feed.entries)
    played_episodes = get_played_episodes()
    unplayed_episodes = get_unplayed_episodes(
        played_episodes=played_episodes, all_mp3=all_mp3
    )
    playing_episode_link = unplayed_episodes[0]
    playing(sound=playing_episode_link)
    print(f"This episode has been played.")
    update_played_episodes(
        played_episodes=[],
        playing_episdoe_link=playing_episode_link,
    )


THE_ECONOMIST_RSS_LINK = "https://rss.acast.com/theeconomistallaudio"

# while True:
play_latest_episode()
