import streamlit as st
import os
import demucs.separate
from mashup import mashup_technic_1, mashup_technic_2, mashup_technic_3
import io
import base64
import soundfile as sf

## MASHUP METHODS

mashup_technics = [('Mashup Technic 1', mashup_technic_1), ('Mashup Technic 2', mashup_technic_2), ('Mashup Technic 3', mashup_technic_3)]


global vocals_song_path
os.makedirs('./input', exist_ok=True)
os.makedirs('./separated/mdx_extra', exist_ok=True)
os.makedirs('./output', exist_ok=True)
    
# Titre de l'application
st.title("AutoMashup")

# Upload de fichiers audio

with st.form("audio-form", clear_on_submit=True):
    
    audio_file = st.file_uploader("Sélectionnez un fichier audio pour la voix (formats pris en charge : mp3, wav)", type=["mp3", "wav"])
    submitted = st.form_submit_button("Upload and seperate")

# Check if files are uploaded
if submitted and audio_file:
    # Utilisez la méthode name pour obtenir le nom du fichier
    filename = audio_file.name
    path = f"./input/{filename}"

    with open(path, "wb") as f:
        f.write(audio_file.read())
    demucs.separate.main(["--mp3", "--two-stems", "vocals", "-n", "mdx_extra", path])

    instru_path = f'./separated/mdx_extra/{filename}/no_vocals.mp3'
    vocals_path = f'./separated/mdx_extra/{filename}/vocals.mp3'
    
    # Avoid run demucs multiples times if the uploaded file still exist
    audio_file = None

if os.path.exists('./separated/mdx_extra/'):
    for index, folder_name in enumerate(os.listdir('./separated/mdx_extra/')):
        folder_path = os.path.join('./separated/mdx_extra/', folder_name)
        if os.path.isdir(folder_path):
            col1, col2, col3 = st.columns(3)
            col1.write(folder_name)
            button1_id = f"button1_{index}"
            button2_id = f"button2_{index}"
            if col2.button("Vocals", key=button1_id):
                st.session_state.vocals = folder_name
            if col3.button("Instru", key=button2_id):
                st.session_state.instru = folder_name

st.divider()
col4, col5= st.columns(2)  

col4.header("Vocals :")
col4.write(st.session_state.vocals if "vocals" in st.session_state else "")

col5.header("Instru :")
col5.write(st.session_state.instru if "instru" in st.session_state else "")

for mashup_technic in mashup_technics:
    if st.button(mashup_technic[0], disabled=not ("vocals" in st.session_state and "instru" in st.session_state)):
        vocals = st.session_state.vocals
        instru = st.session_state.instru 
        mashup, sr = mashup_technic[1](vocals, instru)
        st.audio(mashup, sample_rate=sr)

        # Add a progress bar
        progress_bar = st.progress(0)

        # Use tqdm to display progress in the console
        for _ in tqdm(range(100), desc="Processing", position=0, leave=True):
            # Simulate some processing time
            time.sleep(0.01)
            progress_bar.progress(_/100)

        mashup, sr = mashup_technic[1](vocals, instru)
        st.audio(mashup, sample_rate=sr)
        
        buffer = io.BytesIO()
        sf.write(buffer, mashup, sr, format='wav')

        # Encodez le fichier audio en base64
        b64 = base64.b64encode(buffer.getvalue()).decode()

        st.markdown(f'<a href="data:audio/wav;base64,{b64}" download="mashup.wav">Télécharger le fichier audio</a>', unsafe_allow_html=True)

        # Add a delete button for the selected songs
        if st.button("Supprimer les chansons sélectionnées"):
            if "vocals" in st.session_state:
                vocals_folder = f'./separated/mdx_extra/{st.session_state.vocals}'
                shutil.rmtree(vocals_folder, ignore_errors=True)
                st.session_state.pop("vocals", None)
            if "instru" in st.session_state:
                instru_folder = f'./separated/mdx_extra/{st.session_state.instru}'
                shutil.rmtree(instru_folder, ignore_errors=True)
                st.session_state.pop("instru", None)

