import json
import os
import plotly.graph_objects as go
from natsort import natsorted


def get_results_json(results_file_path):
    json_data = {}
    if os.path.isfile(results_file_path):
        with open(results_file_path, 'r') as file:
            json_data = json.load(file)
    else:
        print('File {} does not exist. No results loaded.'.format(results_file_path))

    return json_data


def scan_videos_from_path(videos_path):
    videos_to_consider = []
    with os.scandir(videos_path) as dir_iterator:
        for file in dir_iterator:
            # only consider files starting with a number and with mp4 extension
            video_name = file.name
            if file.is_file() and video_name[0].isdigit() and video_name.endswith('.mp4'):
                videos_to_consider.append(video_name)
    # sort videos to always be consistent
    return natsorted(videos_to_consider, reverse=True)


config = {
    "intertia": {
        'chart_title': 'Elbow method',
        'label_x': 'K',
        'label_y': 'Inercia',
        'tick': None,
        'showlegend': True,
    },
    "field-detection": {
        'chart_title': 'Field detection',
        'metric_name': "jaccard_index",
        'label_x': 'Field detection',
        'tick': None,
        'showlegend': True,
    },
    "players-sorting": {
        'chart_title': 'Sort Players',
        'label_x': 'Ok percentage',
        'tick': None,
        'showlegend': True,
        'correctly_sorted_players': "correctly_sorted_players",
        'badly_sorted_players': "badly_sorted_players",
    },
    "players-detection": {
        'chart_title': 'Player Detection',
        'label_x': 'Ok percentage',
        'tick': None,
        'showlegend': True
    },
}

if __name__ == '__main__':

    sub_problem_suffix = "players-detection"  # field-detection, intertia, players-sorting, players-detection

    videos_to_consider = scan_videos_from_path("./test/videos")

    fig = go.Figure()
    fig.update_layout(
        title=config[sub_problem_suffix]['chart_title'],
        xaxis_title=config[sub_problem_suffix]['label_x'],
        yaxis_title=config[sub_problem_suffix].get('label_y', None),
        xaxis=dict(dtick=config[sub_problem_suffix]['tick']),
        showlegend=config[sub_problem_suffix]['showlegend']
    )
    fig.update_xaxes(showline=True, linewidth=1, gridcolor='lightgrey')

    video_idx = len(videos_to_consider)
    for video_name in videos_to_consider:
        video_name_without_extesion = video_name.split(".")[0]
        results_file_path = './experiments/' + video_name_without_extesion + "-" + sub_problem_suffix + ".json"
        results = get_results_json(results_file_path)

        if not "frame_results" in results:
            continue

        frame_results = results["frame_results"]

        if sub_problem_suffix == 'intertia' and len(results["frame_results"]) > 0:
            frame_results = results["frame_results"][0]
            fig.add_trace(
                go.Scatter(
                    x=frame_results['k'],
                    y=frame_results['inertias'],
                    name=video_name_without_extesion,
                    hoverinfo="x",
                    mode="lines",
                    legendrank=video_idx
                ))

        if sub_problem_suffix == 'players-detection':
            total_players_in_frame = \
                [frame_data['expected_players'] for
                 frame_data in
                 frame_results]

            good_detected_players_in_frame = \
                [frame_data['correctly_detected_players'] for
                 frame_data in
                 frame_results]

            good_percentage = [good / total * 100 for good, total
                               in zip(good_detected_players_in_frame, total_players_in_frame)
                               ]

            fig.add_trace(
                go.Box(
                    x=good_percentage,
                    name=video_name_without_extesion,
                    boxpoints="all",
                    hoverinfo="x",
                    boxmean=True,
                    legendrank=video_idx
                )
            )

        if sub_problem_suffix == 'players-sorting' and len(results["frame_results"]) > 0:
            good_values = [frame_data[config[sub_problem_suffix]['correctly_sorted_players']] for frame_data in
                           frame_results]
            badly_values = [frame_data[config[sub_problem_suffix]['badly_sorted_players']] for frame_data in
                            frame_results]

            totals = [x + y for x, y in zip(good_values, badly_values)]
            good_percentage = [good / total * 100 for good, total in zip(good_values, totals)]

            fig.add_trace(
                go.Box(
                    x=good_percentage,
                    name=video_name_without_extesion,
                    boxpoints="all",
                    hoverinfo="x",
                    boxmean=True,
                    legendrank=video_idx
                )
            )

        if sub_problem_suffix == 'field-detection':
            metric_values = [frame_data[config[sub_problem_suffix]['metric_name']] for frame_data in frame_results]
            frame_numbers = [frame_data['frame_number'] for frame_data in frame_results]

            fig.add_trace(
                go.Box(
                    x=metric_values,
                    name=video_name_without_extesion,
                    customdata=frame_numbers,
                    hovertemplate='Value: %{x}<br>Frame: %{customdata} <extra></extra>',
                    boxpoints="all",
                    boxmean=True,
                    legendrank=video_idx
                )
            )

        video_idx -= 1

    fig.show()
