
import streamlit as st
import pandas as pd

import os
from pathlib import Path
from pydub import AudioSegment
from pydub import AudioSegment
from pydub.playback import play

# Create directories if they don't exist
os.makedirs('./input', exist_ok=True)
os.makedirs('./separated/mdx_extra', exist_ok=True)
os.makedirs('./output', exist_ok=True)

# Titre de l'application
st.title("AutoMashup")

# Sélection du fichier audio pour la voix
audio_file1 = st.file_uploader("Sélectionnez un fichier audio pour la voix (formats pris en charge : mp3, wav)", type=["mp3", "wav"])

# Sélection du fichier audio pour la musique
audio_file2 = st.file_uploader("Sélectionnez un fichier audio pour la musique (formats pris en charge : mp3, wav)", type=["mp3", "wav"])

# Check if files are uploaded
if audio_file1 is not None and audio_file2 is not None:
    # Save the uploaded files to temporary paths
    voice_path = "./input/voice_temp.wav"
    music_path = "./input/music_temp.wav"
    
    with open(voice_path, "wb") as f:
        f.write(audio_file1.read())
    
    with open(music_path, "wb") as f:
        f.write(audio_file2.read())


    import demucs.separate


    demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", "mdx_extra", music_path])

    instru_path = './separated/mdx_extra/' + os.path.splitext(os.path.basename(music_path))[0] + '/no_vocals.mp3'

    import librosa
    import soundfile as sf
    import numpy as np
    from IPython.display import Audio

    def adjust_bpm(bpm):
        while bpm < 80 or bpm > 160:
            if bpm < 80:
                bpm *= 2
            elif bpm > 160:
                bpm /= 2
        return bpm

    def increase_array_size(arr, new_size):
        """
        Increases the size of the array if its length is below the given threshold.

        :param arr: The NumPy array to increase.
        :param threshold: The minimum length required for the array.
        :param new_size: The new desired size of the array.
        :return: The array with an increased size if necessary.
        """
        if len(arr) < new_size:
            # Create a new array with the new size
            increased_arr = np.zeros(new_size)

            # Copy elements from the original array to the new array
            increased_arr[:len(arr)] = arr

            return increased_arr
        else:
            return arr

    import librosa
    import numpy as np


    song1, sr1 = librosa.load(song1_path)
    vocals, sr1 = librosa.load(vocals_path)

    song2, sr2 = librosa.load(song2_path)
    instru, sr2 = librosa.load(instru_path)

    tempo1, beat_frames1 = librosa.beat.beat_track(y=song1, sr=sr1)
    tempo2, beat_frames2 = librosa.beat.beat_track(y=song2, sr=sr2)

    beat_frames2_aligned = beat_frames2 * (tempo1 / tempo2)

    instru_aligned = np.roll(instru, int(beat_frames2_aligned[0] - beat_frames1[0]))

    size = max(len(instru_aligned), len(vocals))
    mashup = increase_array_size(instru_aligned, size) + increase_array_size(vocals, size)

    Audio(mashup, rate=sr1)

    def increase_array_size(array, new_size):
        return np.interp(np.linspace(0, 1, new_size), np.linspace(0, 1, len(array)), array)

    song1, sr1 = librosa.load(song1_path)
    vocals, sr1 = librosa.load(vocals_path)

    song2, sr2 = librosa.load(song2_path)
    instru, sr2 = librosa.load(instru_path)

    # Extraction des tempos et des cadences de battement
    tempo1, beat_frames1 = librosa.beat.beat_track(y=song1, sr=sr1)
    tempo2, beat_frames2 = librosa.beat.beat_track(y=song2, sr=sr2)

    # Ajustement des cadences de battement
    beat_frames2_aligned = np.linspace(0, len(beat_frames2) - 1, len(beat_frames2)) * (tempo1 / tempo2)

    # Décalage de l'instrumental pour l'alignement temporel
    # Ajustez manuellement le décalage temporel en changeant la valeur de offset
    offset = 10  # ajustez cette valeur en conséquence
    instru_aligned = np.roll(instru, int(beat_frames2_aligned[0] - beat_frames1[0]) + offset)

    # Ajustement de la taille des tableaux
    size = max(len(instru_aligned), len(vocals))
    instru_aligned = increase_array_size(instru_aligned, size)
    vocals = increase_array_size(vocals, size)

    # Création du mashup
    mashup = instru_aligned + vocals

    Audio(mashup, rate=sr1)

    # Show the mashup using Streamlit's audio widget
    #st.audio(mashup, format="audio/mp3", caption="Mashup Audio")
    st.button("Play Mashup Audio", on_click=lambda: play(AudioSegment.from_file(mashup, format="mp3")))
































































# # Vérifier si un fichier a été téléchargé
# if audio_file1:
#     st.audio(audio_file1, format='voice/wav')

#     # Bouton de traitement
#     if st.button("Traiter le fichier"):
#         # Sauvegarder le fichier audio téléchargé temporairement
#         temp_dir1 = Path("temp_voice")
#         temp_dir1.mkdir(exist_ok=True)
#         temp_file_path1 = temp_dir1 / audio_file1.name
#         with open(temp_file_path1, "wb") as temp_file:
#             temp_file.write(audio_file1.getvalue())

#     #     # Charger le fichier audio avec pydub
#     #     audio = AudioSegment.from_file(temp_file_path)

#         # # Exemple de traitement : doubler la vitesse
#         # audio_processed = audio.speedup(playback_speed=2.0)

#     # # Sauvegarder le fichier traité
#     # output_file_path_1 = temp_dir / "voice.wav"
#     # audio_processed.export(output_file_path_1, format="wav")

#     # Afficher le lien de téléchargement pour le fichier traité
#     st.success("Traitement terminé!")
#     st.audio(output_file_path_1, format='audio/wav', key='processed_voice')
#     st.markdown(f"**[Télécharger le fichier traité](sandbox:/temp_audio/processed_voice.wav)**")

#         # # Nettoyer les fichiers temporaires
#         # for file in temp_dir.iterdir():
#         #     file.unlink()
#         # temp_dir.rmdir()

# # Vérifier si un fichier a été téléchargé
# if audio_file2:
#     st.audio(audio_file2, format='audio/wav')

#     # Bouton de traitement
#     if st.button("Traiter le fichier"):
#         # Sauvegarder le fichier audio téléchargé temporairement
#         temp_dir2 = Path("temp_voice")
#         temp_dir2.mkdir(exist_ok=True)
#         temp_file_path2 = temp_dir1 / audio_file2.name
#         with open(temp_file_path2, "wb") as temp_file:
#             temp_file.write(audio_file2.getvalue())

#     # # Sauvegarder le fichier traité
#     # output_file_path_2 = temp_dir2 / "music.wav"
#     # audio_processed.export(output_file_path_2, format="wav")

#     # Afficher le lien de téléchargement pour le fichier traité
#     st.success("Traitement terminé!")
#     st.audio(output_file_path_2, format='music/wav', key='processed_audio')
#     st.markdown(f"**[Télécharger le fichier traité](sandbox:/temp_audio/processed_audio.wav)**")


# import demucs.separate

# demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", "mdx_extra", output_file_path_1])
# demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", "mdx_extra", output_file_path_2])

# vocals_path = './separated/mdx_extra/' + song1_path[song1_path.rfind('/')+1:song1_path.rfind('.')] + '/vocals.mp3'
# instru_path = './separated/mdx_extra/' +song2_path[song2_path.rfind('/')+1:song2_path.rfind('.')] + '/no_vocals.mp3'

# import librosa
# import soundfile as sf
# import numpy as np
# from IPython.display import Audio

# def adjust_bpm(bpm):
#     while bpm < 80 or bpm > 160:
#         if bpm < 80:
#             bpm *= 2
#         elif bpm > 160:
#             bpm /= 2
#     return bpm

# def increase_array_size(arr, new_size):
#     """
#     Increases the size of the array if its length is below the given threshold.

#     :param arr: The NumPy array to increase.
#     :param threshold: The minimum length required for the array.
#     :param new_size: The new desired size of the array.
#     :return: The array with an increased size if necessary.
#     """
#     if len(arr) < new_size:
#         Create a new array with the new size
#         increased_arr = np.zeros(new_size)

#         Copy elements from the original array to the new array
#         increased_arr[:len(arr)] = arr

#         return increased_arr
#     else:
#         return arr
    



# song1, sr1 = librosa.load(output_file_path_2)
# vocals, sr1 = librosa.load(vocals_path)

# song2, sr2 = librosa.load(output_file_path_1)
# instru, sr2 = librosa.load(instru_path)

# tempo1, beat_frames1 = librosa.beat.beat_track(y=song1, sr=sr1)
# tempo2, beat_frames2 = librosa.beat.beat_track(y=song2, sr=sr2)

# beat_frames2_aligned = beat_frames2 * (tempo1 / tempo2)

# instru_aligned = np.roll(instru, int(beat_frames2_aligned[0] - beat_frames1[0]))

# size = max(len(instru_aligned), len(vocals))
# mashup = increase_array_size(instru_aligned, size) + increase_array_size(vocals, size)

# Audio(mashup, rate=sr1)

# def increase_array_size(array, new_size):
#     return np.interp(np.linspace(0, 1, new_size), np.linspace(0, 1, len(array)), array)

# song1, sr1 = librosa.load(output_file_path_2)
# vocals, sr1 = librosa.load(vocals_path)

# song2, sr2 = librosa.load(output_file_path_1)
# instru, sr2 = librosa.load(instru_path)

# #Extraction des tempos et des cadences de battement
# tempo1, beat_frames1 = librosa.beat.beat_track(y=song1, sr=sr1)
# tempo2, beat_frames2 = librosa.beat.beat_track(y=song2, sr=sr2)

# #Ajustement des cadences de battement
# beat_frames2_aligned = np.linspace(0, len(beat_frames2) - 1, len(beat_frames2)) * (tempo1 / tempo2)

# #Décalage de l'instrumental pour l'alignement temporel
# #Ajustez manuellement le décalage temporel en changeant la valeur de offset
# offset = 10  # ajustez cette valeur en conséquence
# instru_aligned = np.roll(instru, int(beat_frames2_aligned[0] - beat_frames1[0]) + offset)

# #Ajustement de la taille des tableaux
# size = max(len(instru_aligned), len(vocals))
# instru_aligned = increase_array_size(instru_aligned, size)
# vocals = increase_array_size(vocals, size)

# #Création du mashup
# mashup = instru_aligned + vocals

# Audio(mashup, rate=sr1)






































# def run_python_code(code):
#     try:
#         exec(code)
#     except Exception as e:
#         st.error(f"Error: {e}")

# def main():
#     st.title("Run Python Code ")

#     # File upload widget
#     uploaded_file = st.file_uploader("Choose a Python file", type="py")

#     if uploaded_file is not None:
#         st.write("### Uploaded Python File:")
#         st.code(uploaded_file.getvalue())

#         # Read the file
#         code = uploaded_file.getvalue().decode("utf-8")

#         # Button to run the code
#         if st.button("Run Code"):
#             st.write("### Output:")
#             run_python_code(code)

# if __name__ == "__main__":
#     main()


# import requests

# def run_python_code(code):
#     try:
#         exec(code)
#     except Exception as e:
#         st.error(f"Erreur : {e}")

# def main():
#     st.title("Exécuter un Programme depuis GitHub avec Streamlit")

#     # Entrée de l'URL GitHub
#     github_url = st.text_input("Entrez l'URL du fichier Python sur GitHub")

#     # Bouton pour exécuter le code
#     if st.button("Exécuter le Code depuis GitHub"):
#         try:
#             # Télécharger le contenu du fichier depuis GitHub
#             response = requests.get(github_url)
#             code = response.text

#             # Afficher le code
#             st.write("### Code Téléchargé:")
#             st.code(code)

#             # Exécuter le code
#             st.write("### Sortie:")
#             run_python_code(code)

#         except Exception as e:
#             st.error(f"Erreur lors du téléchargement et de l'exécution du code : {e}")

# if __name__ == "__main__":
#     main()
