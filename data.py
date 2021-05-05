import csv


def get_music_list():
    """renvoie la liste des dictionnaires contenant les informations de toutes les musiques disponibles sous la forme
    : {'id': ,'titre': ,'auteur': ,'genre': ,'url': } """
    with open("Base_de_données.csv", 'r', encoding="utf-8") as csv_file:
        music_list = []
        csv_reader = csv.reader(csv_file, delimiter=";")
        next(csv_reader)  # On passe  la première ligne pour lire obtenir les musiques
        for row in csv_reader:
            music_list.append({"id": row[0], "titre": row[1], "auteur": row[2], "genre": row[3], "url": row[4]})
    return music_list


def genres():
    """Retourne une liste de dictionnaires de tous les genres disponibles avec leurs identifiants sous la forme {
    'id': ,'genre' } """
    music_list = get_music_list()
    genres = []
    i = 1
    for music in music_list:
        genre = music['genre']
        new_genre = True
        for el in genres:
            if genre == el['genre']:
                new_genre = False
        if new_genre:
            genres.append({"id": i, "genre": genre})
            i += 1
    return genres


def auteurs():
    """Retourne la liste de tous les auteurs disponibles"""
    music_list = get_music_list()
    auteurs = []
    for music in music_list:
        auteur = music['auteur']
        if auteur not in auteurs:
            auteurs.append(auteur)
    return auteurs
