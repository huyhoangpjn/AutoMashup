import numpy as np

def closest_index(value, value_list):
    closest_index = min(range(len(value_list)), key=lambda i: abs(value_list[i] - value))
    return closest_index



class Segment:
    def __init__(self, segment_dict):
        for key in segment_dict.keys():
            setattr(self, key, segment_dict[key])

    def link_track(self, track):
        self.track = track

    def get_beat_number(self):
        start_beat = closest_index(self.start, self.track.beats)
        end_beat = closest_index(self.end, self.track.beats)
        return end_beat-start_beat
    

    def get_length_seconds(self):
        return self.end - self.start
    

    def get_beats(self):
        beats = self.track.beats
        start_beat = closest_index(self.start, beats)
        end_beat = closest_index(self.end, beats)
        return end_beat-start_beat, beats[start_beat:end_beat]
    

    def get_beats_no_offset(self):
        beat_number, beats = self.get_beats()
        beats = beats - np.repeat(beats[0], len(beats))
        return beat_number, beats


    def get_downbeats(self):
        beats = self.track.downbeats
        start_beat = closest_index(self.start, beats)
        end_beat = closest_index(self.end, beats)
        return end_beat-start_beat, beats[start_beat:end_beat]
    

    def get_downbeats_no_offset(self):
        beat_number, beats = self.get_downbeats()
        beats = beats - np.repeat(beats[0], len(beats))
        return beat_number, beats


    def get_audio(self):
         return self.track.audio[round(self.start*self.track.sr):round(self.end*self.track.sr)]
    
    def get_audio_margin(self, margin):
        if self.start-margin>0 and round((self.end+margin)*self.track.sr)<len(self.track.audio):
            return self.track.audio[round((self.start-margin)*self.track.sr):round((self.end+margin)*self.track.sr)], margin
        else:
            return self.get_audio(), 0
    
    def get_audio_beat_fitted(self, beat_number, fade_duration = 0):
        if beat_number==0:
            return np.array([]), [], []
        phase, margin = self.get_audio_margin(fade_duration)

        segment_beat_number, segment_beats = self.get_beats_no_offset()

        phase_beat_number, phase_beats = segment_beat_number, segment_beats

        _, segment_downbeats = self.get_downbeats_no_offset()

        phase_downbeats = segment_downbeats[margin*self.track.sr:]

        while phase_beat_number < beat_number:
            phase_beat_number += segment_beat_number
            phase_beats = np.concatenate([np.array(phase_beats), segment_beats + np.repeat(len(phase)*1/self.track.sr,len(segment_beats))])
            phase_downbeats = np.concatenate([phase_downbeats, segment_downbeats + np.repeat(len(phase)*1/self.track.sr,len(segment_downbeats))])

            phase = np.concatenate((phase, self.get_audio()))
            # phase = cross_fade(phase, self.get_audio_margin(fade_duration))

        phase = phase[:round(len(phase)*(beat_number/phase_beat_number))]
        phase_beats = phase_beats.tolist()[:beat_number]
        
        phase_downbeats = [phase_downbeat for phase_downbeat in phase_downbeats if phase_downbeat<phase_beats[-1]]
        return phase, phase_beats, phase_downbeats



