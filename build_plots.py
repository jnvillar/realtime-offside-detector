import json
import os

import matplotlib.pyplot as plt
import numpy as np

from utils import constants


def get_results_json(results_file_path):
    json_data = {}
    if os.path.isfile(results_file_path):
        with open(results_file_path, 'r') as file:
            json_data = json.load(file)
    else:
        print('File {} does not exist. No results loaded.'.format(results_file_path))

    return json_data


if __name__ == '__main__':

    # x axis variables
    x_label = 'Numero de frame'
    x_min = 0
    x_max = 270
    x_tick = 20
    # y axis variables
    y_label = 'Indice de Jaccard'
    y_min = 0
    y_max = 1
    y_tick = 0.1


    video_name = constants.VideoConstants.video_1_Arsenal_Chelsea_107_122
    results_file_path = './experiments' + '/' + video_name.split(".")[0] + "-field-detection.json"
    results = get_results_json(results_file_path)

    frame_results = results["frame_results"]
    frame_numbers = [frame_data["frame_number"] for frame_data in frame_results]
    jaccard = [frame_data['jaccard_index'] for frame_data in frame_results]

    plt.plot(frame_numbers, jaccard, 'o')
    plt.ylabel(y_label)
    plt.xlabel(x_label)
    plt.ylim(y_min, y_max)
    plt.xlim(x_min, x_max)
    plt.yticks(np.arange(y_min, y_max, y_tick))
    plt.xticks(np.arange(x_min, x_max, x_tick))
    plt.show()
