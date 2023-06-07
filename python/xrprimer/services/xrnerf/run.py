from viewer_state import ViewerState


def run_viewer():
    """start the viewer."""
    viewer_state = ViewerState()
    while True:
        viewer_state.update_scene()


if __name__ == '__main__':
    run_viewer()
