import json
import os
import plotly.graph_objects as go

def get_results_json(results_file_path):
    json_data = {}
    if os.path.isfile(results_file_path):
        with open(results_file_path, 'r') as file:
            json_data = json.load(file)
    else:
        print('File {} does not exist. No results loaded.'.format(results_file_path))

    return json_data


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
    }
}

if __name__ == '__main__':

    sub_problem_suffix = "intertia"  # field-detection, intertia

    videos_path = "./test/videos"
    videos_to_consider = []
    with os.scandir(videos_path) as dir_iterator:
        for file in dir_iterator:
            # only consider files starting with a number and with mp4 extension
            video_name = file.name
            if file.is_file() and video_name[0].isdigit() and video_name.endswith('.mp4'):
                videos_to_consider.append(video_name)

        fig = go.Figure()
        fig.update_layout(
            title=config[sub_problem_suffix]['chart_title'],
            xaxis_title=config[sub_problem_suffix]['label_x'],
            yaxis_title=config[sub_problem_suffix].get('label_y', None),
            xaxis=dict(dtick=config[sub_problem_suffix]['tick']),
            showlegend=config[sub_problem_suffix]['showlegend']
        )

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
                        mode="lines")
                )
            else:
                metric_values = [frame_data[config[sub_problem_suffix]['metric_name']] for frame_data in frame_results]
                fig.add_trace(
                    go.Box(x=metric_values, name=video_name_without_extesion, boxpoints="all", hoverinfo="x",
                           boxmean=True)
                )

        fig.show()
