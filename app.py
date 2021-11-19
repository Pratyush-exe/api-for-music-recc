from flask import Flask
from flask import request
import pandas as pd
import numpy as np
import random
from sklearn.cluster import KMeans
import json
from sklearn.decomposition import PCA

df = pd.read_csv(r'final.csv')

cols = ['artist', 'danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness',
        'instrumentalness', 'liveness', 'valence', 'tempo', 'duration_ms', 'time_signature', 'label']
non_categorical = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness',
                   'valence', 'tempo', 'duration_ms']
categorical = ['artist', 'key', 'mode', 'time_signature', 'label']

df[non_categorical] = df[non_categorical].apply(lambda x: (x - x.min()) / (x.max() - x.min()))

pca = PCA(0.95)
data = df.drop_duplicates()
data = pca.fit_transform(data[non_categorical])
data = pd.DataFrame(data)


def train(df_train):
    n = 1
    for _ in range(n):
        km = KMeans(
            n_clusters=4, init='random',
            n_init=10, max_iter=1000,
            tol=1e-04, random_state=0
        )
        y_km = km.fit(df_train)
    return km


def k_mean_distance(center_coordinates, data_coordiantes):
    summ = 0
    mag = 0
    for i in range(len(center_coordinates)):
        summ += (center_coordinates[i] - data_coordiantes[i]) ** 2
        mag += (data_coordiantes[i]) ** 2
    return (summ) * 0.5


km = train(data)
data = pd.DataFrame(data)
data['label'] = km.labels_
data['artist'] = df.artist
data['name'] = df.name
data['preview'] = df.preview
data['popularity'] = df.popularity
data['type'] = df.label
data.head()


def song_recommendation(song, data):
    arr = []
    dummy_df = data.loc[data['label'] == song.label.values[0]]
    for i in range(len(dummy_df.values)):
        if i > 51: break
        dist = k_mean_distance(dummy_df.values[i][0:7], song.values[0][0:7])
        arr.append((
            dummy_df.values[i][11] / (dist + 0.00000001) ** 2,
            dist,
            dummy_df.values[i][11],
            dummy_df.values[i][8],
            dummy_df.values[i][9],
            dummy_df.values[i][10],
            dummy_df.values[i][12]
        ))
    arr.sort()
    return arr


app = Flask(__name__)


@app.route("/")
def hello_world():
    user_input = request.args.get('name', default='', type=str)
    song_list = []
    for k in df['name']:
        if user_input.lower() in k.lower():
            song_list = df[df['name'] == k].index.values
            break

    if len(song_list) == 0 or user_input == '':
        return json.dumps({000:'Invalid Input'})
    else:
        print('-' * 100)
        song = data.loc[[random.choice(song_list)]]
        ans = song_recommendation(song, data)
        # j = 1
        # for i in ans[::-1]:
        #     print('Number:               ', j)
        #     print('Popularity/distance:  ', i[0])
        #     print('Artist:               ', i[3])
        #     print('Song Name:            ', i[4])
        #     print('Type:                 ', i[6])
        #     print('-' * 100)
        #     j += 1
        return json.dumps(ans)


if __name__ == '__main__':
    app.run()
