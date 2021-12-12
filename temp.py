import vlc, easygui
import requests

url = "https://sphinx.acast.com/theeconomistallaudio/checksandbalance/checksandbalance-taiwanwonder/media.mp3"
doc = requests.get(url)
with open("audio.mp3", "wb") as f:
    f.write(doc.content)

media = easygui.fileopenbox(title="Choose media to open")
player = vlc.MediaPlayer(media)
while True:
    choice = easygui.buttonbox(
        title="@biglesp Audio Player",
        msg="Press Play to start",
        choices=["Play", "Pause", "Stop", "New"],
    )
    print(choice)
    if choice == "Play":
        player.play()
    elif choice == "Pause":
        player.pause()
    elif choice == "Stop":
        player.stop()
    elif choice == "New":
        media = easygui.fileopenbox(title="Choose media to open")
        player = vlc.MediaPlayer(media)
    else:
        break
