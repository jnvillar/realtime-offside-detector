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
        'label_x': 'K',
        'label_y': 'Inercia',
        'tick': None,
        'showlegend': True,
    },
    "field_detection": {
        'chart_title': None,
        'metric_name': "jaccard_index",
        'label_x': 'Field detection',
        'label_x': 'Indice de Jaccard',
        'tick': None,
        'showlegend': False,
        'x_range': None
    },
    "vanishing-point-finder": {
        'chart_title': None,
        'metric_name': "x_axis_distance_percentage",
        'label_x': 'Distancia',
        'tick': None,
        'showlegend': True,
        'x_range': None
    },
    "player_sorter": {
        'chart_title': None,
        'label_x': 'Ok percentage',
        'tick': None,
        'showlegend': False,
        'correctly_sorted_players': "correctly_sorted_players",
        'badly_sorted_players': "badly_sorted_players",
    },
    "player_detection": {
        'chart_title': None,
        'label_x': 'Ok percentage',
        'tick': None,
        'showlegend': False,
        'x_range': [0, 100]
    },
    "player_detection-extra_players": {
        'chart_title': None,
        'label_x': 'Extra detected players',
        'tick': None,
        'showlegend': False,
        'x_range': [0, 20]
    },
    "player_detection-not_detected_players": {
        'chart_title': None,
        'label_x': 'Not detected players',
        'tick': None,
        'showlegend': False,
        'x_range': [0, 20]
    },
}

if __name__ == '__main__':

    sub_problem_suffix = "player_detection-not_detected_players"  # field_detection, intertia, player_sorter, player_detection
    method = "kmeans"  # background_subtraction, hough_transform, hough_transform_with_background_subtraction, hough_transform_with_background_subtraction_and_field_detection

    export_html_file = True

    videos_to_consider = scan_videos_from_path("./test/videos")

    font_size = 22
    fig = go.Figure()
    fig.update_layout(
        title=config[sub_problem_suffix].get('chart_title', None),
        xaxis=dict(
            title=config[sub_problem_suffix]['label_x'],
            titlefont=dict(size=font_size),
            dtick=config[sub_problem_suffix]['tick'],
            range=config[sub_problem_suffix].get('x_range', None),
            tickfont=dict(size=font_size)
        ),
        yaxis=dict(
            title=config[sub_problem_suffix].get('label_y', None),
            titlefont=dict(size=font_size),
            tickfont=dict(size=font_size)
        ),
        showlegend=config[sub_problem_suffix]['showlegend']
    )
    fig.update_xaxes(showline=True, linewidth=1, gridcolor='lightgrey')

    # to know which videos have more than one fragment
    fragments_per_video = {}
    for video_name in videos_to_consider:
        video_id = video_name.split("_")[0]
        fragments_per_video[video_id] = fragments_per_video.get(video_id, 0) + 1

    # to keep track of which is the next fragment for a video
    next_fragment_per_video = fragments_per_video.copy()
    video_idx = len(videos_to_consider)
    for video_name in videos_to_consider:
        video_id = video_name.split("_")[0]
        video_name_without_extesion = video_name.split(".")[0]
        results_file_path = './experiments/' + video_name_without_extesion + "-" + sub_problem_suffix.split("-")[0]
        video_name_in_chart = "{} {}{} ".format("Video", video_id, "" if fragments_per_video[video_id] == 1 else "." + chr(ord('A') - 1 + next_fragment_per_video.get(video_id, 1)))
        next_fragment_per_video[video_id] = next_fragment_per_video.get(video_id, 1) - 1

        if method != "":
            results_file_path = results_file_path + "-" + method

        results_file_path += ".json"

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
                    name=video_name_in_chart,
                    hoverinfo="x",
                    mode="lines",
                    legendrank=video_idx
                ))

        if sub_problem_suffix.split("-")[0] == 'player_detection':
            total_players_in_frame = \
                [frame_data['expected_players'] for
                 frame_data in
                 frame_results]

            good_detected_players_in_frame = \
                [frame_data['correctly_detected_players'] for
                 frame_data in
                 frame_results]

            extra_players_in_frame = \
                [frame_data['extra_detected_players'] for
                 frame_data in
                 frame_results]

            not_detected_players_in_frame = \
                [frame_data['not_detected_players'] for
                 frame_data in
                 frame_results]

            x_metric = None
            if sub_problem_suffix == 'player_detection':
                x_metric = [good / total * 100 for good, total
                            in zip(good_detected_players_in_frame, total_players_in_frame)
                            ]
            if sub_problem_suffix == 'player_detection-extra_players':
                x_metric = extra_players_in_frame
            if sub_problem_suffix == 'player_detection-not_detected_players':
                x_metric = not_detected_players_in_frame

            fig.add_trace(
                go.Box(
                    x=x_metric,
                    name=video_name_in_chart,
                    boxpoints="all",
                    hoverinfo="x",
                    boxmean=True,
                    legendrank=video_idx
                )
            )

        if sub_problem_suffix == 'player_sorter' and len(results["frame_results"]) > 0:
            good_values = [frame_data[config[sub_problem_suffix]['correctly_sorted_players']] for frame_data in
                           frame_results]
            badly_values = [frame_data[config[sub_problem_suffix]['badly_sorted_players']] for frame_data in
                            frame_results]

            totals = [x + y for x, y in zip(good_values, badly_values)]
            good_percentage = [good / total * 100 for good, total in zip(good_values, totals)]

            fig.add_trace(
                go.Box(
                    x=good_percentage,
                    name=video_name_in_chart,
                    boxpoints="all",
                    hoverinfo="x",
                    boxmean=True,
                    legendrank=video_idx
                )
            )

        if sub_problem_suffix == 'field_detection':
            metric_values = [frame_data[config[sub_problem_suffix]['metric_name']] for frame_data in frame_results]
            frame_numbers = [frame_data['frame_number'] for frame_data in frame_results]

            fig.add_trace(
                go.Box(
                    x=metric_values,
                    name=video_name_in_chart,
                    customdata=frame_numbers,
                    hovertemplate='Value: %{x}<br>Frame: %{customdata} <extra></extra>',
                    boxpoints="all",
                    boxmean=True,
                    legendrank=video_idx
                )
            )

        if sub_problem_suffix == 'vanishing-point-finder':
            metric_values = [frame_data[config[sub_problem_suffix]['metric_name']] for frame_data in frame_results]
            frame_numbers = [frame_data['frame_number'] for frame_data in frame_results]

            fig.add_trace(
                go.Box(
                    x=metric_values,
                    name=video_name_in_chart,
                    customdata=frame_numbers,
                    hovertemplate='Value: %{x}<br>Frame: %{customdata} <extra></extra>',
                    boxpoints="all",
                    boxmean=True,
                    legendrank=video_idx
                )
            )

        video_idx -= 1

    if export_html_file:
        export_file_name = "plots/" + sub_problem_suffix
        if method != "":
            export_file_name += "-" + method

        metric_name = config[sub_problem_suffix.split("-")[0]].get('metric_name', '')
        if metric_name != "":
            export_file_name += "-" + metric_name

        export_file_name += ".html"
        fig.write_html(export_file_name)

    fig.show()
