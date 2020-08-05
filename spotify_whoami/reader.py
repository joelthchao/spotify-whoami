import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import spotipy
from spotipy.util import prompt_for_user_token
from spotipy.oauth2 import SpotifyOAuth

from spotify_whoami import config


def login(username=None):
    scope = 'user-read-recently-played'
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET') or input('Client Secret: ').strip()
    username = username or input('Username: ').strip()
    token = prompt_for_user_token(username, scope=scope, client_id=config.CLIENT_ID,
                                  client_secret=client_secret, redirect_uri=config.REDIRECT_URI)
    return token


def read(token):
    sp = spotipy.Spotify(auth=token)
    res = sp.current_user_recently_played(limit=50)
    popularities = []
    track_ids = []
    for item in res['items']:
        played_at = item['played_at']
        track = item['track']
        popularities.append(track['popularity'] / 100)
        track_ids.append(track['id'])

    if len(track_ids) == 0:
        raise Exception('No track ids are found.')

    audio_features = sp.audio_features(track_ids)

    feature_keys = [
        ('danceability', 0, 1),
        ('energy', 0, 1),
        ('loudness', -30, 0),
        ('speechiness', 0, 1),
        ('acousticness', 0, 1),
        ('instrumentalness', 0, 1),
        ('liveness', 0, 1),
        ('valence', 0, 1),
        ('tempo', 0, 200),
    ]

    data = []
    for audio_feature in audio_features:
        for key, low, high in feature_keys:
            val = (audio_feature[key] - low) / (high - low)
            data.append((key, val))
    df = pd.DataFrame(data, columns=['feature', 'value'])

    return df


def plot(df):
    f, ax = plt.subplots()
    sns.stripplot(x='feature', y='value', data=df, alpha=0.25)
    sns.pointplot(x='feature', y='value', data=df, join=False, palette='dark',
                  markers='D', scale=0.5, ci=None)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize=6)
    plt.show()


if __name__ == '__main__':
    token = login()
    df = read(token)
    plot(df)
