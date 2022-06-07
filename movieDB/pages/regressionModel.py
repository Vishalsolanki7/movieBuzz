import os
# enable results in terminal
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")
django.setup()

import numpy as np
import pandas as pd
# import math

from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

import matplotlib.pyplot as plt


def get_Movie_df(Movie):
    # store records into a dataframe
    movie_df = pd.DataFrame()
    movie_df['Year'] = pd.Series(list(map(lambda x: int(x.year), Movie.objects.only("year"))))
    movie_df['Title'] = pd.Series(list(map(lambda x: x.title, Movie.objects.only("title"))))
    movie_df['Genre'] = pd.Series(list(map(lambda x: x.genres, Movie.objects.only("genres"))))
    movie_df['Rating'] = pd.Series(list(map(lambda x: float(x.rating), Movie.objects.only("rating"))))
    movie_df['MetScore'] = pd.Series(list(map(lambda x: int(x.metascore), Movie.objects.only("metascore"))))
    movie_df['Votes'] = pd.Series(list(map(lambda x: int(x.votes), Movie.objects.only("votes"))))
    movie_df['Earned'] = pd.Series(
        list(map(lambda x: float(x.gross_earning_in_mil), Movie.objects.only("gross_earning_in_mil"))))
    # movie_df['Actor'] = pd.Series(list(map(lambda x: x.actor, Movie.objects.only("actor"))))
    # movie_df['Director'] = pd.Series(list(map(lambda x: x.director, Movie.objects.only("director"))))
    # print(movie_df['Earned'])
    # Remove the row with 0 (originally None)
    movie_df.replace(0, np.nan, inplace=True)
    movie_df = movie_df.dropna()

    # Convert category variable to indicator variable
    dummy_df = pd.get_dummies(movie_df.Genre)
    # dummy_df = pd.get_dummies(movie_df.Genre, prefix = 'Genre')
    movie_df = movie_df.join(dummy_df)
    # print(movie_df['Year'])

    return movie_df


def get_Actor_df(Actor):
    actor_df = pd.DataFrame()
    actor_df['Name'] = pd.Series(list(map(lambda x: x.name, Actor.objects.only("name"))))
    actor_df['Date'] = pd.Series(list(map(lambda x: x.date, Actor.objects.only("date"))))
    actor_df['Masterpiece'] = pd.Series(list(map(lambda x: x.masterpiece, Actor.objects.only("masterpiece"))))
    actor_df['AwardWin'] = pd.Series(list(map(lambda x: int(x.award_win), Actor.objects.only("award_win"))))
    actor_df['AwardNom'] = pd.Series(list(map(lambda x: int(x.award_nom), Actor.objects.only("award_nom"))))
    # string split by ', ', only key first 4 columns
    masterpiece_tmp = pd.DataFrame(list(actor_df['Masterpiece'].str.split(', '))).drop([4, 5, 6], axis=1)
    masterpiece_tmp.columns = ['Masterpiece_1', 'Masterpiece_2', 'Masterpiece_3', 'Masterpiece_4']
    actor_df = actor_df.join(masterpiece_tmp)
    return actor_df
    # pass


def get_Director_df(Director):
    director_df = pd.DataFrame()
    director_df['Name'] = pd.Series(list(map(lambda x: x.name, Director.objects.only("name"))))
    director_df['Date'] = pd.Series(list(map(lambda x: x.date, Director.objects.only("date"))))
    director_df['Masterpiece'] = pd.Series(list(map(lambda x: x.masterpiece, Director.objects.only("masterpiece"))))
    # string split by ', ', only key first 4 columns
    masterpiece_tmp = pd.DataFrame(list(director_df['Masterpiece'].str.split(', '))).drop([4, 5], axis=1)
    masterpiece_tmp.columns = ['Masterpiece_1', 'Masterpiece_2', 'Masterpiece_3', 'Masterpiece_4']
    director_df['AwardWin'] = pd.Series(list(map(lambda x: int(x.award_win), Director.objects.only("award_win"))))
    director_df['AwardNom'] = pd.Series(list(map(lambda x: int(x.award_nom), Director.objects.only("award_nom"))))
    # print(masterpiece_tmp)
    director_df = director_df.join(masterpiece_tmp)
    return director_df


def build_lg_model(Movie, Director, Actor):
    movie_df = get_Movie_df(Movie)
    # actor_df = get_Actor_df(Actor)
    # director_df = get_Director_df(Director)
    filter_data = []
    # SELECT m._meta.pk.name AS mID: to avoid 'InvalidQuery: Raw query must include the primary key'
    # sql_string = "SELECT m._meta.pk.name AS mID, m.title AS title, m.rating AS rating, m.votes AS votes, m.metascore AS metoscore, \
    #     m.gross_earning_in_mil AS gross, d.name AS name, d.award_win AS d_win, d.award_nom AS d_nom, \
    #     a.name AS star, a.award_win AS a_win, a.award_nom AS a_nom \
    #     FROM ((pages_director AS d LEFT JOIN pages_movie AS m ON d.name = m.director_id) \
    #     LEFT JOIN pages_actor AS a ON a.name = m.actor_id)"

    # for records in Movie.objects.raw(sql_string):
    #     filter_data.append(list(records))
    # code above still has error

    # X columns:
    # ['Year', 'Rating', 'MetScore', 'Votes', 'Action', 'Adventure',
    # 'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family',
    # 'Fantasy', 'Horror', 'Mystery', 'Romance', 'Thriller']
    # X = movie_df.drop(['Genre', 'Title', 'Earned', 'Actor', 'Director'], axis = 1)
    X = movie_df.drop(['Genre', 'Title', 'Earned'], axis=1)
    y = movie_df.Earned
    # print(X.columns)

    model_lg = LinearRegression()
    # scores = []
    # kfold = KFold(n_splits=3, shuffle=True, random_state=3)
    # for i, (train, test) in enumerate(kfold.split(X, y)):
    #     model_lg.fit(X.iloc[train,:], y.iloc[train])
    #     score = model_lg.score(X.iloc[test,:], y.iloc[test])
    #     scores.append(score)

    # Split X and y into X_
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=1)
    # fit
    model_lg.fit(X_train, y_train)
    # test
    y_predict = model_lg.predict(X_test)
    regression_model_mse = mean_squared_error(y_predict, y_test)
    score = model_lg.score(X_test, y_test)
    # predict

    return model_lg, X_test.columns, regression_model_mse, score

# movie_df = get_Movie_df(Movie)
# print(movie_df[:5])

# model_lg, X_test, y_test = build_lg_model(Movie, Director, Actor)
# for idx, col_name in enumerate(X_train.columns):
#     print(model_lg.coef_[idx], idx)

# actor_df = get_Actor_df(Actor)
# print(actor_df.loc[:5,:])

# director_df = get_Director_df(Director)
# print(director_df.iloc[:5])

# SQL v.s. panda
# airport_freq.merge(airports[airports.ident == 'KLAX'][['id']], 
#                  left_on='airport_ref', 
#                  right_on='id', 
#                  how='inner')[['airport_ident', 'type', 'description', 'frequency_mhz']]

# select airport_ident, type, description, frequency_mhz from airport_freq join airports on airport_freq.airport_ref = airports.id where airports.ident = 'KLAX'

# print(movie_df.merge(director_df, left_on='Director', right_on = 'Name', suffixes = ('', 'Dir'), how = 'left').loc[:5])

# movie_df.Director.isin(director_df.Name)
#
