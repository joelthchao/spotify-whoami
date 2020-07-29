import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def main():
    auth_manager = auth()
    sp = spotipy.Spotify(auth_manager=auth_manager)
    res = sp.current_user_recently_played(limit=50)
    popularities = []
    track_ids = []
    for item in res['items']:
        played_at = item['played_at']
        track = item['track']
        popularities.append(track['popularity'] / 100)
        track_ids.append(track['id'])

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

    f, ax = plt.subplots()
    sns.stripplot(x='feature', y='value', data=df, alpha=0.25)
    sns.pointplot(x='feature', y='value', data=df, join=False, palette='dark',
                  markers='D', scale=0.5, ci=None)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=30, horizontalalignment='right', fontsize=6)
    plt.show()


def auth():
    scope = 'user-read-recently-played'
    client_id = os.environ.get('SPOTIPY_CLIENT_ID') or input('Client ID: ').strip()
    client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET') or input('Client Secret: ').strip()
    redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI') or input('Redirect URI: ').strip()
    username = os.environ.get('SPOTIPY_USERNAME') or input('Username: ').strip()
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        username=username,
        scope=scope)
    return auth_manager


if __name__ == '__main__':
    main()