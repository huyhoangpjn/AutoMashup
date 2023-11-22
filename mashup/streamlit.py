import streamlit as st
import os
from pathlib import Path
import demucs.separate
import librosa
import numpy as np
global vocals_song_path
os.makedirs('./input', exist_ok=True)
os.makedirs('./separated/mdx_extra', exist_ok=True)
os.makedirs('./output', exist_ok=True)

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
    
# Titre de l'application
st.title("AutoMashup")

# Upload de fichiers audio
audio_file = st.file_uploader("Sélectionnez un fichier audio pour la voix (formats pris en charge : mp3, wav)", type=["mp3", "wav"])

# Check if files are uploaded
if audio_file is not None:
    # Utilisez la méthode name pour obtenir le nom du fichier
    filename = audio_file.name
    path = f"./input/{filename}"

    with open(path, "wb") as f:
        f.write(audio_file.read())
    demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", "mdx_extra", path])

    instru_path = f'./separated/mdx_extra/{filename}/no_vocals.mp3'
    vocals_path = f'./separated/mdx_extra/{filename}/vocals.mp3'

if os.path.exists('./separated/mdx_extra/'):
    for index, folder_name in enumerate(os.listdir('./separated/mdx_extra/')):
        folder_path = os.path.join('./separated/mdx_extra/', folder_name)
        if os.path.isdir(folder_path):
            col1, col2 = st.columns(2)
            col1.write(folder_name)
            button1_id = f"button1_{index}"
            button2_id = f"button2_{index}"
            if col2.button("Vocals", key=button1_id):
                st.session_state.vocals_path = './separated/mdx_extra/' + folder_name + '/vocals.mp3'
                st.session_state.vocals_song_path = './input/' + folder_name + '.mp3'

            if col2.button("Instru", key=button2_id):
                st.session_state.instru_path = './separated/mdx_extra/' + folder_name + '/no_vocals.mp3'
                st.session_state.instru_song_path = './input/' + folder_name + '.mp3'


if st.button("Generate Mashup"):
    vocals_path = st.session_state.vocals_path
    vocals_song_path = st.session_state.vocals_song_path
    instru_song_path = st.session_state.instru_song_path
    instru_path = st.session_state.instru_path

    song1, sr1 = librosa.load(vocals_song_path)
    vocals, sr1 = librosa.load(vocals_path)

    song2, sr2 = librosa.load(instru_song_path)
    instru, sr2 = librosa.load(instru_path)

    tempo1, beat_frames1 = librosa.beat.beat_track(y=song1, sr=sr1)
    tempo2, beat_frames2 = librosa.beat.beat_track(y=song2, sr=sr2)

    beat_frames2_aligned = beat_frames2 * (tempo1 / tempo2)

    instru_aligned = np.roll(instru, int(beat_frames2_aligned[0] - beat_frames1[0]))

    size = max(len(instru_aligned), len(vocals))
    mashup = increase_array_size(instru_aligned, size) + increase_array_size(vocals, size)
    st.audio(mashup, sample_rate=sr1)

