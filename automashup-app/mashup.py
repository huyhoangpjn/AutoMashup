from utils import increase_array_size, load_instru, get_path, \
get_input_path, repitch, fit_phase
import librosa
import numpy as np
import math
import scipy

# tracks, the argument of mashup technics is a list of dicts looking 
# like this : 
# dict = {
#     'track_name' : String, 
#     'audio' : audio of the track, it's a np array, it can be only a part of the song (vocals, instru, ...)
#     'sr' : the sampling frequency, 
#     'metadata' : metadata of the audio 
#     }


def mashup_technic_1(tracks):
    sr = tracks[0]['sr'] # The first track is used to determine the bpm
    tempo, beat_frames = tracks[0]['metadata']["bpm"], np.array(tracks[0]['metadata']["beats"])
    mashup = np.zeros(0)
    mashup_name = ""
    for track in tracks:
        mashup_name += track['track_name'] + " "
        track_tempo, track_beat_frames = track['metadata']["bpm"], np.array(track['metadata']["beats"])
        beat_frames_aligned = track_beat_frames * (tempo / track_tempo)
        time_difference = beat_frames[0] - track_beat_frames[0]
        beat_frames = beat_frames + np.repeat(time_difference, len(beat_frames))
        separated_song = track['audio']
        instru_aligned = np.roll(separated_song, int(beat_frames_aligned[0] - beat_frames[0]))
        size = max(len(instru_aligned), len(mashup))
        mashup = np.array(mashup)
        mashup = (increase_array_size(instru_aligned, size) + increase_array_size(mashup, size))
    dict = {
    'track_name' : mashup_name, 
    'audio' : mashup,
    'sr' : sr, 
    'metadata' : tracks[0]['metadata'] # Here we consider we keep the same metadata as the first song (might not be true for the key for instance)
    }
    return dict


def mashup_technic_downbeats(tracks):
    sr = tracks[0]['sr'] # The first track is used to determine the bpm
    tempo, beat_frames = tracks[0]['metadata']["bpm"], np.array(tracks[0]['metadata']["downbeats"])
    mashup = np.zeros(0)
    mashup_name = ""
    for track in tracks:
        mashup_name += track['track_name'] + " "
        track_tempo, track_beat_frames = track['metadata']["bpm"], np.array(track['metadata']["downbeats"])
        beat_frames_aligned = track_beat_frames * (tempo / track_tempo)
        time_difference = beat_frames[0] - track_beat_frames[0]
        beat_frames = beat_frames + np.repeat(time_difference, len(beat_frames))
        separated_song = track['audio']
        instru_aligned = np.roll(separated_song, int(beat_frames_aligned[0] - beat_frames[0]))
        size = max(len(instru_aligned), len(mashup))
        mashup = np.array(mashup)
        mashup = (increase_array_size(instru_aligned, size) + increase_array_size(mashup, size))
    dict = {
    'track_name' : mashup_name, 
    'audio' : mashup,
    'sr' : sr, 
    'metadata' : tracks[0]['metadata'] # Here we consider we keep the same metadata as the first song (might not be true for the key for instance)
    }
    return dict

def mashup_technic_4(tracks):
    sr = tracks[0]['sr'] # The first track is used to determine the bpm
    tempo, beat_frames = tracks[0]['metadata']["bpm"], np.array(tracks[0]['metadata']["downbeats"])
    mashup = np.zeros(0)
    mashup_name = ""
    for track in tracks:
        mashup_name += track['track_name'] + " "
        track_tempo, track_beat_frames = track['metadata']["bpm"], np.array(track['metadata']["downbeats"])

        tempo_ratio = tempo / track_tempo
        separated_song = track['audio']
        audio_stretched = librosa.effects.time_stretch(separated_song, tempo_ratio)

        size = max(len(audio_stretched), len(mashup))
        mashup = np.array(mashup)
        mashup = (increase_array_size(audio_stretched, size) + increase_array_size(mashup, size))
    dict = {
    'track_name' : mashup_name, 
    'audio' : mashup,
    'sr' : sr, 
    'metadata' : tracks[0]['metadata'] # Here we consider we keep the same metadata as the first song (might not be true for the key for instance)
    }
    return dict

def mashup_technic_2(tracks):
    tracks = repitch(tracks)
    return mashup_technic_1(tracks)


def mashup_technic_3(tracks):
    sr = tracks[0]['sr'] # The first track is used to determine the bpm
    tempo, beat_frames = tracks[0]['metadata']["bpm"], np.array(tracks[0]['metadata']["beats"])
    segments = tracks[0]["metadata"]["segments"]
    mashup = np.zeros(0)
    mashup_name = ""
    for t in range(len(tracks-1)):
        track = fit_phase(tracks[t+1], segments)
        mashup_name += tracks[t+1]['track_name'] + " "
        track_tempo, track_beat_frames = track['metadata']["bpm"], np.array(track['metadata']["beats"])
        beat_frames_aligned = track_beat_frames * (tempo / track_tempo)
        separated_song = track['audio']
        instru_aligned = np.roll(separated_song, int(beat_frames_aligned[0] - beat_frames[0]))
        size = max(len(instru_aligned), len(mashup))
        mashup = np.array(mashup)
        mashup = (increase_array_size(instru_aligned, size) + increase_array_size(mashup, size))
        
    dict = {
    'track_name' : mashup_name, 
    'audio' : mashup,
    'sr' : sr, 
    'metadata' : tracks[0]['metadata'] # Here we consider we keep the same metadata as the first song (might not be true for the key for instance)
    }
    return dict
    # Do not modify vocals
    # Align Verse with verse
    # On each chorus of the vocals, launch the chorus of the instru
    # make the chorus long enough to fit
    # High pass transition
    # try to get second verse instru


# To update with the new argument
def mashup_technic_3(tracks):
    beat_frame_lists = []
    tempos = []
    mashup_name = ""
    for track in tracks:
        mashup_name += track['track_name'] + " "
        tempo = track["metadata"]["bpm"]
        beat_frames = track["metadata"]["downbeats"]
        tempos.append(tempo)
        beat_frame_lists.append(beat_frames)
    
    average_bpm = np.mean(tempo)

    mother_beat_frames = increase_array_size(beat_frame_lists[0] * average_bpm / tempo[0], max([len(beats for beats in beat_frame_lists)]))
    aligned_audios = []
    for i in range(len(tracks)):
        beat_frames_aligned = increase_array_size(beat_frame_lists[i] * average_bpm / tempo[i], max([len(beats for beats in beat_frame_lists)]))
        offset = int(np.mean(beat_frames_aligned - mother_beat_frames))
        aligned_audios.append(np.roll(tracks[i]["audio"], offset))

    size = max([len(aligned_audio) for aligned_audio in aligned_audios])

    aligned_audios = [increase_array_size(aligned_audio, size) for aligned_audio in aligned_audios]
   
    mashup = sum(aligned_audios)

    dict = {
    'track_name' : mashup_name, 
    'audio' : mashup,
    'sr' : tracks[0], 
    'metadata' : tracks[0]['metadata']
    }
    return dict, 

def mashup_technic_fit_phase(tracks):
    for i in range(len(tracks)-1):
        tracks[i+1] = fit_phase(tracks[i+1], tracks[0])
    return mashup_technic_downbeats(tracks)

def mashup_technic_fit_phase_repitch(tracks):
    tracks = repitch(tracks)
    return mashup_technic_downbeats(tracks)