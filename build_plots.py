import json
import os

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def get_results_json(results_file_path):
    json_data = {}
    if os.path.isfile(results_file_path):
        with open(results_file_path, 'r') as file:
            json_data = json.load(file)
    else:
        print('File {} does not exist. No results loaded.'.format(results_file_path))

    return json_data


if __name__ == '__main__':

    chart_title = None
    metric_name = "jaccard_index"
    sub_problem_suffix = "intertia"  # field-detection, intertia
    label = 'Elbow method'
    tick = None
    showlegend = False

    videos_path = "./test/videos"
    videos_to_consider = []
    with os.scandir(videos_path) as dir_iterator:
        for file in dir_iterator:
            # only consider files starting with a number and with mp4 extension
            video_name = file.name
            if file.is_file() and video_name[0].isdigit() and video_name.endswith('.mp4'):
                videos_to_consider.append(video_name)

        fig = go.Figure()
        fig.update_layout(title=chart_title, xaxis_title=label, xaxis=dict(dtick=tick), showlegend=showlegend)
        for video_name in videos_to_consider:
            video_name_without_extesion = video_name.split(".")[0]
            results_file_path = './experiments/' + video_name_without_extesion + "-" + sub_problem_suffix + ".json"
            results = get_results_json(results_file_path)

            if "frame_results" in results:
                frame_results = results["frame_results"]

                if sub_problem_suffix == 'intertia' and len(results["frame_results"]) > 0:
                    frame_results = results["frame_results"][0]

                    data = {
                        'k': frame_results['k'],
                        'inertias': frame_results['inertias'],
                    }

                    df = pd.DataFrame(data)

                    fig.add_trace(
                        go.Scatter(x=df["k"], y=df["inertias"], name=video_name_without_extesion, mode="lines")
                    )
                else:
                    metric_values = [frame_data[metric_name] for frame_data in frame_results]
                    fig.add_trace(
                        go.Box(x=metric_values, name=video_name_without_extesion, boxpoints="all", hoverinfo="x",
                               boxmean=True)
                    )

        fig.show()
