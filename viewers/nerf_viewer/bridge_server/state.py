class State:
    def __init__(self):
        self.camera_rotation = [
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0
        ]
        self.camera_translation = [0.0, 0.0, 0.0]
        self.camera_fov = 60
        self.resolution = 720
        self.render_type = 'rgb'