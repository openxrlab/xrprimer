from .base_world import BaseWorld


class SenseMoCapWorld(BaseWorld):
    """A world class for SenseMoCap coordinate convention.

    A human subject in this word faces to somewhere on xOz plane and his head
    is up towards y-. By using the rotation rotation matrix of this world(left
    multiplication), 3D data can be transformed from base world space to the
    current space.
    """
    ROTATION = BaseWorld.ROTATION
