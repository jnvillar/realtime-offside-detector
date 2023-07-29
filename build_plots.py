import json
import os
import plotly.graph_objects as go
import plotly.express as px
from natsort import natsorted
import numpy as np


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


def export_to_html_file(method, sub_problem_suffix, config):
    export_file_name = "plots/" + sub_problem_suffix
    if method != "":
        export_file_name += "-" + method

    metric_name = config[sub_problem_suffix.split("-")[0]].get('metric_name', '')
    if metric_name != "":
        export_file_name += "-" + metric_name

    export_file_name += ".html"
    fig.write_html(export_file_name)


def configure_figure_layout(fig, sub_problem_config, method, idx):
    label_y = sub_problem_config.get('label_y', None)
    if label_y.__class__.__name__ == 'list':
        label_y = sub_problem_config['label_y'][idx]

    label_x = sub_problem_config.get('label_x', None)
    if label_x.__class__.__name__ == 'list':
        label_x = sub_problem_config['label_x'][idx]

    if label_x is not None:
        label_x = label_x + ' ' + sub_problem_config['label_by_method'][
            method] if 'label_by_method' in sub_problem_config else label_x

    font_size = sub_problem_config.get('font_size', 22)
    if font_size.__class__.__name__ == 'list':
        font_size = sub_problem_config['font_size'][idx]
        if font_size is None:
            font_size = 22

    fig.update_layout(
        title=sub_problem_config.get('chart_title', None),
        xaxis=dict(
            title=label_x,
            titlefont=dict(size=font_size),
            dtick=sub_problem_config['tick'],
            range=sub_problem_config.get('x_range', None),
            tickfont=dict(size=font_size)
        ),
        yaxis=dict(
            title=label_y,
            titlefont=dict(size=font_size),
            tickfont=dict(size=font_size),
            range=sub_problem_config.get('y_range', None),
        ),
        showlegend=sub_problem_config['showlegend']
    )
    fig.update_xaxes(showline=True, linewidth=1, gridcolor='lightgrey')


def get_video_fragment_character(num_fragments_for_video, next_fragment_for_video):
    return "" if num_fragments_for_video == 1 else "." + chr(ord('A') - 1 + next_fragment_for_video)


def print_intertia_plot(frame_results, fig, video_name_in_chart, video_idx):
    frame_results = frame_results[0]
    fig.add_trace(
        go.Scatter(
            x=frame_results['k'],
            y=frame_results['inertias'],
            name=video_name_in_chart,
            hoverinfo="x",
            mode="lines",
            legendrank=video_idx
        ))


def print_player_tracker_plot(
        frame_results,
        fig,
        video_name_in_chart,
        video_idx,
        method,
        results_file_path,
        sub_problem_suffix
):
    frame_results = [d for d in frame_results if d.get('type') == 'detect_and_compare']

    method_player_detection = "_".join(method.split("_")[1:])
    no_tracking_file = "-".join(
        results_file_path.split("-")[0:2]) + "-player_detection-" + method_player_detection + ".json"
    no_tracker_results = get_results_json(no_tracking_file)
    frame_no_tracking_results = no_tracker_results["frame_results"]
    frame_no_tracking_results = [d for d in frame_no_tracking_results if d.get('type') == 'detect_and_compare']

    total_players_in_frame_no_tracking = \
        [frame_data['expected_players'] for
         frame_data in
         frame_no_tracking_results]

    good_detected_players_in_frame_no_tracking = \
        [frame_data['correctly_detected_players'] for
         frame_data in
         frame_no_tracking_results]

    extra_players_in_frame_no_tracking = \
        [frame_data['extra_detected_players'] for
         frame_data in
         frame_no_tracking_results]

    not_detected_players_in_frame_no_tracking = \
        [frame_data['not_detected_players'] for
         frame_data in
         frame_no_tracking_results]

    x_metric = None
    if sub_problem_suffix == 'player_tracker':
        x_metric = [good / total * 100 for good, total
                    in zip(good_detected_players_in_frame_no_tracking, total_players_in_frame_no_tracking)
                    ]
        if 'background_subtraction' in method and x_metric[0] <= 0.1:
            x_metric.pop(0)
    if sub_problem_suffix == 'player_tracker-extra_players':
        x_metric = extra_players_in_frame_no_tracking
    if sub_problem_suffix == 'player_tracker-not_detected_players':
        x_metric = not_detected_players_in_frame_no_tracking

    fig.add_trace(
        go.Box(
            x=x_metric,
            name=video_name_in_chart,
            boxpoints='outliers',
            hoverinfo="x",
            boxmean=True,
            legendrank=video_idx,
            showlegend=False,
            marker_color='indianred',
        )
    )

    # ----------------

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
    if sub_problem_suffix == 'player_tracker':
        x_metric = [good / total * 100 for good, total
                    in zip(good_detected_players_in_frame, total_players_in_frame)
                    ]
        if 'background_subtraction' in method and x_metric[0] <= 0.1:
            x_metric.pop(0)
    if sub_problem_suffix == 'player_tracker-extra_players':
        x_metric = extra_players_in_frame
    if sub_problem_suffix == 'player_tracker-not_detected_players':
        x_metric = not_detected_players_in_frame

    fig.add_trace(
        go.Box(
            x=x_metric,
            name=video_name_in_chart,
            boxpoints='outliers',
            hoverinfo="x",
            boxmean=True,
            showlegend=False,
            marker_color='forestgreen',
        )
    )

    ## find if any object in fig.data contains the attribute name == "Con tracking"
    legend_exists = False
    for data in fig.data:
        if data.name == "Con tracking":
            legend_exists = True

    legend = dict(
        x=0.03,
        y=0.97,
    )

    if 'extra_players' in sub_problem_suffix or 'not_detected_players' in sub_problem_suffix:
        legend = dict(
            x=0.93,
            y=0.97,
        )

    if not legend_exists:
        fig.update_layout(
            showlegend=True,
            legend=legend
        )

        fig.add_trace(
            go.Box(
                x=[None],
                y=[None],
                name="Con tracking",
                showlegend=True,
                marker_color='forestgreen',
            )
        )

        fig.add_trace(
            go.Box(
                x=[None],
                y=[None],
                name="Sin tracking",
                showlegend=True,
                marker_color='indianred',
            )
        )


def print_player_detection_plot(frame_results, fig, video_name_in_chart, video_idx):
    frame_results = [d for d in frame_results if d.get('type') == 'detect_and_compare']

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
        if 'background_subtraction' in method and x_metric[0] <= 0.1:
            x_metric.pop(0)
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


def print_player_sorter_plot(frame_results, fig, video_name_in_chart, video_idx, sub_problem_config):
    frame_results = [d for d in frame_results if d.get('type') == 'detect_and_compare']

    good_values = [frame_data[sub_problem_config['correctly_sorted_players']] for frame_data in
                   frame_results]
    badly_values = [frame_data[sub_problem_config['badly_sorted_players']] for frame_data in
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


def print_player_tracker_plot_time(
        fig,
        video_name_in_chart,
        video_idx,
        results_file_path,
        sub_problem_config
):
    aux_plot_time(
        fig,
        video_name_in_chart,
        video_idx,
        results_file_path,
        sub_problem_config
    )


def print_player_sorter_plot_time(
        fig,
        video_name_in_chart,
        video_idx,
        results_file_path,
        sub_problem_config
):
    aux_plot_time(
        fig,
        video_name_in_chart,
        video_idx,
        results_file_path,
        sub_problem_config
    )


def print_player_detection_plot_time(
        fig,
        video_name_in_chart,
        video_idx,
        results_file_path,
        sub_problem_config
):
    aux_plot_time(
        fig,
        video_name_in_chart,
        video_idx,
        results_file_path,
        sub_problem_config
    )


def print_field_detection_plot_time(
        fig,
        video_name_in_chart,
        video_idx,
        results_file_path,
        sub_problem_config
):
    aux_plot_time(
        fig,
        video_name_in_chart,
        video_idx,
        results_file_path,
        sub_problem_config)


def aux_plot_time(
        fig,
        video_name_in_chart,
        video_idx,
        results_file_path,
        sub_problem_config
):
    if sub_problem_config.get('charts', 0) == 0:
        bar_plot_time(fig, video_name_in_chart, video_idx, results_file_path, sub_problem_config)
    else:
        box_plot_time(fig, video_idx, results_file_path, sub_problem_config)


def box_plot_time(fig, video_idx, results_file_path, sub_problem_config):
    colors = ['indianred', 'forestgreen', 'royalblue', 'darkorange', 'darkviolet', 'darkturquoise']

    if sub_problem_config.get('results', None) is None:
        sub_problem_config['results'] = {
            'metrics': {},
            'color': {}
        }

    for idx, method in enumerate(sub_problem_config['time_methods']):
        file = "-".join(
            results_file_path.split("-")[0:3]) + "-" + method + ".json"
        results = get_results_json(file)

        results = [d.get("time", 0) * 1000 for d in results["frame_results"]]

        metrics = sub_problem_config['results']['metrics'].get(method, [])
        mean = np.mean(results)
        metrics.append(mean)

        sub_problem_config['results']['color'][method] = colors[idx]
        sub_problem_config['results']['metrics'][method] = metrics

    if video_idx == 1:
        sub_problem_config['charts'] = 1

        for k, v in sub_problem_config['results']['metrics'].items():
            fig.add_trace(
                go.Box(
                    x=v,
                    name=sub_problem_config['translations'][k],
                    boxpoints="all",
                    boxmean=True,
                    legendrank=video_idx,
                    marker=dict(
                        color=sub_problem_config['results']['color'][k]  # Assign colors based on the method
                    ),
                )
            )
        fig.update_layout(legend=dict(x=0.99, y=0.99, xanchor='right', yanchor='top'))
        sub_problem_config['results'] = None


def bar_plot_time(fig, video_name_in_chart, video_idx, results_file_path, sub_problem_config):
    if sub_problem_config.get('results', None) is None:
        sub_problem_config['results'] = {
            'metrics': {},
            'video_name': {},
            'color': {},
            'max_y': 0
        }

    colors = ['indianred', 'forestgreen', 'royalblue', 'darkorange', 'darkviolet', 'darkturquoise']

    for idx, method in enumerate(sub_problem_config['time_methods']):
        file = "-".join(
            results_file_path.split("-")[0:3]) + "-" + method + ".json"
        results = get_results_json(file)

        results = [d.get("time", 0) * 1000 for d in results["frame_results"]]

        metrics = sub_problem_config['results']['metrics'].get(method, [])
        mean = np.mean(results)
        metrics.append(mean)
        if mean > sub_problem_config['results']['max_y']:
            sub_problem_config['results']['max_y'] = mean

        sub_problem_config['results']['metrics'][method] = metrics

        video_name = sub_problem_config['results']['video_name'].get(method, [])
        video_name.append(video_name_in_chart)
        sub_problem_config['results']['video_name'][method] = video_name

        sub_problem_config['results']['color'][method] = colors[idx]

    if video_idx == 1:
        sub_problem_config['charts'] = 1

        for k, v in sub_problem_config['results']['metrics'].items():
            fig.add_trace(
                go.Bar(
                    name=sub_problem_config['translations'][k],
                    y=sub_problem_config['results']['metrics'][k],
                    x=sub_problem_config['results']['video_name'][k],
                    # orientation='h',  # Hori
                    marker=dict(
                        color=sub_problem_config['results']['color'][k]  # Assign colors based on the method
                    ),
                    text=sub_problem_config['results']['metrics'][k],
                    textposition='auto',  # 'auto' places the labels inside the bars
                    texttemplate='%{text:.2f} ms',
                )
            )

        fig.update_layout(yaxis=dict(range=[0, sub_problem_config['results']['max_y'] * 1.13]))
        fig.update_layout(barmode='group')
        fig.update_layout(legend=dict(x=0.99, y=0.99, xanchor='right', yanchor='top'))
        sub_problem_config['results'] = None


def print_field_detection_plot(frame_results, fig, video_name_in_chart, video_idx, sub_problem_config):
    frame_results = [d for d in frame_results if d.get('type') == 'detect_and_compare']

    metric_values = [frame_data[sub_problem_config['metric_name']] for frame_data in frame_results]
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


def print_vanishing_point_plot(frame_results, fig, video_name_in_chart, video_idx, sub_problem_config):
    frame_results = [d for d in frame_results if d.get('type') == 'detect_and_compare']

    metric_values = [frame_data[sub_problem_config['metric_name']] for frame_data in frame_results]
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


config = {
    "intertia": {
        'methods': [
            'intertia',
        ],
        'label_x': 'K',
        'label_y': 'Inercia',
        'tick': None,
        'showlegend': True,
    },
    "field_detection": {
        'chart_title': None,
        'metric_name': "jaccard_index",
        'label_x': 'Indice de Jaccard',
        'tick': None,
        'showlegend': False,
        'x_range': None,
        'methods': [
            'green_detection', 'ground_pixels_detection'
        ],
    },
    "field_detection_time": {
        'chart_title': None,
        'label_y': ['Tiempo (ms)', None],
        'label_x': [None, 'Tiempo (ms)'],
        'tick': None,
        'showlegend': True,
        'x_range': None,
        'methods': [
            'bar', 'box'
        ],
        'translations': {
            'green_detection': 'Detección de verde',
            'ground_pixels_detection': 'G>R>B',
        },
        'time_methods': [
            'green_detection', 'ground_pixels_detection'
        ]
    },
    "player_detection_time": {
        'chart_title': None,
        'label_y': ['Tiempo (ms)', None],
        'label_x': [None, 'Tiempo (ms)'],
        'tick': None,
        'showlegend': True,
        'x_range': None,
        'methods': [
            'bar', 'box'
        ],
        'translations': {
            'edges': 'Bordes',
            'otsu': 'Otsu',
            'background_subtraction': 'Substracción de fondo',
            'kmeans': 'K-Means',
            'by_color': 'Color'
        },
        'time_methods': [
            'edges', 'otsu', 'background_subtraction', 'kmeans', 'by_color'
        ]
    },
    "player_sorter_time": {
        'chart_title': None,
        'label_y': ['Tiempo (ms)', None],
        'label_x': [None, 'Tiempo (ms)'],
        'tick': None,
        'showlegend': True,
        'x_range': None,
        'translations': {
            'kmeans': 'K-Means',
            'bsas': 'BSAS',
        },
        'methods': [
            'bar', 'box'
        ],
        'time_methods': [
            'kmeans', 'bsas'
        ]
    },
    "vanishing_point_finder_time": {
        'chart_title': None,
        'label_y': ['Tiempo (ms)', None],
        'label_x': [None, 'Tiempo (ms)'],
        'tick': None,
        'showlegend': True,
        'x_range': None,
        'translations': {
            'hough': 'Calculo de punto de fuga',
        },
        'methods': [
            'bar', 'box'
        ],
        'time_methods': [
            'hough'
        ]
    },
    "player_tracker_time": {
        'chart_title': None,
        'label_y': ['Tiempo (ms)', None],
        'label_x': [None, 'Tiempo (ms)'],
        'tick': None,
        'showlegend': True,
        'x_range': None,
        'methods': [
            'bar', 'box'
        ],
        'translations': {
            'distance_edges': 'Bordes',
            'distance_otsu': 'Otsu',
            'distance_background_subtraction': 'Substracción de fondo',
            'distance_kmeans': 'K-Means',
            'distance_by_color': 'Color'
        },
        'time_methods': [
            'distance_edges', 'distance_otsu', 'distance_background_subtraction', 'distance_kmeans', 'distance_by_color'
        ],
        'font_size': [22, 18]
    },
    "vanishing_point_finder": {
        'chart_title': None,
        'metric_name': "distance_meters",
        'label_x': 'Distancia (metros)',
        'tick': None,
        'showlegend': False,
        'x_range': [0, 35],
        'methods': ['hough']
    },
    "player_sorter": {
        'methods': [
            'kmeans',
            'bsas'
        ],
        'chart_title': None,
        'label_x': 'Ok percentage',
        'tick': None,
        'showlegend': False,
        'correctly_sorted_players': "correctly_sorted_players",
        'badly_sorted_players': "badly_sorted_players",
    },
    "player_detection": {
        'chart_title': None,
        'methods': [
            'edges', 'otsu', 'background_subtraction', 'kmeans', 'by_color'
        ],
        'label_by_method': {
            'edges': 'utilizando detección por bordes',
            'otsu': 'utilizando detección por Otsu',
            'background_subtraction': 'utilizando detección por substracción de fondo',
            'kmeans': 'utilizando detección por K-Means',
            'by_color': 'utilizando detección por color'
        },
        'label_x': 'Porcentaje de jugadores detectados correctamente',
        'tick': None,
        'showlegend': False,
        'x_range': [0, 100]
    },
    "player_detection-extra_players": {
        'chart_title': None,
        'label_x': 'Cantidad de jugadores detectados de más',
        'methods': [
            'edges', 'otsu', 'background_subtraction', 'kmeans', 'by_color'
        ],
        'label_by_method': {
            'edges': 'utilizando detección por bordes',
            'otsu': 'utilizando detección por Otsu',
            'background_subtraction': 'utilizando detección por substracción de fondo',
            'kmeans': 'utilizando detección por K-Means',
            'by_color': 'utilizando detección por color'
        },
        'tick': None,
        'showlegend': False,
        'x_range': [0, 20]
    },
    "player_detection-not_detected_players": {
        'chart_title': None,
        'label_x': 'Cantidad de jugadores no detectados',
        'methods': [
            'edges', 'otsu', 'background_subtraction', 'kmeans', 'by_color'
        ],
        'label_by_method': {
            'edges': 'utilizando detección por bordes',
            'otsu': 'utilizando detección por Otsu',
            'background_subtraction': 'utilizando detección por substracción de fondo',
            'kmeans': 'utilizando detección por K-Means',
            'by_color': 'utilizando detección por color'
        },
        'tick': None,
        'showlegend': False,
        'x_range': [0, 20]
    },
    "player_tracker": {
        'chart_title': None,
        'methods': [
            'distance_edges', 'distance_otsu', 'distance_background_subtraction', 'distance_kmeans', 'distance_by_color'
        ],
        'label_x': 'Porcentaje de jugadores detectados correctamente',
        'label_by_method': {
            'distance_edges': 'utilizando detección por bordes',
            'distance_otsu': 'utilizando detección por Otsu',
            'distance_background_subtraction': 'utilizando etección por substracción de fondo',
            'distance_kmeans': 'utilizando detección por K-Means',
            'distance_by_color': 'utilizando detección por color'
        },
        'tick': None,
        'showlegend': False,
        'x_range': [0, 101]
    },
    "player_tracker-extra_players": {
        'chart_title': None,
        'methods': [
            'distance_edges', 'distance_otsu', 'distance_background_subtraction', 'distance_kmeans', 'distance_by_color'
        ],
        'label_x': 'Cantidad de jugadores detectados de más',
        'label_by_method': {
            'distance_edges': 'utilizando detección por bordes',
            'distance_otsu': 'utilizando detección por Otsu',
            'distance_background_subtraction': 'utilizando etección por substracción de fondo',
            'distance_kmeans': 'utilizando detección por K-Means',
            'distance_by_color': 'utilizando detección por color'
        },
        'tick': None,
        'showlegend': False,
        'x_range': [0, 20]
    },
    "player_tracker-not_detected_players": {
        'chart_title': None,
        'methods': [
            'distance_edges', 'distance_otsu', 'distance_background_subtraction', 'distance_kmeans', 'distance_by_color'
        ],
        'label_x': 'Cantidad de jugadores no detectados',
        'label_by_method': {
            'distance_edges': 'utilizando detección por bordes',
            'distance_otsu': 'utilizando detección por Otsu',
            'distance_background_subtraction': 'utilizando etección por substracción de fondo',
            'distance_kmeans': 'utilizando detección por K-Means',
            'distance_by_color': 'utilizando detección por color'
        },
        'tick': None,
        'showlegend': False,
        'x_range': [0, 20]
    },
}

if __name__ == '__main__':

    sub_problem_suffix = "player_detection-not_detected_players"  # field_detection, intertia, player_sorter, player_detection, player_tracker

    sub_problem_config = config[sub_problem_suffix]
    methods = sub_problem_config['methods']

    export_html_file = True
    videos_to_consider = scan_videos_from_path("./test/videos")
    x_axis_title = sub_problem_config.get('label_x', None)

    for idx, method in enumerate(methods):
        fig = go.Figure()
        configure_figure_layout(fig, sub_problem_config, method, idx)

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
            video_name_without_extension = video_name.split(".")[0]
            sub_problem_suffix_without_time = sub_problem_suffix.replace("_time", "")
            results_file_path = './experiments/' + video_name_without_extension + "-" + \
                                sub_problem_suffix_without_time.split("-")[0]
            video_name_in_chart = "{} {}{} ".format("Video", video_id,
                                                    get_video_fragment_character(fragments_per_video[video_id],
                                                                                 next_fragment_per_video.get(video_id,
                                                                                                             1)))
            next_fragment_per_video[video_id] = next_fragment_per_video.get(video_id, 1) - 1

            if method != "":
                results_file_path = results_file_path + "-" + method

            results_file_path += ".json"

            frame_results = None
            if "time" not in sub_problem_suffix:
                results = get_results_json(results_file_path)
                if "frame_results" not in results:
                    continue
                frame_results = results["frame_results"]

            if sub_problem_suffix == 'intertia' and len(frame_results) > 0:
                print_intertia_plot(frame_results, fig, video_name_in_chart, video_idx)

            if 'player_tracker' in sub_problem_suffix and "time" not in sub_problem_suffix:
                print_player_tracker_plot(frame_results, fig, video_name_in_chart, video_idx, method, results_file_path,
                                          sub_problem_suffix)

            if sub_problem_suffix.split("-")[0] == 'player_detection':
                print_player_detection_plot(frame_results, fig, video_name_in_chart, video_idx)

            if sub_problem_suffix == 'player_sorter' and len(frame_results) > 0:
                print_player_sorter_plot(frame_results, fig, video_name_in_chart, video_idx, sub_problem_config)

            if sub_problem_suffix == 'field_detection':
                print_field_detection_plot(frame_results, fig, video_name_in_chart, video_idx, sub_problem_config)

            if sub_problem_suffix == 'vanishing_point_finder':
                print_vanishing_point_plot(frame_results, fig, video_name_in_chart, video_idx, sub_problem_config)

            if sub_problem_suffix == 'field_detection_time':
                print_field_detection_plot_time(fig, video_name_in_chart, video_idx, results_file_path,
                                                sub_problem_config)

            if sub_problem_suffix == 'player_detection_time':
                print_player_detection_plot_time(fig, video_name_in_chart, video_idx, results_file_path,
                                                 sub_problem_config)

            if sub_problem_suffix == 'player_sorter_time':
                print_player_sorter_plot_time(fig, video_name_in_chart, video_idx, results_file_path,
                                              sub_problem_config)

            if sub_problem_suffix == 'vanishing_point_finder_time':
                print_player_sorter_plot_time(fig, video_name_in_chart, video_idx, results_file_path,
                                              sub_problem_config)

            if sub_problem_suffix == 'player_tracker_time':
                print_player_tracker_plot_time(fig, video_name_in_chart, video_idx, results_file_path,
                                               sub_problem_config)

            video_idx -= 1

        if export_html_file:
            export_to_html_file(method, sub_problem_suffix, config)

        fig.show()
