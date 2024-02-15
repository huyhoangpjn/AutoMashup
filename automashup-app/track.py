import json
import librosa
import os
import numpy as np

from utils import note_to_frequency, calculate_semitone_shift
from segment import *

def get_path(track_name, type):
    if type == 'entire':
        if os.path.exists('./input/' + track_name + '.wav'):
            path = './input/' + track_name + '.wav'
        else :
            path = './input/' + track_name + '.mp3'

    else : 
        path = './separated/htdemucs/' + track_name + '/' + type + '.wav'
        if not os.path.exists(path):
            path = './separated/htdemucs/' + track_name + type + '.mp3'

    assert(os.path.exists(path))

    return path

def increase_array_size(arr, new_size):
    if len(arr) < new_size:
        increased_arr = np.zeros(new_size)
        increased_arr[:len(arr)] = arr
        return increased_arr
    else:
        return arr

def create_phase(self, phase_type, beat_number):
    # Function which creates a phase of a certain type and a certain duration
    if beat_number==0:
        return np.array([]), [], []
    
    labels = [segment["label"] for segment in self.segments]

    index = labels.index(phase_type)
    
    phase_beat_number, phase_beats = self.segments[index].get_beats()

    phase_downbeats = self.segments[index].get_down_beats()

    phase_beats = phase_beats - np.repeat(phase_beats[0], len(phase_beats))
    phase_downbeats = phase_downbeats - np.repeat(phase_downbeats[0], len(phase_downbeats))

    one_time_offset = phase_beats[1] 
    variable_offset = phase_beats[-1]

    phase_start = self.segments[index].start
    phase_end = self.segments[index].end

    phase = np.array(self.audio[round(phase_start*self.sr):round(phase_end*self.sr)])

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
    
# Track object
class Track:
    def __init__(self, track_name, type):
        self.name = track_name + ' - ' + type
        audio, sr = librosa.load(get_path(track_name, type))
        self.audio = audio
        self.sr = sr
        self.segments = []

        struct_path = f"./struct/{self.name}.json"
        with open(struct_path, 'r') as file:
            metadata = json.load(file)

        for key in metadata.keys():
            if key!="segments":
                self.key = metadata[key]
            else:
                for segment in metadata["segments"]:
                    segment_ = Segment(segment, self)
                    self.segments.append(segment_)


    def get_key(self):
        best_key, best_score = "", ""
        for key, score in self.key.items():
            if best_score=="" or best_score<score:
                best_key, best_score = key, score
        return best_key

    def __repitch(self, semitone_shift):
        # To be done : update key metadatas
        shifted_audio = librosa.effects.pitch_shift(self.audio, self.sr, n_steps=semitone_shift)
        
        self.audio = shifted_audio

    def pitch_track(self, target_key):
        target_frequency = note_to_frequency(target_key)
        track_frequency = note_to_frequency(self.get_key())
        self.__repitch(calculate_semitone_shift(track_frequency, target_frequency))

    def add_metronome(self):
        downbeat_sound_audio, _ = librosa.load("../metronome-sounds/block.mp3")
        otherbeat_sound_audio, _ = librosa.load("../metronome-sounds/drumstick.mp3")

        for i, beat_frame in enumerate(self.beats):
            clic_sound = downbeat_sound_audio if i % 4 == 0 else otherbeat_sound_audio
            clic = increase_array_size(clic_sound, len(self.audio[round(self.sr*beat_frame):]))
            if len(self.audio[round(self.sr*beat_frame):])>=len(clic):
                self.audio[round(self.sr*beat_frame):] += clic

    def fit_phase(self, target_track):
        list_audio = [] 
        beats = []
        downbeats = []
        phase_end = 0

        for segment in target_track.segments:
            if segment.label == "chorus":
                beat_number = segment.get_beat_number()
                phase, phase_beats, phase_downbeats = create_phase("chorus", beat_number, track)
                list_audio.append(phase)
            else : 
                beat_number = get_beat_number(segment, mother_track)
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
        
    





