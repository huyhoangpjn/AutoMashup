import numpy as np
import copy
from utils import closest_index

# Define a Track class to represent a part of a track
# The aim of this kind of object is to keep together the audio itself,
# and the beats

class Segment:

    transition_time = 0.5 # transition time in seconds

    def __init__(self, segment_dict):
        # We create a segment from a dict coming from metadata.
        # They look like this : 
        # {
        #   "start": 0.4,
        #   "end": 22.82,
        #   "label": "verse"
        # }

        for key in segment_dict.keys():
            setattr(self, key, segment_dict[key])


    def link_track(self, track):
        # Function to link a segment to a track, must be set whenever
        # we create a segment
        # it loads all the pieces of information useful for a segment
        self.sr = track.sr
        beats = track.beats
        downbeats = track.downbeats
        
        start_beat = closest_index(self.start, beats)
        end_beat = closest_index(self.end, beats)

        self.beats = beats[start_beat:end_beat]
        
        if self.beats == []:
            self.downbeats = []
            self.audio = np.array([])
            self.left_transition = np.array([])
            self.right_transition = np.array([])

        else:
            self.beats = self.beats - np.repeat(self.beats[0], len(self.beats))

            self.downbeats = [downbeat for downbeat in downbeats if downbeat in self.beats]
            
            if self.downbeats != []:
                self.downbeats = self.downbeats - np.repeat(self.downbeats[0], len(self.downbeats))

            self.audio = track.audio[round(self.start*self.sr):round(self.end*self.sr)]

            if self.start - self.transition_time > 0 :
                self.left_transition = track.audio[round((self.start-self.transition_time)*self.sr):round(self.start*self.sr)]
            else :
                self.left_transition = track.audio[:round(self.start*self.sr)]
            if self.end + self.transition_time < len(track.audio) * self.sr:
                self.right_transition = track.audio[round(self.end*self.sr):round((self.end+self.transition_time)*self.sr)]
            else : 
                self.right_transition = track.audio[round(self.end*self.sr):]

    def concatenate(self, segment):
        # Functions to concatenate two segments, and to keep track of beats and downbeats
        # transition_length = min(len(self.right_transition), len(segment.left_transition))
        self.beats = np.concatenate([np.array(self.beats), segment.beats + np.repeat(len(self.audio)*1/self.sr,len(self.beats))])
        self.downbeats = np.concatenate([self.downbeats, segment.downbeats + np.repeat(len(self.audio)*1/self.sr,len(segment.downbeats))])
        self.audio = np.concatenate((self.audio, segment.audio))


    def get_audio_beat_fitted(self, beat_number):
        # function to fit a segment to a certain beat number
        result = copy.deepcopy(self)
        if beat_number==0:
            result.audio = np.array([])
            result.beats = []
            result.downbeats = []
        else : 
            while len(result.beats) < beat_number:
                result.concatenate(self)
            result.audio = result.audio[:round(len(result.audio)*(beat_number/len(result.beats)))]
            result.beats = result.beats.tolist()[:beat_number]
            result.downbeats = [phase_downbeat for phase_downbeat in result.downbeats if phase_downbeat<result.beats[-1]]
        return result



