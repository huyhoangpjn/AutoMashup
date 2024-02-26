import streamlit as st
import os
import allin1
import json
import copy
from barfi import st_barfi, Block

from track import Track
from mashup import mashup_technic_fit_phase, \
mashup_technic_fit_phase_repitch, mashup_technic
from utils import remove_track, key_from_dict


## MASHUP METHODS
mashup_technics = \
{
    'Mashup technic' : mashup_technic,
    'Mashup with phase fit' : mashup_technic_fit_phase, 
    'Mashup with phase fit and repitch': mashup_technic_fit_phase_repitch,
}

# Check if we have the necessary existing directories
os.makedirs('./input', exist_ok=True)
os.makedirs('./separated/htdemucs', exist_ok=True)
os.makedirs('./output', exist_ok=True)
st.set_page_config(layout="wide")


# Application title
st.title("AutoMashup")
st.markdown("### A workflow app which generates mashups")


# Audio files upload
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
            
            #trigger analyze
            allin1.analyze(path, out_dir='./struct', demix_dir='./separated', keep_byproducts=True)

            audio_file = None

    st.success('Preprocessing completed !')


# Song list
if os.path.exists('./separated/htdemucs/'):
    st.title('Tracks')

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.markdown("## Song Name")
    col2.markdown("## BPM")
    col3.markdown("## Key")
    col4.markdown("## Analysis")

    st.divider()

    # for each song, we show some information
    for index, folder_name in enumerate(os.listdir('./separated/htdemucs/')):

        # we get the file resulting of allin1 analysis
        struct_path = os.path.join('./struct/' + folder_name + '.json')
        if os.path.exists(struct_path):
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.write(folder_name)

            # then we display some data
            with open('./struct/' + folder_name + '.json') as f:
                analysis = json.load(f)
                col2.markdown(analysis['bpm'] if 'bpm' in analysis else "")
                col3.markdown(key_from_dict(analysis["key"]) if "key" in analysis else "")
                download_button_id = f"download_button_{index}"
                col4.download_button('Analysis', f, key = download_button_id)

            remove_button_id = f"remove_button_{index}"
            if col5.button("Remove Track", key = remove_button_id):
                remove_track(folder_name)
                st.rerun()

st.divider()


track_list = []

if os.path.exists('./separated/htdemucs/'):
    for index, folder_name in enumerate(os.listdir('./separated/htdemucs/')):
        folder_path = os.path.join('./struct/' + folder_name + '.json')
        if os.path.exists(folder_path):
            track_list.append(folder_name)

if track_list==[]:
    st.markdown("## Upload some songs before using AutoMashup")

else:
    ##### BARFI

    # Now we'll be defining the different blocks of our workflow
    # Each block will be linked to a compute function which will take 
    # effect when we execute the workflow

    ### Feeder
    # The feeder is the block which enables to select a song as input
    # It enables to select a song from the ones we already processed 
    # It gives 5 outputs of type Track, corresponding to the separated
    # or entire versions of the selected song

    feed = Block(name="Track")

    # Interfaces
    feed.add_output("Track")
    feed.add_output(name='Vocals')
    feed.add_output(name='Bass')
    feed.add_output(name='Drums')
    feed.add_output(name='Other')

    def feed_func(self):
        track_name = self._options['Track']['value']
        # spinner to view loading
        with st.spinner('Loading ' + self._name):
            # a feeder will display all the different tracks of a song 
            # (already separated by allin1)
            # Outputs
            self.set_interface(name="Track", value=Track.track_from_song(track_name, 'entire'))
            self.set_interface(name='Vocals', value=Track.track_from_song(track_name, 'vocals'))
            self.set_interface(name='Bass', value=Track.track_from_song(track_name, 'bass'))
            self.set_interface(name='Drums', value=Track.track_from_song(track_name, 'drums'))
            self.set_interface(name='Other', value=Track.track_from_song(track_name, 'other'))

    feed.add_compute(feed_func)

    # option for choosing the song
    feed.add_option("Track", 'select', value=track_list[0], items=track_list)

    ### Merger
    # The merger block is made to combine up to 4 tracks and to 
    # produce another one

    merger = Block(name='Mixer')

    # Interfaces
    merger.add_output(name='Result')
    merger.add_input(name='Input 1 (Beat Structure)')
    merger.add_input(name='Input 2')
    merger.add_input(name='Input 3')
    merger.add_input(name='Input 4')

    # We add an option to be able to select a mashup method
    merger.add_option("Method", 'select', value=next(iter(mashup_technics)), items=list(mashup_technics.keys()))

    def merger_func(self):
        # spinner to view loading
        with st.spinner('Computing ' + self._name):
            # we make a copy of each input because the objects may
            # be modified during the mashups
            track1 = copy.deepcopy(self.get_interface(name='Input 1 (Beat Structure)'))
            track2 = copy.deepcopy(self.get_interface(name='Input 2'))
            track3 = copy.deepcopy(self.get_interface(name='Input 3'))
            track4 = copy.deepcopy(self.get_interface(name='Input 4'))

            if (track1 == None):
                # track1 will be used as our base, it must be set
                st.markdown("### "+self._name)
                st.markdown("Input 1 must be set")
            else :
                tracks = [track1, track2, track3, track4]
                tracks = [track for track in tracks if track is not None]

                # we apply the mashup technic
                self.set_interface(name="Result", value=mashup_technics[self._options['Method']['value']](tracks))

    merger.add_compute(merger_func)

    ### Player
    # The player bloc is the bloc which creates a player to listen to 
    # tracks
    # We'll also put a metronome option to be able to hear the beats
    # according to the metadata of the selected track

    player = Block(name='Player')
    player.add_input(name='Track')
    player.add_option("Metronome", "checkbox")

    def player_func(self):
        # view loading
        with st.spinner('Computing ' + self._name):
            # again we do a copy, because the metronome will modify
            # the audio
            track = copy.deepcopy(self.get_interface(name='Track'))

            if (track==None):
                st.markdown("### "+self._name)
                st.markdown("The player must have an input")
            else:
                # metronome
                if self._options['Metronome']['value']:
                    track.add_metronome()

                st.markdown("### "+self._name + " : " + track.name)
                mashup, sr = track.audio, track.sr
                st.audio(mashup, sample_rate=sr)
            st.divider()

    player.add_compute(player_func)

    # Trigger Barfi, add all the blocks
    barfi_result = st_barfi(base_blocks=[feed, merger, player], compute_engine=True)