def closest_index(value, value_list):
    closest_index = min(range(len(value_list)), key=lambda i: abs(value_list[i] - value))
    return closest_index

class Segment:
    def __init__(self, segment_dict, track):
        for key in segment_dict.keys():
            self.key = segment_dict[key]
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

    def get_down_beats(self):
            beats = self.track.downbeats
            start_beat = closest_index(self.start, beats)
            end_beat = closest_index(self.end, beats)
            return end_beat-start_beat, beats[start_beat:end_beat]


