from utils import increase_array_size
import librosa
import numpy as np
import essentia.standard as es
from pathlib import Path
import allin1

def mashup_technic_1(vocals, instru):
    vocals_path = './separated/mdx_extra/' + vocals + '/vocals.mp3'
    vocals_song_path = './input/' + vocals + '.mp3'
    
    instru_path = './separated/mdx_extra/' + instru + '/no_vocals.mp3'
    instru_song_path = './input/' + instru + '.mp3'

    song1, sr1 = librosa.load(vocals_song_path)
    vocals, sr1 = librosa.load(vocals_path)

    song2, sr2 = librosa.load(instru_song_path)
    instru, sr2 = librosa.load(instru_path)

    tempo1, beat_frames1 = librosa.beat.beat_track(y=song1, sr=sr1)
    tempo2, beat_frames2 = librosa.beat.beat_track(y=song2, sr=sr2)

    beat_frames2_aligned = beat_frames2 * (tempo1 / tempo2)

    instru_aligned = np.roll(instru, int(beat_frames2_aligned[0] - beat_frames1[0]))

    size = max(len(instru_aligned), len(vocals))
    return (increase_array_size(instru_aligned, size) + increase_array_size(vocals, size), sr1)

def mashup_technic_2(vocals, instru):
    vocals_path = './separated/mdx_extra/' + vocals + '/vocals.mp3'
    vocals_song_path = './input/' + vocals + '.mp3'
    
    instru_path = './separated/mdx_extra/' + instru + '/no_vocals.mp3'
    instru_song_path = './input/' + instru + '.mp3'

    song1, sr1 = librosa.load(vocals_song_path)
    vocals, sr1 = librosa.load(vocals_path)

    song2, sr2 = librosa.load(instru_song_path)
    instru, sr2 = librosa.load(instru_path)

    # Extraction des tempos et des cadences de battement
    tempo1, beat_frames1 = librosa.beat.beat_track(y=song1, sr=sr1)
    tempo2, beat_frames2 = librosa.beat.beat_track(y=song2, sr=sr2)

    audio1 = es.MonoLoader(filename=vocals_song_path)()
    rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
    bpm, beat_frames1, beats_confidence, _, beats_intervals = rhythm_extractor(audio1)

    audio2 = es.MonoLoader(filename=instru_song_path)()
    rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
    bpm, beat_frames2, beats_confidence, _, beats_intervals = rhythm_extractor(audio2)
    
    # Calcul du BPM moyen
    average_bpm = np.mean([tempo1, tempo2])

    # Ajustement des tempos pour maintenir un changement constant en BPM
    tempo_ratio1 = average_bpm / tempo1
    tempo_ratio2 = average_bpm / tempo2

    # Ajustement des cadences de battement
    beat_frames1_aligned = increase_array_size(beat_frames1 * tempo_ratio1, len(beat_frames2))
    beat_frames2_aligned = beat_frames2 * tempo_ratio2

    # Calcul de l'offset pour l'alignement temporel
    offset = int(np.mean(beat_frames2_aligned - beat_frames1_aligned))

    # Décalage de l'instrumental pour l'alignement temporel
    instru_aligned = np.roll(instru, offset)

    # Ajustement de la taille des tableaux
    size = max(len(instru_aligned), len(vocals))
    instru_aligned = increase_array_size(instru_aligned, size)
    vocals = increase_array_size(vocals, size)

    # Création du mashup
    mashup = instru_aligned + vocals

    return mashup, sr1

def mashup_technic_3(vocals, instru):
    vocals_path = './separated/mdx_extra/' + vocals + '/vocals.mp3'
    vocals_song_path = './input/' + vocals
    vocals_song_path += '.mp3' if Path(vocals_song_path+'.mp3').is_file() else '.wav'
        
    instru_path = './separated/mdx_extra/' + instru + '/no_vocals.mp3'
    instru_song_path = './input/' + instru 
    instru_song_path += '.mp3' if Path(instru_song_path+'.mp3').is_file() else '.wav'

    vocals, sr1 = librosa.load(vocals_path)
    instru, sr2   = librosa.load(instru_path)
    
    # Analyze songs (This model include the source separation by demucs --> need to be optimized later)
    results = allin1.analyze([vocals_song_path, instru_song_path])
    
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

    return mashup, sr1