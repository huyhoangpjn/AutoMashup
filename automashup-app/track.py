import json
import librosa
import numpy as np
import copy

from utils import note_to_frequency, calculate_pitch_shift, get_path,\
      increase_array_size
from segment import *


# Track object
class Track:
    def __init__(self, track_name, audio, metadata, sr):
        self.name = track_name
        self.audio = audio
        self.sr = sr
        self.segments = []
        for key in metadata.keys():
            if key!="segments":
                setattr(self, key, metadata[key])
            else:
                for segment in metadata["segments"]:
                    if isinstance(segment, Segment):
                        segment_ = segment
                    else:
                        segment_ = Segment(segment)
                    segment_.link_track(self)
                    self.segments.append(segment_)


    def track_from_song(track_name, type):
        name = track_name + ' - ' + type
        audio, sr = librosa.load(get_path(track_name, type), sr=44100)
        struct_path = f"./struct/{track_name}.json"
        with open(struct_path, 'r') as file:
            metadata = json.load(file)
        return Track(name, audio, metadata, sr)


    def mashup_track(metadata_track, audio):
        track = copy.deepcopy(metadata_track)
        track.audio = audio
        return track

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
        self.__repitch(calculate_pitch_shift(track_frequency, target_frequency))


    def add_metronome(self):
        downbeat_sound_audio, _ = librosa.load("../metronome-sounds/block.mp3")
        otherbeat_sound_audio, _ = librosa.load("../metronome-sounds/drumstick.mp3")
        for i, beat_frame in enumerate(self.beats):
            clic_sound = downbeat_sound_audio if i % 4 == 0 else otherbeat_sound_audio
            clic = increase_array_size(clic_sound, len(self.audio[round(self.sr*beat_frame):]))
            if len(self.audio[round(self.sr*beat_frame):])>=len(clic):
                self.audio[round(self.sr*beat_frame):] += clic


    def fit_phase(self, target_track):
        audio = np.array([])
        beats = [0]
        downbeats = [0]
        for target_segment in target_track.segments:
            i = 0
            segment = self.segments[i]
            while i<len(self.segments)-1 and (segment.label!=target_segment.label or segment.get_beat_number()==0):
                i+=1
                segment = self.segments[i]
            if not (segment.label==target_segment.label and segment.get_beat_number()>0):
                audio = np.concatenate([audio, np.zeros(int(target_segment.get_beat_number() / (self.bpm/60) * self.sr))])
                beats = beats + [beats[-1] + (i+1)/(self.bpm/60) for i in range(target_segment.get_beat_number())]
                downbeats = downbeats + [downbeats[-1] + (4*i+1)/(self.bpm/60) for i in range(target_segment.get_beat_number()//4)]
            else: 
                phase, phase_beats, phase_downbeats = segment.get_audio_beat_fitted(target_segment.get_beat_number())
                audio = np.concatenate([audio, phase])
                beats = beats + [beats[-1] + phase_beat for phase_beat in phase_beats]
                downbeats = downbeats + [downbeats[-1] + phase_downbeat for phase_downbeat in phase_downbeats]
        beats = beats[1:]
        downbeats = downbeats[1:]
        self.audio = audio
        self.beats = beats
        self.downbeats = downbeats
        
    





