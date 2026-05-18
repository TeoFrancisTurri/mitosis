from client.config import CAMERA_ZOOM_SPEED, CAMERA_ZOOM_MIN, CAMERA_ZOOM_BASE, CAMERA_ZOOM_MASS_POWER, CAMERA_ZOOM_CELL_POWER, CAMERA_ZOOM_REFERENCE_WIDTH


class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0
        self.zoom = 1.0

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.half_screen_width = screen_width // 2
        self.half_screen_height = screen_height // 2

    def update(self, target_x, target_y, cell_count, total_mass, delta_time):
        self.x = target_x - self.half_screen_width
        self.y = target_y - self.half_screen_height

        screen_factor = self.screen_width / CAMERA_ZOOM_REFERENCE_WIDTH
        target_zoom = screen_factor * CAMERA_ZOOM_BASE / (total_mass ** CAMERA_ZOOM_MASS_POWER * cell_count ** CAMERA_ZOOM_CELL_POWER)
        target_zoom = max(CAMERA_ZOOM_MIN, target_zoom)
        self.zoom += (target_zoom - self.zoom) * CAMERA_ZOOM_SPEED * delta_time

    def apply(self, x, y):
        rel_x = x - self.x - self.half_screen_width
        rel_y = y - self.y - self.half_screen_height
        return (
            rel_x * self.zoom + self.half_screen_width,
            rel_y * self.zoom + self.half_screen_height,
        )

    def scale(self, size):
        return size * self.zoom
