import numpy as np
import os
import librosa 
import shutil
import json
from pymusickit.key_finder import KeyFinder
import math

def increase_array_size(arr, new_size):
    if len(arr) < new_size:
        # Create a new array with the new size
        increased_arr = np.zeros(new_size)

        # Copy elements from the original array to the new array
        increased_arr[:len(arr)] = arr

        return increased_arr
    else:
        return arr
    

def adjust_bpm(bpm):
    while bpm < 80 or bpm > 160:
        if bpm < 80:
            bpm *= 2
        elif bpm > 160:
            bpm /= 2
    return bpm


def get_path(track_name, type):
    path = './separated/htdemucs/' + track_name + '/' + type + '.wav'
    if not os.path.exists(path):
        path = './separated/htdemucs/' + track_name + type + '.mp3'
    assert(os.path.exists(path))
    return path


def get_input_path(track_name):
    if os.path.exists('./input/' + track_name + '.wav'):
        input_path = './input/' + track_name + '.wav'
    else :
        input_path = './input/' + track_name + '.mp3'
    
    assert(os.path.exists(input_path))
    return input_path


def load_instru(bass, drums, other):
    bass_path = './separated/htdemucs/' + bass + '/bass.wav'
    drums_path = './separated/htdemucs/' + drums + '/drums.wav'
    other_path = './separated/htdemucs/' + other + '/other.wav'
    paths = [bass_path, drums_path, other_path]
    tracks = []
    for path in paths:
        if os.path.exists(path):
            tracks.append(librosa.load(path))
    sr = max(freq for _, freq in tracks)
    for i in range(len(tracks)):
        tracks[i] = (librosa.resample(tracks[i][0], orig_sr=tracks[i][1], target_sr=sr), sr)
    return (np.vstack([track[0] for track in tracks]), sr)


def remove_track(track_name):
    struct_path = "./struct/" + track_name + ".json"
    folder_path = "./separated/htdemucs/" + track_name + "/"
    os.remove(struct_path)
    shutil.rmtree(folder_path)


def extract_filename(file_path):
    filename = os.path.basename(file_path)
    filename_without_extension, _ = os.path.splitext(filename)
    return filename_without_extension


def key_finder(path): 
    filename = extract_filename(path)
    struct_path = f"./struct/{filename}.json"
    with open(struct_path, 'r') as file:
        data = json.load(file)
        data['key'] = KeyFinder(path).key_dict
    with open(struct_path, 'w') as file:
        json.dump(data, file, indent=2)


def load_track(track_name):
    audio, sr = librosa.load(get_input_path(track_name))
    struct_path = f"./struct/{track_name}.json"
    with open(struct_path, 'r') as file:
        metadata = json.load(file)
    dict = {
        'track_name' : track_name, 
        'audio' : audio, 
        'sr' : sr, 
        'metadata' : metadata
        }
    return dict


def split_track(track, type):
    track_name = track["track_name"]
    sr = track["sr"]
    metadata = track["metadata"]
    audio, _ = librosa.load(get_path(track_name, type))
    dict = {
        'track_name' : track_name + '-' + type, 
        'audio' : audio, 
        'sr' : sr, 
        'metadata' : metadata
        }
    return dict


def note_to_frequency(key):
    note, mode = key.split(' ', 1)
    reference_frequency=440.0
    semitone_offsets = {'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'D#': -6, 'Eb': -6, 'E': -5, 'Fb': -5, 'E#': -4,
                        'F': -4, 'F#': -3, 'Gb': -3, 'G': -2, 'G#': -1, 'Ab': -1, 'A': 0, 'A#': 1, 'Bb': 1, 'B': 2, 'Cb': 2, 'B#': 3}
    semitone_offset = semitone_offsets[note]
    if mode == 'minor':
        semitone_offset -= 3 
    frequency = reference_frequency * 2 ** (semitone_offset / 12)
    return frequency


def calculate_pitch_shift(source_freq, target_freq):
    pitch_shift = 12 * math.log2(target_freq / source_freq)
    return pitch_shift


def key_from_dict(dict):
    best_key, best_score = "", ""
    for key, score in dict.items():
        if best_score=="" or best_score<score:
            best_key, best_score = key, score
    return best_key


def repitch_audio(track, semitone_shift):
    audio, sr = track['audio'], track['sr']
    shifted_audio = librosa.effects.pitch_shift(audio, sr, n_steps=semitone_shift)
    track['audio'] = shifted_audio
    # To be done : update key metadatas
    return track


def pitch_track(track, target_key):
    track_key = key_from_dict(track['metadata']['key'])
    target_frequency = note_to_frequency(target_key)
    track_frequency = note_to_frequency(track_key)
    shifted_track = repitch_audio(track, calculate_pitch_shift(track_frequency, target_frequency))
    return shifted_track
    
def repitch(tracks):
    target_key = key_from_dict(tracks[0]['metadata']['key'])
    for i in range(len(tracks)-1):
        tracks[i+1] = pitch_track(tracks[i+1], target_key)
    return tracks


def closest_index(value, value_list):
    closest_index = min(range(len(value_list)), key=lambda i: abs(value_list[i] - value))
    return closest_index

def get_beats(segment, track):
    beats = track["metadata"]["beats"]

    start_beat = closest_index(segment["start"], beats)
    end_beat = closest_index(segment["end"], beats)

    beat_number = end_beat-start_beat
    return beat_number, beats[start_beat:end_beat]

def get_down_beats(segment, track):
    downbeats = track["metadata"]["downbeats"]

    start_beat = closest_index(segment["start"], downbeats)
    end_beat = closest_index(segment["end"], downbeats)

    beat_number = end_beat-start_beat
    return downbeats[start_beat:end_beat]

def get_beat_number(segment, track):
    beats = track["metadata"]["beats"]
    start_beat = closest_index(segment["start"], beats)
    end_beat = closest_index(segment["end"], beats)
    beat_number = end_beat-start_beat
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

def create_phase(phase_type, beat_number, track):
    segments = track['metadata']['segments']
    sr = track['sr']
    labels = [segment["label"] for segment in segments]
    if phase_type in labels:
        index = labels.index(phase_type)
        phase_beat_number, phase_beats = get_beats(segments[index], track)
        phase_downbeats = get_down_beats(segments[index], track)

        phase_beats = phase_beats - np.repeat(phase_beats[0], len(phase_beats))
        phase_downbeats = phase_downbeats - np.repeat(phase_downbeats[0], len(phase_downbeats))

        phase_start = segments[index]["start"]

        phase_end = segments[index]["end"]

        phase = np.array(track['audio'][round(phase_start*sr):round(phase_end*sr)])

        while phase_beat_number < beat_number:

            phase_beat_number*=2

            phase = np.concatenate((phase, phase))
             
            phase_beats = np.concatenate([np.array(phase_beats), phase_beats + np.repeat(phase_end, len(phase_beats))])

            phase_downbeats = np.concatenate([phase_downbeats, phase_downbeats + np.repeat(phase_end, len(phase_downbeats))])

        phase = phase[:round(len(phase)*(beat_number/phase_beat_number))]
    return phase, phase_beats.tolist(), phase_downbeats.tolist(), phase_end



def fit_phase(track, mother_track):
    list_audio = [] 
    beats = [] 
    downbeats = []
    phase_end = 0
    segments = mother_track["metadata"]["segments"]

    for segment in segments:
        if segment["label"] == "chorus":
            beat_number = get_beat_number(segment, mother_track)
            phase, phase_beats, phase_downbeats, new_phase_end = create_phase("chorus", beat_number, track)
            list_audio.append(phase)

        else : 
            beat_number= get_beat_number(segment, mother_track)
            phase, phase_beats, phase_downbeats, new_phase_end = create_phase("verse", beat_number, track)
            list_audio.append(phase)
        
        phase_beats = [phase_beat + phase_end for phase_beat in phase_beats]
        phase_downbeats = [phase_downbeats + phase_end for phase_downbeats in phase_beats]

        phase_end = new_phase_end
        beats = beats + phase_beats
        downbeats = downbeats + phase_downbeats

    audio = list_audio[0]

    for i in range(len(list_audio)-1):
        audio = np.concatenate((audio, list_audio[i+1]))

    track['audio'] = audio
    track['metadata']['beats'] = beats
    track['metadata']['downbeats'] = downbeats

    return track


def add_metronome(track):
    sr = track['sr']
    downbeat_sound_audio, _ = librosa.load("../metronome-sounds/block.mp3")
    otherbeat_sound_audio, _ = librosa.load("../metronome-sounds/drumstick.mp3")
    beat_frames = track["metadata"]["beats"]
    track_audio = track['audio']
    for i, beat_frame in enumerate(beat_frames):
        print(beat_frame)
        track_audio[round(sr*beat_frame):] += increase_array_size(downbeat_sound_audio if i % 4 == 0 else otherbeat_sound_audio, len(track_audio[round(sr*beat_frame):]))
    track['audio'] = track_audio
    return track