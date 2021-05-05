from flask import Flask, render_template, redirect, url_for, request, flash
from data import get_music_list, genres
from wtforms import Form, StringField, validators, SelectField
from random import shuffle
from youtube_to_python import import_musique
from rfc3987 import parse
import os

# Variables globales, utilisées par les différentes pages
music_list = get_music_list()  # dictionnaire de tous les morceaux ayant pour clés : id, titre, auteur, genre, url
music_styles = genres()  # liste des dictionnaires des genres existants dans la base de données
songs = []  # liste des morceaux qui seront joués dans la partie (même style que music_list, avec un chemin
# pour les musiques qui vont être joué)
answers = []  # Une liste des réponses de l'utilisateur de la forme suiavante [(titre, auteur, réponse), ...]
first_time = True  # Initialise la partie (pour ne lancer qu'une seule fois le son 'here we go' quand on arrive)
nb_music_to_load = 5
numero_music = 1  # l'étape du jeu à laquelle on est rendu

genre_form = []
for dic_genre in music_styles:
    genre = dic_genre["genre"]
    genre_form.append((genre, genre))  # Créé une liste adaptée au SelectField


class ItemForm(Form):
    """Item Form Class utilisée pour le formulaire de add_music.html"""
    title = StringField('Title', [validators.Length(min=1, max=200)])
    author = StringField('Author', [validators.Length(min=1, max=100)])
    genre = SelectField(u'Genre', choices=genre_form)
    url = StringField('Url')


# Création du site web
app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'


# Index
@app.route('/')
def index():
    global songs
    global answers
    global first_time
    global numero_music
    # on réinitialise les variables utiles pour éviter des problèmes si l'utilisateur recommence une partie
    songs = []
    answers = []
    first_time = True
    numero_music = 1
    return render_template('home.html')


# About
@app.route('/about_us')
def about():
    return render_template('about_us.html')


# Project
@app.route('/project')
def project():
    return render_template('project.html')


# Automatic_selection
@app.route('/auto_sel', methods=['GET', 'POST'])
def auto_sel():
    """Gere la gestion automatique des musiques.
    L'utilisateur coche les genres de musiques qu'il veut, et l'ensemble des musiques correspondantes est rajouté"""
    global songs
    items = music_styles
    # on récupère les informations du formulaire (liste des id des genres sélectionnés)
    value = request.form.getlist('check')
    if value:  # S'il y a une information
        for id in value:
            for music in music_list:
                # On rajoute l'ensemble des musiques dont le genre correspond à ceux sélectionnés
                if music["genre"] == music_styles[int(id) - 1]['genre']:
                    songs.append(music)
        return redirect(url_for('loading'))
    return render_template('auto_selection.html', items=items)


# Sel_Manu
@app.route('/manual_selection', methods=['GET', 'POST'])
def manu_sel():
    """Ici, l'utilisateur coche les musiques qu'il souhaite entendre"""
    global songs
    value = request.form.getlist("check")
    if value:
        for id in value:
            songs.append(music_list[int(id) - 1])
        return redirect(url_for('loading'))
    return render_template('manual_selection.html', musics=music_list)


# Loading
@app.route('/loading', methods=['GET', 'POST'])
def loading():
    global songs
    global nb_music_to_load
    """On charge ici les musiques que le joueur a selectionnée
    On reçoit également un nombre max de musique à jouer"""
    if request.method == 'POST':
        nb_music_to_load = request.form["nb_music"]  # Nombre de musique à jouer
        if nb_music_to_load.isdigit():  # Si c'est bien un chiffre
            nb_music_to_load = int(nb_music_to_load)  # On le stocke dans la variable globale
        else:
            nb_music_to_load = 5  # Sinon, on prend une valeur par défaut 

        if not os.path.exists("morceaux"):  # Répertoire temporaire, où les musiques seront télechargées et converties
            os.makedirs("morceaux")

        if len(songs) > nb_music_to_load:  # S'il y a plus de musiques choisies que le nombre voulu
            shuffle(songs)  # On mélange
            while len(songs) > nb_music_to_load:  # et on supprime jusqu'à le que compte soit bon
                songs.pop()

        for song in songs:  # Pour les musiques restantes
            old_path, new_path = "morceaux/" + song["id"] + ".mp3", "static/musics/" + song["id"] + ".mp3"
            if not os.path.exists(new_path):  # Si la musique n'est pas déjà téléchargée
                import_musique(song["url"], song["id"])  # On la télécharge
                os.rename(old_path, new_path)  # On la déplace dans le bon chemin
            song["chemin"] = new_path  # On enregistre le chemin vers le fichier audio

        shuffle(songs)  # Et on remelange la musique encore une fois
        return redirect(url_for('play'))

    else:
        return render_template('chargement.html')


# Play
@app.route('/play', methods=['GET', 'POST'])
def play():
    """Fonction appelée lorsqu'on va sur le lien play
    Un extrait est joué pendant 30 secondes, puis un formulaire de réponse apparaît, et l'utilisateur doit saisir
    la musique correspondante (c'est le principe du blindtest...)

    On limite également le nombre de musiques"""
    global first_time
    global songs
    global answers
    global nb_music_to_load
    global numero_music

    if songs:  # S'il y a des musiques à jouer
        # on ne veut pas que la partie dure trop longtemps, donc on limite le nombre de musiques à 10
        nb_music_to_play = len(songs) + numero_music - 1  # nombre de musiques à jouer initialement
        song = songs[0]  # On choisit la première musique
        path_to_song = song["chemin"]
        title = song["titre"]
        author = song["auteur"]
        genre = song["genre"]

        if request.method == 'POST':  # Si la requête est 'POST' (ie, si l'utilisateur a cliqué sur le bouton submit)
            first_time = False
            answer = request.form["answer"]  # On récupère sa réponse
            answers.append((title, author, answer))  # On modifie les réponses
            # On enlève ici la musique jouée, et pas avant,
            # sinon, s'il ne reste qu'une seule musique, on ne peut pas récupérer la réponse du joueur
            del songs[0]
            numero_music += 1
            shuffle(songs)  # On mélange la liste des musiques
            return redirect(url_for('play'))

        return render_template('play.html', first_time=first_time, path_to_song=path_to_song, title=title,
                               author=author, genre=genre, numero_music=numero_music, nb_music_to_play=nb_music_to_play)
    else:
        return redirect(url_for('score'))


# Add Music to the CSV file
@app.route('/add_music', methods=['GET', 'POST'])
def add_music():
    """On ajoute des musiques à notre base de données"""
    global music_list
    form = ItemForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data  # Getting the form from HTML
        author = form.author.data
        genre = form.genre.data
        url = form.url.data
        id = int(music_list[-1]["id"]) + 1
        try:
            parse(url, rule='IRI')  # vérifie la validité de l'url
            with open('Base_de_données.csv', 'a') as fd:
                # Writing in the csv file
                fd.write('\n' + str(id) + ';' + str(title) + ';' + str(author) + ';' + str(genre) + ';' + str(url))

            music_list = get_music_list()  # On actualise la liste des musiques

            flash('Music Added to the blindtest list', 'success')
            return redirect('/add_music')
        except ValueError:
            flash('Not a valid url', 'warning')  # renvoie un message d'erreur

    genres = []  # récupère la liste des genres
    for el in music_styles:
        genres.append(el['genre'])

    return render_template('add_music.html', form=form, genres=genres)


# Scores
@app.route('/score')
def score():
    """Page des scores
    On récupère la liste de toutes les réponses, et on rajoute un point par bonne réponse.
    Une bonne réponse est le titre de la musique"""
    global answers
    max_score = len(answers)
    user_score = 0
    for titre, auteur, user_answer in answers:
        if user_answer.lower() == titre.lower():
            user_score += 1
    return render_template('score.html', answers=answers, max_score=max_score, user_score=user_score)


if __name__ == '__main__':
    app.run(debug=True)
