class Analytics:
    def __init__(self, name):
        self.events = []
        self.name = name

    def save(self, event):
        frame = event['frame']
        if frame is None:
            exit('event must have field "frame" and it must be an integer')
        try:
            frame = int(frame)
        except:
            exit('"frame" field must be  an integer')

        self.events.append(event)

    def store(self):
        data = {}
        for event in self.events:
            frame_number = event['frame']
            frame_data = data.get(frame_number)
            for key, value in event.items():
                frame_data[key] = value

        with open('{}.json'.format(self.name), 'w') as f:
            print(data, file=f)
