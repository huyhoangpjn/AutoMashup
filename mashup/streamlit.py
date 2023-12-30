import streamlit as st
import os
from mashup import mashup_technic_1, mashup_technic_2, mashup_technic_3
from utils import remove_track, key_finder
import io
import base64
import soundfile as sf
import allin1

## MASHUP METHODS
# mashup_technics = [('Mashup Technic 1', mashup_technic_1), ('Mashup Technic 2', mashup_technic_2), ('Mashup Technic 3', mashup_technic_3)]
mashup_technics = [('Mashup Technic 1', mashup_technic_1)]

os.makedirs('./input', exist_ok=True)
os.makedirs('./separated/htdemucs', exist_ok=True)
os.makedirs('./output', exist_ok=True)

st.set_page_config(layout="wide")  
# Titre de l'application
st.title("AutoMashup")
if st.checkbox("Advanced mode"):
    st.session_state.advanced = True
else:
    st.session_state.advanced = False
# Upload de fichiers audio

with st.form("audio-form", clear_on_submit=True):
    audio_file = st.file_uploader("Sélectionnez un fichier audio (formats pris en charge : mp3, wav)", type=["mp3", "wav"])
    submitted = st.form_submit_button("Envoyer le(s) fichier(s) et lancer le preprocessing")

# Check if files are uploaded
if submitted and audio_file:
    # Utilisez la méthode name pour obtenir le nom du fichier
    filename = audio_file.name
    path = f"./input/{filename}"

    with open(path, "wb") as f:
        f.write(audio_file.read())
    # allin1.analyze(path, out_dir='./struct', demix_dir='./separated')
    allin1.analyze(path, out_dir='./struct', demix_dir='./separated', keep_byproducts=True)
    key_finder(path)
    audio_file = None

if os.path.exists('./separated/htdemucs/'):
    for index, folder_name in enumerate(os.listdir('./separated/htdemucs/')):
        folder_path = os.path.join('./struct/' + folder_name + '.json')
        if os.path.exists(folder_path):
            if ("advanced" in st.session_state and st.session_state.advanced):
                col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
                col1.write(folder_name)
                button1_id = f"button1_{index}_1"
                button2_id = f"button2_{index}_1"
                button3_id = f"button3_{index}_1"
                button4_id = f"button4_{index}_1"
                button5_id = f"button5_{index}_1"
                button6_id = f"button6_{index}_1"
                if col2.button("Bass", key=button1_id):
                    st.session_state.bass = folder_name
                if col3.button("Drums", key=button2_id):
                    st.session_state.drums = folder_name
                if col4.button("Other", key=button3_id):
                    st.session_state.other = folder_name
                if col5.button("Vocals", key=button4_id):
                    st.session_state.vocals = folder_name
                if col6.button("Beat Structure", key = button5_id):
                    st.session_state.beat = folder_name
                if col7.button("Remove Track", key = button6_id):
                    remove_track(folder_name)
            else :
                col1, col2, col3, col4 = st.columns(4)
                col1.write(folder_name)
                button1_id = f"button1_{index}"
                button2_id = f"button2_{index}"
                button3_id = f"button3_{index}"
                if col2.button("Vocals", key=button1_id):
                    st.session_state.vocals = folder_name
                    st.session_state.beat = folder_name
                if col3.button("Instru", key=button2_id):
                    st.session_state.drums = folder_name
                    st.session_state.bass = folder_name
                    st.session_state.other = folder_name 
                if col4.button("Remove Track", key = button3_id):
                    remove_track(folder_name)

st.divider()


if ("advanced" in st.session_state and st.session_state.advanced):
    col1, col2, col3, col4, col5 = st.columns(5)  
    col1.header("Bass :")
    col1.write(st.session_state.bass if "bass" in st.session_state else "")

    col2.header("Drums :")
    col2.write(st.session_state.drums if "drums" in st.session_state else "")

    col3.header("Other :")
    col3.write(st.session_state.other if "other" in st.session_state else "")

    col4.header("Vocals :")
    col4.write(st.session_state.vocals if "vocals" in st.session_state else "")

    col5.header("Beat Structure :")
    col5.write(st.session_state.beat if "beat" in st.session_state else "")
else:
    col1, col2 = st.columns(2)  
    col1.header("Vocals :")
    col1.write(st.session_state.vocals if "vocals" in st.session_state else "")

    col2.header("Instru :")
    col2.write(st.session_state.other if "other" in st.session_state else "")


for mashup_technic in mashup_technics:
    if st.button(mashup_technic[0], disabled=not("beat" in st.session_state and ("vocals" in st.session_state or "bass" in st.session_state or "drums" in st.session_state or "other" in st.session_state))):
        tracks = {}
        for track in ["beat", "vocals", "bass", "other", "drums"]:
            if track in st.session_state:
                tracks[track] = st.session_state[track]
        mashup, sr = mashup_technic[1](tracks)
        st.audio(mashup, sample_rate=sr) 
        buffer = io.BytesIO()
        sf.write(buffer, mashup, sr, format='wav')
        # Encodez le fichier audio en base64
        b64 = base64.b64encode(buffer.getvalue()).decode()
        st.markdown(f'<a href="data:audio/wav;base64,{b64}" download="mashup.wav">Télécharger le fichier audio</a>', unsafe_allow_html=True)

