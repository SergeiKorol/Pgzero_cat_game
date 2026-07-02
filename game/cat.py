from config import CELL


class Cat:
    """Кот на поле: отрисовка, анимация ходьбы и ожидания."""

    def __init__(self, username, cell_x, cell_y):
        """
        Создаёт кота в указанной клетке.

        :param username: никнейм игрока из Telegram
        :param cell_x: клетка X на сетке (0-31)
        :param cell_y: клетка Y на сетке (0-31)
        """
        self.username = username
        self.target_cell_x = cell_x
        self.target_cell_y = cell_y
        self.pixel_x = cell_x * CELL
        self.pixel_y = cell_y * CELL
        self.direction = "down"
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.is_moving = False

    def move_to_cell(self, cell_x, cell_y):
        """
        Задаёт новую целевую клетку и направление спрайта.

        Если координаты не изменились, ничего не делает.
        """
        if cell_x == self.target_cell_x and cell_y == self.target_cell_y:
            return
        delta_x = cell_x - self.target_cell_x
        delta_y = cell_y - self.target_cell_y
        if abs(delta_x) >= abs(delta_y):
            self.direction = "right" if delta_x > 0 else "left"
        else:
            self.direction = "down" if delta_y > 0 else "up"
        self.target_cell_x = cell_x
        self.target_cell_y = cell_y
        self.animation_frame = 0
        self.is_moving = True

    def update(self, delta_time):
        """
        Плавно сдвигает кота к целевой клетке и переключает кадры анимации.

        :param delta_time: время с прошлого кадра (секунды)
        """
        target_pixel_x = self.target_cell_x * CELL
        target_pixel_y = self.target_cell_y * CELL
        offset_x = target_pixel_x - self.pixel_x
        offset_y = target_pixel_y - self.pixel_y
        distance = (offset_x * offset_x + offset_y * offset_y) ** 0.5

        if distance < 1:
            self.pixel_x = float(target_pixel_x)
            self.pixel_y = float(target_pixel_y)
            self.is_moving = False
            return

        move_step = (CELL / 0.8) * delta_time
        if move_step >= distance:
            self.pixel_x = float(target_pixel_x)
            self.pixel_y = float(target_pixel_y)
            self.is_moving = False
        else:
            self.pixel_x += offset_x / distance * move_step
            self.pixel_y += offset_y / distance * move_step
            self.is_moving = True
            self.animation_timer += delta_time
            if self.animation_timer > 0.15:
                self.animation_timer = 0.0
                self.animation_frame = (self.animation_frame + 1) % 4

    def draw(self, screen, actor_class):
        """
        Рисует спрайт кота и никнейм над ним.

        :param screen: поверхность pgzero
        :param actor_class: класс Actor из pgzero
        """
        if self.is_moving:
            sprite_name = f"walk_{self.direction}/cat_walk_{self.direction}_{self.animation_frame + 1}"
        else:
            sprite_name = f"wait_{self.direction}/cat_wait_{self.direction}_1"
        sprite = actor_class(sprite_name, pos=(self.pixel_x + 16, self.pixel_y + 16))
        sprite.draw()
        screen.draw.text(
            self.username,
            (self.pixel_x, self.pixel_y - 10),
            fontsize=14,
            color="white",
        )
