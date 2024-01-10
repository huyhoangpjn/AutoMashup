from utils import increase_array_size, load_instru, get_path, \
get_input_path, repitch
import librosa
import numpy as np
import math

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

def mashup_technic_2(tracks):
    tracks = repitch(tracks)
    return mashup_technic_1(tracks)

"""
def get_beat_number(segment, track):
    beats = track["metadata"]["beats"]
    beat_number = beats.find(segment["end"])-beats.find(segment["start"])
    return beat_number


def smooth_transition(audio1, audio2):
    y1, sr1 = librosa.load(song1_path, sr=sampling_rate)
    y2, sr2 = librosa.load(song2_path, sr=sampling_rate)
    min_len = min(len(y1), len(y2))
    y1 = y1[:min_len]
    y2 = y2[:min_len]
    fade_in = np.linspace(0.0, 1.0, int(fade_duration * sampling_rate), endpoint=False)
    fade_out = np.linspace(1.0, 0.0, int(fade_duration * sampling_rate), endpoint=False)
    y1[:len(fade_in)] *= fade_in
    y1[-len(fade_out):] *= fade_out
    y2[:len(fade_in)] *= 1 - fade_in
    y2[-len(fade_out):] *= 1 - fade_out
    cutoff_frequency = 500.0  # Fréquence de coupure du filtre passe-haut en Hz
    filter_order = 4
    sos = scipy.signal.butter(filter_order, cutoff_frequency, btype='high', fs=sampling_rate, output='sos')
    # Appliquer le filtre passe-haut à la deuxième chanson
    y2_highpass = scipy.signal.sosfilt(sos, y2)
    transition_signal = y1 + y2_highpass
    librosa.output.write_wav(output_path, transition_signal, sr=sampling_rate)


def fit_phase(track, segments, mother_track):
    original_audio = track["audio"]
    original_segments = track["metadata"]["segments"]
    original_beats = track["metadata"]["beats"]
    list_audio = []    
    for segment in segments:
        if segment["label"] == "chorus":
            beat_number = get_beat_number(segment, mother_track)
            phase = create_phase("chorus", beat_number, track)
            
        else : 


    return track


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
    vocals_path = './separated/mdx_extra/' + vocals + '/vocals.mp3'
    vocals_song_path = './input/' + vocals
    vocals_song_path += '.mp3' if Path(vocals_song_path+'.mp3').is_file() else '.wav'
        
    instru_path = './separated/mdx_extra/' + instru + '/no_vocals.mp3'
    instru_song_path = './input/' + instru 
    instru_song_path += '.mp3' if Path(instru_song_path+'.mp3').is_file() else '.wav'

    vocals, sr1 = librosa.load(vocals_path)
    instru, sr2   = librosa.load(instru_path)
    
    # Analyze songs (This model include the source separation by demucs --> need to be optimized later)
    # results = allin1.analyze([vocals_song_path, instru_song_path])
    # The analysis can be removed, because we already have the metadatas
    
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

    return mashup, sr1"""