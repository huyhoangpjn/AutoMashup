from utils import increase_array_size, load_instru, get_path, \
get_input_path
import librosa
import numpy as np
import essentia.standard as es
from pathlib import Path
import allin1

# tracks, the argument of mashup technics is a list of tuples looking 
# like this : 
# (song_name : String, song : np array, sr : int, metadata : dict)
# The first tuple should give the beat structure

def mashup_technic_1(tracks):
    sr = tracks[0][2]
    tempo, beat_frames = tracks[0][3]["bpm"], np.array(tracks[0][3]["beats"])
    mashup = np.zeros(0)
    mashup_name = ""
    for track in tracks:
        mashup_name += track[0] + " "
        track_tempo, track_beat_frames = track[3]["bpm"], np.array(track[3]["beats"])
        beat_frames_aligned = track_beat_frames * (tempo / track_tempo)
        separated_song = track[1]
        instru_aligned = np.roll(separated_song, int(beat_frames_aligned[0] - beat_frames[0]))
        size = max(len(instru_aligned), len(mashup))
        mashup = np.array(mashup)
        mashup = (increase_array_size(instru_aligned, size) + increase_array_size(mashup, size))
    return (mashup_name, mashup, sr, tracks[0][3])

# To update with the new argument
def mashup_technic_2(tracks):
    vocals_path = './separated/mdx_extra/' + vocals + '/vocals.mp3'
    vocals_song_path = './input/' + vocals
    vocals_song_path += '.mp3' if Path(vocals_song_path+'.mp3').is_file() else '.wav'
        
    instru_path = './separated/mdx_extra/' + instru + '/no_vocals.mp3'
    instru_song_path = './input/' + instru 
    instru_song_path += '.mp3' if Path(instru_song_path+'.mp3').is_file() else '.wav'

    vocals, sr1 = librosa.load(vocals_path)
    instru, sr2   = librosa.load(instru_path)
    
    # Analyze songs (This model include the source separation by demucs --> need to be optimized later)
    results = allin1.analyze([vocals_song_path, instru_song_path])
    
    tempo1, beat_frames1 = results[0].bpm, librosa.time_to_frames(results[0].beats, sr=sr1)
    tempo2, beat_frames2 = results[1].bpm, librosa.time_to_frames(results[1].beats, sr=sr2)
    
    average_bpm = np.mean([tempo1, tempo2])

    tempo_ratio1 = average_bpm / tempo1
    tempo_ratio2 = average_bpm / tempo2

    beat_frames1_aligned = increase_array_size(beat_frames1 * tempo_ratio1, max(len(beat_frames2), len(beat_frames1)))
    beat_frames2_aligned = increase_array_size(beat_frames2 * tempo_ratio2, max(len(beat_frames2), len(beat_frames1)))

    offset = int(np.mean(beat_frames2_aligned - beat_frames1_aligned))
    
    instru_aligned = np.roll(instru, offset)

    size = max(len(instru_aligned), len(vocals))
    instru_aligned = increase_array_size(instru_aligned, size)
    vocals = increase_array_size(vocals, size)

    mashup = instru_aligned + vocals

    return mashup, sr1