please edit the app_config.json

1. go to the website https://developer.spotify.com/dashboard
2. click right top to log into spotify
3. go to the website https://developer.spotify.com/dashboard again
4. Create right top 'Create App"
5. fill in all necessary field. Remind the requested URL has been provided in app_config.json
6. click on the top right "settings"
7. change the client id and client secret into yours on that app_config.json
8. Save the file


To open the app

Currently please type command 
```sh
python user_interface.py
``` 
on command prompt. 

Please make sure you have downloaded everything on command prompt or anaconda(what ever which one you like
```sh
pip install torch spotipy transformers datasets SpeechRecognition spotipy tk pyaudio scikit-learn accelerate
``` 

The first time will train the model, and it will open longer(12-20 minutes). If it is not working, just close the chatbot and open again by typing into command 
```sh
python user_interface.py
``` 
