from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Max, Min
from .models import Movie, Director, Actor
from .regressionModel import build_lg_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

import csv, os
from os.path import join
from .forms import MovieForm
from django.core.paginator import Paginator
from itertools import repeat
import numpy as np
import pandas as pd

# enable results in terminal
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myapp.settings")
django.setup()


def home(request):
    return render(request, "home.html", {})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return render(request, 'insert_data.html')
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'registration.html', context)


def clean_string_list(stringa):
    """Utility function, to improve formatting in 'masterpiece' column.
    Change "['Enter the Void', 'Druid Peak', 'Blinders', 'Boys on Film X']" into 
    'Enter the Void, Druid Peak, Blinders, Boys on Film X'
    """
    bad_chars = "[]\"\"\'\'"
    for c in bad_chars:
        stringa = stringa.replace(c, "")
    return stringa


def director(request):
    base_dir = os.path.abspath(__file__)

    for i in range(3):
        base_dir = os.path.dirname(base_dir)

    with open(base_dir + '/Data/director.csv') as g:
        reader = csv.DictReader(g)
        for line in reader:
            try:
                val = int(line['dr_awards_wins'])
            except ValueError:
                val = 0

            try:
                val_nom = int(line['dr_awards_nomi tions'])
            except ValueError:
                val_nom = 0

            tmp = Director(name=line['dr_name'],
                           date=line['dr_date'],
                           place=line['dr_place'],
                           masterpiece=clean_string_list(line['dr_knownfor']),
                           award_win=val,
                           award_nom=val_nom,
                           person_link=line['dr_link'],
                           award_link=line['dr_awards_link'])

            tmp.save()

    all_director = Director.objects.all()

    paginator = Paginator(all_director, 50)
    page = request.GET.get('page')
    directors = paginator.get_page(page)

    return render(request, "director.html", {'Director': directors})


def movie(request):
    base_dir = os.path.abspath(__file__)

    for i in range(3):
        base_dir = os.path.dirname(base_dir)

    with open(base_dir + '/Data/movie_data_0325.csv') as f:
        reader = csv.DictReader(f)
        for line in reader:

            try:
                director_nm = Director.objects.get(name=line['Director'])
            except Director.DoesNotExist:
                director_nm = None

            try:
                act_nm = Actor.objects.get(name=line['Actor'])
            except Actor.DoesNotExist:
                act_nm = None

            try:
                rate = float(line['Rating'])
            except ValueError:
                rate = 0

            try:
                score = int(line['Metascore'])
            except ValueError:
                score = 0

            try:
                vote_num = int(line['Votes'])
            except ValueError:
                vote_num = 0

            try:
                earned = float(line['Gross_Earning_in_Mil'])
            except ValueError:
                earned = 0.0

            tmp = Movie(movieid=line['Movie_ID'],
                        year=line['Year'],
                        rank=line['Rank'],
                        title=line['Title'],
                        description=line['Description'],
                        duration=line['Duration'],
                        genres=line['Genre'],
                        rating=rate,
                        metascore=score,
                        votes=vote_num,
                        gross_earning_in_mil=earned,
                        director=director_nm,
                        actor=act_nm)

            tmp.save()

    all_movies = Movie.objects.all()

    paginator = Paginator(all_movies, 50)
    page = request.GET.get('page')
    movies = paginator.get_page(page)

    return render(request, "movie.html", {'Movie': movies})


def actor(request):
    base_dir = os.path.abspath(__file__)

    for i in range(3):
        base_dir = os.path.dirname(base_dir)

    with open(base_dir + '/Data/star.csv') as g:
        reader = csv.DictReader(g)
        for line in reader:
            try:
                val = int(line['st_awards_wins'])
            except ValueError:
                val = 0

            try:
                val_nom = int(line['st_awards_nominations'])
            except ValueError:
                val_nom = 0


            tmp = Actor(name=line['st_name'],
                        date=line['st_date'],
                        place=line['st_place'],
                        masterpiece=clean_string_list(line['st_knownfor']),
                        award_win=val,
                        award_nom=val_nom,
                        person_link=line['st_link'],
                        award_link=line['st_awards_link'])

            tmp.save()

    all_actor = Actor.objects.all()

    paginator = Paginator(all_actor, 50)

    page = request.GET.get('page')
    actors = paginator.get_page(page)

    return render(request, "actor.html", {'Actor': actors})


def insert_data(request):
    return render(request, "insert_data.html", {})


def insert_data_submission(request):
    year = request.POST["year"]
    title = request.POST["title"]
    genres = request.POST["type"]
    descrption = request.POST["description"]
    director_name = request.POST["director"]
    actor_name = request.POST["actor"]

    new_actor = Actor(name=actor_name)
    new_director = Director(name=director_name)

    new_actor.save()
    new_director.save()

    director_name = Director.objects.get(name=director_name)
    actor_name = Actor.objects.get(name=actor_name)

    new_movie = Movie(title=title, year=year, genres=genres, description=descrption, director=director_name,
                      actor=actor_name)
    new_movie.save()
    return render(request, "insert_data.html", {})


def edit_movie(request, pk):
    post = get_object_or_404(Movie, pk=pk)
    if request.method == 'POST':
        form = MovieForm(request.POST, instance=post)

        try:
            if form.is_valid():
                form.save()
                messages.success(request, 'Your movie has been updated!')
        except Exception as e:
            messages.warning(request, 'Your movie was not updated: Error {}'.format(e))
    else:
        form = MovieForm(instance=post)
    context = {
        'form': form,
        'post': post
    }
    return render(request, "new_movie.html", context)


def prediction(request):
    template = "prediction.html"
    gross_template = None
    title = '9'  # default is '9.jpg' in prediction.html
    # the model
    model_lg, paramters, mse, score = build_lg_model(Movie, Director, Actor)

    # the movie to be predicted
    if request.GET.get('prediction'):
        query = request.GET.get('prediction')
        tep = "%%%s%%" % query
        # filter_data = Movie.objects.raw(
        #     "SELECT m.title AS title, m.year AS year, m.rating AS rating, m.votes AS votes, m.metascore AS metascore, m.genres AS genre \
        #             m.gross_earning_in_mil AS gross \
        #             FROM pages_movie AS m WHERE m.title LIKE %s", [tep])
        filter_data = Director.objects.raw(
            "SELECT m.title AS title, m.year AS year, m.rating AS rating, m.votes AS votes, m.metascore AS metascore, \
            m.gross_earning_in_mil AS gross, m.genres AS genre, d.name AS name, d.award_win AS d_win, d.award_nom AS d_nom, \
            a.name AS star, a.award_win AS a_win, a.award_nom AS a_nom \
            FROM ((pages_director AS d LEFT JOIN pages_movie AS m ON d.name = m.director_id) \
            LEFT JOIN pages_actor AS a ON a.name = m.actor_id) \
            WHERE m.title LIKE %s", [tep])
        limit_tuple = filter_data[:1]  # get the first records
        # title, year, rating, metascore, votes, genre, gross = None, None, None, None, None, None, None
        # print(limit_tuple)
        for movie in limit_tuple:
            title = movie.title
            year = movie.year
            rating = movie.rating
            metascore = movie.metascore
            votes = movie.votes
            genre = movie.genre
            gross = movie.gross

        # Build dataframe to be predicted
        genre_list = ['Action', 'Adventure',
                      'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family',
                      'Fantasy', 'Horror', 'Mystery', 'Romance', 'Thriller']
        genre_index = genre_list.index(genre)
        tmp_list = list(repeat(0, len(genre_list)))
        tmp_list[genre_index] = 1
        predict_df = pd.DataFrame(columns=['Year', 'Rating', 'MetScore', 'Votes', 'Action', 'Adventure',
                                           'Animation', 'Biography', 'Comedy', 'Crime', 'Drama', 'Family',
                                           'Fantasy', 'Horror', 'Mystery', 'Romance', 'Thriller'])
        predict_df.loc[0] = [year, rating, metascore, votes] + tmp_list
        gross_predict = model_lg.predict(predict_df)
        gross_template = [gross_predict[0], gross]

    context = {
        'score': round(score, 3),
        'cols': paramters,
        'coefs': [round(elem, 2) for elem in model_lg.coef_],
        'mse': round(mse, 3),
        'box_offic': gross_template,
        'search_title': title,
        'poster_path': join('images', 'poster', title + '.jpg')
    }
    print(join('images', 'poster', title + '.jpg'))
    return render(request, template, context)

def new_movie(request):
    template = 'new_movie.html'
    form = MovieForm(request.POST or None)
    if form.is_valid():
        form.save()
    else:
        form = MovieForm()
    context = {
        'form': form,
    }
    return render(request, template, context)


def delete_movie(request, pk):
    post = get_object_or_404(Movie, pk=pk)
    try:
        if request.method == 'POST':
            form = MovieForm(request.POST, instance=post)
            post.delete()
            messages.success(request, 'You have successfully deleted the movie')
        else:
            form = MovieForm(instance=post)
    except Exception as e:
        messages.warning(request, 'The movie cannot be deleted: Error {}'.format(e))
    context = {
        'form': form,
        'post': post
    }
    return render(request, "new_movie.html", context)


def search(request):
    template = 'recommendation.html'
    query = request.GET.get('q')
    tep = "%%%s%%" % query
    filter_title = Director.objects.raw(
        "SELECT m.title AS title, d.name AS name, a.name AS star \
        FROM pages_director AS d LEFT JOIN pages_movie AS m ON d.name = m.director_id \
        LEFT JOIN pages_actor AS a ON a.name = m.actor_id \
        WHERE m.title LIKE %s", [tep])

    filter_data = Director.objects.raw(
        "SELECT m.title AS title, m.rating AS rating, m.votes AS votes, m.metascore AS metascore, \
        m.gross_earning_in_mil AS gross, d.name AS name, d.award_win AS d_win, d.award_nom AS d_nom, \
        a.name AS star, a.award_win AS a_win, a.award_nom AS a_nom \
        FROM pages_director AS d LEFT JOIN pages_movie AS m ON d.name = m.director_id \
        LEFT JOIN pages_actor AS a ON a.name = m.actor_id \
        WHERE m.title LIKE %s", [tep])
    try:
        limit_tuple = filter_data[:1]
        for movie in limit_tuple:
            title = movie.title
            rating = movie.rating
            votes = movie.votes
            metascore = movie.metascore
            gross = movie.gross
            d_award = movie.d_win + movie.d_nom
            a_award = movie.a_win + movie.a_nom

        d_win_max = Director.objects.all().aggregate(r1=Max('award_win'))
        d_win_min = Director.objects.all().aggregate(r2=Min('award_win'))
        d_nom_max = Director.objects.all().aggregate(r3=Max('award_nom'))
        d_nom_min = Director.objects.all().aggregate(r4=Min('award_nom'))

        d_range = d_win_max.get('r1') + d_nom_max.get('r3') - d_win_min.get('r2') - d_nom_min.get('r4')
        new_d_award = (d_award - (d_win_min.get('r2') - d_nom_min.get('r4'))) / d_range * 100

        a_win_max = Actor.objects.all().aggregate(r1=Max('award_win'))
        a_win_min = Actor.objects.all().aggregate(r2=Min('award_win'))
        a_nom_max = Actor.objects.all().aggregate(r3=Max('award_nom'))
        a_nom_min = Actor.objects.all().aggregate(r4=Min('award_nom'))

        a_range = a_win_max.get('r1') + a_nom_max.get('r3') - a_win_min.get('r2') - a_nom_min.get('r4')
        new_a_award = (a_award - (a_win_min.get('r2') - a_nom_min.get('r4'))) / a_range * 100

        rating_max = Movie.objects.all().aggregate(rm1=Max('rating'))
        rating_min = Movie.objects.all().aggregate(rm2=Min('rating'))
        rating_range = rating_max.get('rm1') - rating_min.get('rm2')
        new_rating = (rating - rating_min.get('rm2')) / rating_range * 100

        votes_max = Movie.objects.all().aggregate(rm1=Max('votes'))
        votes_min = Movie.objects.all().aggregate(rm2=Min('votes'))
        votes_range = votes_max.get('rm1') - votes_min.get('rm2')
        new_votes = (votes - votes_min.get('rm2')) / votes_range * 100

        metascore_max = Movie.objects.all().aggregate(rm1=Max('metascore'))
        metascore_min = Movie.objects.all().aggregate(rm2=Min('metascore'))
        metascore_range = metascore_max.get('rm1') - metascore_min.get('rm2')
        new_metascore = (metascore - metascore_min.get('rm2')) / metascore_range * 100

        gross_max = Movie.objects.all().aggregate(rm1=Max('gross_earning_in_mil'))
        gross_min = Movie.objects.all().aggregate(rm2=Min('gross_earning_in_mil'))
        gross_range = gross_max.get('rm1') - gross_min.get('rm2')
        new_gross = (gross - gross_min.get('rm2')) / gross_range * 100

        context = {
            'filter_title': filter_title,
            'limit_tuple': limit_tuple,
            'new_rating': new_rating,
            'new_votes': new_votes,
            'new_d_award': new_d_award,
            'new_a_award': new_a_award,
            'ew_metascoren': new_metascore,
            'new_gross': new_gross
        }
    except UnboundLocalError:
        return render(request, "notFound.html")
    return render(request, template, context)
