from pytube import YouTube
import moviepy.editor as mp
import os


def import_musique(url, name):
    """Télécharge une musique sur youtube et la place dans le dossier '/morceaux'

    :param url: lien YouTube de la vidéo à télécharger
    :param name: nom sous lequel enregistrer la vidéo
    :return: None
    """
    # téléchargement de la vidéo au format mp4
    i = 0
    try:
        yt = YouTube(url)
        video = yt.streams.first()
        video.download('./morceaux')
    except:
        if i >= 10:
            raise 'max recursive error'
        import_musique(url, name)

    # sélection du titre du morceaux (=titre du dernier fichier ajouté à "morceaux")
    a = os.listdir("./morceaux")
    a.sort(key=lambda s: os.path.getmtime(os.path.join("./morceaux", s)))
    titre_init = str(a[-1])

    # sélection de la vidéo avec moviepy
    clip = mp.VideoFileClip("./morceaux/" + titre_init).subclip(0, 30)

    # exportation du fichier son de la vidéo en mp3
    titre = name + ".mp3"  # prend peu de temps
    clip.audio.write_audiofile("./morceaux/" + titre)  # prend peu de temps aussi
