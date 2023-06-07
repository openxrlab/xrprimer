from viewer_state import ViewerState

# TODO: use import paths relative to `xrprimer` rather than the current parent
# TODO: directory to separate the entrypoint and libraries. Unfortunately, the
# TODO: xrprimer cannot be installed on a Windows machine. Need to be tested on
# TODO: MacOS later.
# from python.xrprimer.services.xrnerf.viewer_state import ViewerState


def run_viewer():
    """start the viewer."""
    viewer_state = ViewerState()
    while True:
        viewer_state.update_scene()


if __name__ == '__main__':
    run_viewer()
