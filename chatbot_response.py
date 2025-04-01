import connect2spotify as c2p
import train_with_bert as twb   
class ChatbotResponse:
    def __init__(self,mode):
        self.c2s = c2p.Connect2Spotify("app_config.json")
        self.c2s.mode == mode

    def generate_response(self,user_input,mode):
        self.c2s.mode = mode
        print(f"Current mode: {self.c2s.mode}")
        self.intent = twb.get_intent(user_input)
        if self.intent =="play":
            if self.c2s.mode == "lyric":
                lyric = self.__extractLyric(user_input)
                result = self.c2s.play_by_lyric(lyric)
                return result
            elif self.c2s.mode == "title":
                #user_input = "Play the song Believer by Imagine Dragons"
                title,singer = self.__extractTitleAndSinger(user_input)
                result = self.c2s.play(title,singer)
                return result
        elif self.intent == "pause":
            result = self.c2s.pause()
            return result
        elif self.intent == "skip":
            result = self.c2s.skip_to_next()
            return result
        elif self.intent == "title mode":
            result = self.c2s.change_mode_to_title()
            return result
        elif self.intent == "lyric mode":
            result = self.c2s.change_mode_to_lyric()
            return result
        
    def __extractLyric(self, user_input):
        user_input = user_input.lower()
        if "lyric" in user_input:
            return user_input.split("lyric", 1)[1].strip()
        elif "play" in user_input:
            print(user_input.split("play", 1)[1].strip())
            return user_input.split("play", 1)[1].strip()
        elif "lyrics" in user_input:
            return user_input.split("lyrics", 1)[1].strip()
        else:
            return user_input.strip()

    def __extractTitleAndSinger(self, user_input):
        user_input = user_input.lower()
        song_name = ""
        singer = ""
        
        if "by" in user_input:
            parts = user_input.split("by", 1)
            singer = parts[1].strip()
            if "play the song" in parts[0]:
                song_name = parts[0].split("play the song", 1)[1].strip()
            elif "play" in parts[0]:
                song_name = parts[0].split("play", 1)[1].strip()
        
        return song_name, singer