import numpy as np
import os
import librosa 
import shutil
import json
from pymusickit.key_finder import KeyFinder
import math


def remove_track(track_name):
    struct_path = "./struct/" + track_name + ".json"
    folder_path = "./separated/htdemucs/" + track_name + "/"
    os.remove(struct_path)
    shutil.rmtree(folder_path)


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


def calculate_semitone_shift(source_freq, target_freq):
    pitch_shift = 12 * math.log2(target_freq / source_freq)
    return pitch_shift 

def repitch(tracks):
    target_key = key_from_dict(tracks[0]['metadata']['key'])
    for i in range(len(tracks)-1):
        tracks[i+1] = pitch_track(tracks[i+1], target_key)
    return tracks





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
    if beat_number==0:
        return np.array([]), [], []
    segments = track['metadata']['segments']
    sr = track['sr']
    labels = [segment["label"] for segment in segments]

    if phase_type in labels:
        index = labels.index(phase_type)
        phase_beat_number, phase_beats = get_beats(segments[index], track)
        phase_downbeats = get_down_beats(segments[index], track)
        phase_beats = phase_beats - np.repeat(phase_beats[0], len(phase_beats))
        phase_downbeats = phase_downbeats - np.repeat(phase_downbeats[0], len(phase_downbeats))

        one_time_offset = phase_beats[1] 
        variable_offset = phase_beats[-1]

        phase_start = segments[index]["start"]
        phase_end = segments[index]["end"]

        phase = np.array(track['audio'][round(phase_start*sr):round(phase_end*sr)])

        i = 1
        while phase_beat_number < beat_number:
            phase_beat_number*=2
            phase = np.concatenate((phase, phase))
            phase_beats = np.concatenate([np.array(phase_beats), phase_beats + np.repeat(variable_offset*i+one_time_offset, len(phase_beats))])
            phase_downbeats = np.concatenate([phase_downbeats, phase_downbeats + np.repeat(variable_offset*i+one_time_offset, len(phase_downbeats))])
            i*=2

        phase = phase[:round(len(phase)*(beat_number/phase_beat_number))]
        phase_beats = phase_beats.tolist()[:beat_number]
        phase_downbeat_list = []
        for phase_downbeat in phase_downbeats:
            if phase_downbeat in phase_beats:
                phase_downbeat_list.append(phase_downbeat)
        
    return phase, phase_beats, phase_downbeat_list


def fit_phase(track, mother_track):
    list_audio = [] 
    beats = [] 
    downbeats = []
    phase_end = 0
    segments = mother_track["metadata"]["segments"]

    for segment in segments:
        if segment["label"] == "chorus":
            beat_number = get_beat_number(segment, mother_track)
            phase, phase_beats, phase_downbeats = create_phase("chorus", beat_number, track)
            list_audio.append(phase)
        else : 
            beat_number= get_beat_number(segment, mother_track)
            phase, phase_beats, phase_downbeats = create_phase("verse", beat_number, track)
            list_audio.append(phase)
        phase_beats = [phase_beat + phase_end for phase_beat in phase_beats]
        phase_downbeats = [phase_downbeat + phase_end for phase_downbeat in phase_downbeats]
        beats = beats + phase_beats
        if len(beats)>1:
            phase_end = beats[-1] + beats[-1] - beats[-2]
        
        downbeats = downbeats + phase_downbeats

    audio = list_audio[0]

    for i in range(len(list_audio)-1):
        audio = np.concatenate((audio, list_audio[i+1]))

    track['audio'] = audio
    track['metadata']['beats'] = beats
    track['metadata']['downbeats'] = downbeats

    return track
