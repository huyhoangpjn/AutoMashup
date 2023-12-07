import numpy as np

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
