import json
from domain.status import *


class Analytics:
    def __init__(self, name, **kwargs):
        self.events = []
        self.name = name
        self.config = kwargs

    def save(self, event):
        if self.config.get('status', Status.inactive) == Status.inactive:
            return

        frame = event['frame']
        if frame is None:
            exit('event must have field "frame" and it must be an integer')
        try:
            int(frame)
        except:
            exit('"frame" field must be  an integer')

        for k, v in event.items():
            if k is None or v is None:
                exit('invalid event {}'.format(event))

        self.events.append(event)

    def store(self):
        if self.config.get('status', Status.inactive) == Status.inactive:
            return

        data = {}
        for event in self.events:
            frame_number = event['frame']
            frame_data = data.get(frame_number, {})
            for key, value in event.items():
                frame_data[key] = value
            data[frame_number] = frame_data

        with open('{}.json'.format(self.name), 'w') as f:
            json_object = json.dumps(data, default=lambda o: o.__dict__(), indent=4)
            print(json_object, file=f)
