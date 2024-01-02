import streamlit as st
import os
from mashup import mashup_technic_1, mashup_technic_2, mashup_technic_3
from utils import remove_track, key_finder, get_path, load_track, \
split_track, key_from_dict
import io
import base64
import soundfile as sf
import allin1
import json
from barfi import st_barfi, Block

## MASHUP METHODS
# mashup_technics = [('Mashup Technic 1', mashup_technic_1), ('Mashup Technic 2', mashup_technic_2), ('Mashup Technic 3', mashup_technic_3)]
mashup_technics = [('Mashup Technic 1', mashup_technic_1)]

os.makedirs('./input', exist_ok=True)
os.makedirs('./separated/htdemucs', exist_ok=True)
os.makedirs('./output', exist_ok=True)
st.set_page_config(layout="wide")
# Titre de l'application
st.title("AutoMashup")

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

##### BARFI
### Tracks
def feed_func(self):
    print("feed1")
    self.set_interface(name="Track", value=load_track(self._options['Track']['value']))
    print("feed12")

track_list = []

if os.path.exists('./separated/htdemucs/'):
    for index, folder_name in enumerate(os.listdir('./separated/htdemucs/')):
        folder_path = os.path.join('./struct/' + folder_name + '.json')
        if os.path.exists(folder_path):
            track_list.append(folder_name)

if track_list==[]:
    st.write("Upload some songs before using AutoMashup")
else:
    feed = Block(name="Track")
    feed.add_output("Track")
    feed.add_compute(feed_func)
    feed.add_option("Track", 'select', value=track_list[0], items=track_list),


    ### Splitter
    splitter = Block(name='Splitter')
    splitter.add_input(name='Track')
    splitter.add_output(name='Vocals')
    splitter.add_output(name='Bass')
    splitter.add_output(name='Drums')
    splitter.add_output(name='Other')

    def splitter_func(self):
        print("splitter1")
        track = self.get_interface(name='Track')
        self.set_interface(name='Vocals', value=split_track(track, 'vocals'))
        self.set_interface(name='Bass', value=split_track(track, 'bass'))
        self.set_interface(name='Drums', value=split_track(track, 'drums'))
        self.set_interface(name='Other', value=split_track(track, 'other'))
        print("splitter2")


    splitter.add_compute(splitter_func)

    ### Merger
    merger = Block(name='Mashup Technic 1')
    merger.add_output(name='Result')
    merger.add_input(name='Input 1 (Beat Structure)')
    merger.add_input(name='Input 2')
    merger.add_input(name='Input 3')
    merger.add_input(name='Input 4')

    def merger_func(self):
        print("splitter1")
        track1 = self.get_interface(name='Input 1 (Beat Structure)')
        track2 = self.get_interface(name='Input 2')
        track3 = self.get_interface(name='Input 3')
        track4 = self.get_interface(name='Input 4')
        tracks = [track1, track2, track3, track4]
        self.set_interface(name="Result", value=mashup_technic_1(tracks))
        print("splitter2")

    merger.add_compute(merger_func)

    ### Player
    def player_func(self):
        print("AAAA")
        st.write(self._name)
        track = self.get_interface(name='Track')
        mashup, sr = track[1], track[2]
        st.audio(mashup, sample_rate=sr) 
        st.divider()
        print("BBB")

    player = Block(name='Player')
    player.add_input(name='Track')
    player.add_compute(player_func)

    barfi_result = st_barfi(base_blocks=[feed, splitter, merger, player], compute_engine=True)

    if os.path.exists('./separated/htdemucs/'):
        st.title('Tracks')
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.markdown("## Song Name")
        col2.markdown("## BPM")
        col3.markdown("## Key")
        col4.markdown("## Analysis")
        st.divider()
        for index, folder_name in enumerate(os.listdir('./separated/htdemucs/')):
            folder_path = os.path.join('./struct/' + folder_name + '.json')
            if os.path.exists(folder_path):
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.write(folder_name)
                with open('./struct/' + folder_name + '.json') as f:
                    analysis = json.load(f)
                    col2.markdown(analysis['bpm'] if 'bpm' in analysis else "")
                    col3.markdown(key_from_dict(analysis["key"]) if "key" in analysis else "")
                with open('./struct/' + folder_name + '.json') as f:
                    download_button_id = f"download_button_{index}"
                    col4.download_button('Analysis', f, key = download_button_id)
                col2.write()
                remove_button_id = f"remove_button_{index}"
                if col5.button("Remove Track", key = remove_button_id):
                    remove_track(folder_name)

    st.divider()
