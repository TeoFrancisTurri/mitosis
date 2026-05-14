class Camera:
    def __init__(self, screen_width, screen_height):
        self.x = 0
        self.y = 0

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.half_screen_width = screen_width // 2
        self.half_screen_height = screen_height // 2

    def update(self, target_x, target_y):
        self.x = target_x - self.half_screen_width
        self.y = target_y - self.half_screen_height

    def apply(self, x, y):
        return (
            x - self.x,
            y - self.y
        )