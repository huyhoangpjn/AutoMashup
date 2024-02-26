import numpy as np
import os
import shutil
import math
import json
from pymusickit.key_finder import KeyFinder

### Here are some useful functions used in other parts of the project


def increase_array_size(arr, new_size):
    if len(arr) < new_size:
        # Create a new array with the new size
        increased_arr = np.zeros(new_size)
        # Copy elements from the original array to the new array
        increased_arr[:len(arr)] = arr
        return increased_arr
    else:
        return arr


def get_path(track_name, type):
    # returns the path of a song
    # It can return the whole track or just a separated part of it,
    # depending on the type, which should be one of the following : 
    # 'entire', 'bass', 'drums', 'vocals', 'other'   
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


def remove_track(track_name):
    # function to remove a track and all the files that concern it.
    struct_path = "./struct/" + track_name + ".json"
    folder_path = "./separated/htdemucs/" + track_name + "/"
    os.remove(struct_path)
    shutil.rmtree(folder_path)


def extract_filename(file_path):
    # Extract filename from a given path
    filename = os.path.basename(file_path)
    filename_without_extension, _ = os.path.splitext(filename)
    return filename_without_extension


def note_to_frequency(key):
    # turn a note with a mode to a frequency
    note, mode = key.split(' ', 1)
    reference_frequency=440.0
    semitone_offsets = {'C': -9, 'C#': -8, 'Db': -8, 'D': -7, 'D#': -6, 'Eb': -6, 'E': -5, 'Fb': -5, 'E#': -4,
                        'F': -4, 'F#': -3, 'Gb': -3, 'G': -2, 'G#': -1, 'Ab': -1, 'A': 0, 'A#': 1, 'Bb': 1, 'B': 2, 'Cb': 2, 'B#': 3}
    semitone_offset = semitone_offsets[note]
    if mode == 'minor':
        semitone_offset -= 3 
    frequency = reference_frequency * 2 ** (semitone_offset / 12)
    return frequency


def key_finder(path): 
    filename = extract_filename(path)
    struct_path = f"./struct/{filename}.json"
    with open(struct_path, 'r') as file:
        data = json.load(file)
        data['key'] = KeyFinder(path).key_dict
    with open(struct_path, 'w') as file:
        json.dump(data, file, indent=2)


def calculate_pitch_shift(source_freq, target_freq):
    pitch_shift = 12 * math.log2(target_freq / source_freq)
    return pitch_shift


def key_from_dict(dict):
    # get key from the metadata correlation list
    best_key, best_score = "", ""
    for key, score in dict.items():
        if best_score=="" or best_score<score:
            best_key, best_score = key, score
    return best_key


def closest_index(value, value_list):
    # get the index of the closest value of a specific target in a list
    closest_index = min(range(len(value_list)), key=lambda i: abs(value_list[i] - value))
    return closest_index
