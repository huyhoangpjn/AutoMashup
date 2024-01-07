import streamlit as st
import os
from mashup import mashup_technic_1, mashup_technic_2
from utils import remove_track, key_finder, load_track, \
split_track, key_from_dict
import allin1
import json
from barfi import st_barfi, Block

## MASHUP METHODS
# mashup_technics = [('Mashup Technic 1', mashup_technic_1), ('Mashup Technic 2', mashup_technic_2), ('Mashup Technic 3', mashup_technic_3)]
mashup_technics = {'Simple Mashup': mashup_technic_1, 'Mashup with repitch' : mashup_technic_2}

os.makedirs('./input', exist_ok=True)
os.makedirs('./separated/htdemucs', exist_ok=True)
os.makedirs('./output', exist_ok=True)
st.set_page_config(layout="wide")

# Titre de l'application
st.title("AutoMashup")
st.markdown("### A workflow app which generates mashups")

# Upload de fichiers audio

with st.form("audio-form", clear_on_submit=True):
    audio_files = st.file_uploader("Select audio files (mp3, wav)", type=["mp3", "wav"], accept_multiple_files=True)
    submitted = st.form_submit_button("Trigger Preprocessing")

# Check if files are uploaded
if submitted and audio_files:
    for audio_file in audio_files:
        filename = audio_file.name
        with st.spinner('Preprocessing ' + filename):
            path = f"./input/{filename}"

            with open(path, "wb") as f:
                f.write(audio_file.read())
            allin1.analyze(path, out_dir='./struct', demix_dir='./separated', keep_byproducts=True)
            key_finder(path)
            audio_file = None
    st.success('Preprocessing completed !')

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
            remove_button_id = f"remove_button_{index}"
            if col5.button("Remove Track", key = remove_button_id):
                remove_track(folder_name)
                st.rerun()

st.divider()

##### BARFI
### Tracks
def feed_func(self):
    track = load_track(self._options['Track']['value'])
    with st.spinner('Loading ' + self._name):
        self.set_interface(name="Track", value=track)
        self.set_interface(name='Vocals', value=split_track(track, 'vocals'))
        self.set_interface(name='Bass', value=split_track(track, 'bass'))
        self.set_interface(name='Drums', value=split_track(track, 'drums'))
        self.set_interface(name='Other', value=split_track(track, 'other'))
track_list = []

if os.path.exists('./separated/htdemucs/'):
    for index, folder_name in enumerate(os.listdir('./separated/htdemucs/')):
        folder_path = os.path.join('./struct/' + folder_name + '.json')
        if os.path.exists(folder_path):
            track_list.append(folder_name)

if track_list==[]:
    st.markdown("## Upload some songs before using AutoMashup")
else:
    feed = Block(name="Track")
    feed.add_output("Track")
    feed.add_output(name='Vocals')
    feed.add_output(name='Bass')
    feed.add_output(name='Drums')
    feed.add_output(name='Other')
    feed.add_compute(feed_func)
    feed.add_option("Track", 'select', value=track_list[0], items=track_list)


    ### Merger
    merger = Block(name='Mixer')

    merger.add_output(name='Result')

    merger.add_input(name='Input 1 (Beat Structure)')
    merger.add_input(name='Input 2')
    merger.add_input(name='Input 3')
    merger.add_input(name='Input 4')

    merger.add_option("Method", 'select', value=next(iter(mashup_technics)), items=list(mashup_technics.keys()))

    def merger_func(self):
        with st.spinner('Computing ' + self._name):
            track1 = self.get_interface(name='Input 1 (Beat Structure)')
            track2 = self.get_interface(name='Input 2')
            track3 = self.get_interface(name='Input 3')
            track4 = self.get_interface(name='Input 4')

            if (track1 == None):
                st.markdown("### "+self._name)
                st.markdown("Input 1 must be set")
            else :
                tracks = [track1, track2, track3, track4]
                tracks = [track for track in tracks if track is not None]
                self.set_interface(name="Result", value=mashup_technics[self._options['Method']['value']](tracks))

    merger.add_compute(merger_func)

    ### Player
    def player_func(self):
        with st.spinner('Computing ' + self._name):
            track = self.get_interface(name='Track')
            if (track==None):
                st.markdown("### "+self._name)
                st.markdown("The player must have an input")
            else:
                st.markdown("### "+self._name + " : " + track["track_name"])
                mashup, sr = track["audio"], track["sr"]
                st.audio(mashup, sample_rate=sr)
                st.divider()


    player = Block(name='Player')
    player.add_input(name='Track')
    player.add_compute(player_func)

    barfi_result = st_barfi(base_blocks=[feed, merger, player], compute_engine=True)