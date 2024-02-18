from utils import increase_array_size
import librosa
import numpy as np
from track import Track

def mashup_technic(tracks):
    sr = tracks[0].sr # The first track is used to determine the bpm
    tempo= tracks[0].bpm
    beginning_temporal = tracks[0].downbeats[0]
    beginning = beginning_temporal * sr
    mashup = np.zeros(0)
    mashup_name = ""
    for track in tracks:
        mashup_name += track.name + " "
        track_tempo = track.bpm
        track_beginning_temporal = track.downbeats[0]
        track_sr = track.sr
        track_beginning = track_beginning_temporal * track_sr
        track_audio = track.audio
        track_audio_no_offset = np.array(track_audio)[round(track_beginning):]
        track_audio_accelerated = librosa.effects.time_stretch(track_audio_no_offset, tempo / track_tempo)
        final_track_audio = np.concatenate((np.zeros(round(beginning)), track_audio_accelerated)) 
        size = max(len(mashup), len(final_track_audio))
        mashup = np.array(mashup)
        mashup = (increase_array_size(final_track_audio, size) + increase_array_size(mashup, size))
    return Track.mashup_track(tracks[0], mashup)

def mashup_technic_fit_phase(tracks):
    for i in range(len(tracks)-1):
        tracks[i+1].fit_phase(tracks[0])
    return mashup_technic(tracks)


def mashup_technic_fit_phase_repitch(tracks):
    key = tracks[0].get_key()
    for i in range(len(tracks)-1):
        tracks[i+1].pitch_track(key)
    return mashup_technic_fit_phase(tracks)