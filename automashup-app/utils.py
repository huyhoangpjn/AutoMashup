import numpy as np
import os
import librosa 
import shutil
import json
from pymusickit.key_finder import KeyFinder

def increase_array_size(arr, new_size):
    """
    Increases the size of the array if its length is below the given threshold.

    :param arr: The NumPy array to increase.
    :param threshold: The minimum length required for the array.
    :param new_size: The new desired size of the array.
    :return: The array with an increased size if necessary.
    """
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
    track_name, _, sr, metadata = track
    audio, _ = librosa.load(get_path(track_name, type))
    dict = {
        'track_name' : track_name + '-' + type, 
        'audio' : audio, 
        'sr' : sr, 
        'metadata' : metadata
        }
    return dict


def key_from_dict(dict):
    best_key, best_score = "", ""
    for key, score in dict.items():
        if best_score=="" or best_score<score:
            best_key, best_score = key, score
    return best_key