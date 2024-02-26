from utils import increase_array_size
import librosa
import numpy as np

# Mashup Technics
# In this file, you may add mashup technics
# the input of such a method is a list of up to 4 objects of type Track. 
# You can modify them without making any copy, it's already done before.
# You may find useful methods in the track.py file
# Be sure to return a Track object

def mashup_technic(tracks):
    # Mashup technic with first downbeat alignment and bpm sync
    sr = tracks[0].sr # The first track is used to determine the target bpm
    tempo = tracks[0].bpm
    beginning_instant = tracks[0].downbeats[0] # downbeats metadata
    beginning = beginning_instant * sr
    mashup = np.zeros(0)
    mashup_name = ""

    # we add each track to the mashup
    for track in tracks:
        mashup_name += track.name + " " # name
        track_tempo = track.bpm
        track_beginning_temporal = track.downbeats[0]
        track_sr = track.sr
        track_beginning = track_beginning_temporal * track_sr
        track_audio = track.audio

        # reset first downbeat position
        track_audio_no_offset = np.array(track_audio)[round(track_beginning):] 

        # multiply by bpm rate
        track_audio_accelerated = librosa.effects.time_stretch(track_audio_no_offset, rate = tempo / track_tempo)

        # add the right number of zeros to align with the main track
        final_track_audio = np.concatenate((np.zeros(round(beginning)), track_audio_accelerated)) 

        size = max(len(mashup), len(final_track_audio))
        mashup = np.array(mashup)
        mashup = (increase_array_size(final_track_audio, size) + increase_array_size(mashup, size))

    # we return a modified version of the first track
    # doing so, we keep its metadata
    tracks[0].audio = mashup

    return tracks[0]


def mashup_technic_repitch(tracks):
    # mashup technic which repiches every track to the first one
    key = tracks[0].get_key() # target key
    for i in range(len(tracks)-1):
        tracks[i+1].pitch_track(key) # repitch
    
    # standard mashup method
    return mashup_technic(tracks)


def mashup_technic_fit_phase(tracks):
    # mashup technic with phase alignment (i.e. chorus with chorus, verse with verse...)
    # each track's structure is aligned with the first one's
    for i in range(len(tracks)-1):
        tracks[i+1].fit_phase(tracks[0]) 

    # standard mashup method
    return mashup_technic(tracks)


def mashup_technic_fit_phase_repitch(tracks):
    # mashup technic with phase alignment and repitch
    # repitch
    key = tracks[0].get_key()
    for i in range(len(tracks)-1):
        tracks[i+1].pitch_track(key)

    # phase fit mashup
    return mashup_technic_fit_phase(tracks)