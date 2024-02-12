import pygame
from dataclasses import dataclass
from collections.abc import Callable, Sequence, Iterable, MutableSequence, Mapping, MutableMapping, Hashable
from typing import ClassVar, Protocol, runtime_checkable
pygame.font.init()

T_COLOR = Sequence[int, int, int] | Sequence[int, int, int, int]

@runtime_checkable
class DisplayObject(Protocol):
    def render(self, display) -> None: ...

class Placement:
    CENTER: int = 0
    LEFT: int = 1
    RIGHT: int = 2
    TOP: int = 3
    BOTTOM: int = 4
    LEFT_OUT: int = 5
    RIGHT_OUT: int = 6
    TOP_OUT: int = 7
    BOTTOM_OUT: int = 8
    TOP_LEFT: int = 9
    TOP_RIGHT: int = 10
    BOTTOM_LEFT: int = 11
    BOTTOM_RIGHT: int = 12

    _indicies = list(range(13))

    @classmethod
    def real_placement(cls, placement: int) -> bool:
        return placement in cls._indicies

    @classmethod
    def double_placement(cls, placement: int) -> bool:
        if not cls.real_placement(placement):
            return ValueError('Not a valid Placement')

        return placement in (cls.TOP_LEFT, cls.TOP_RIGHT, cls.BOTTOM_LEFT, cls.BOTTOM_RIGHT, cls.CENTER)

    @classmethod
    def split(cls, placement: int) -> int | tuple[int, int]:
        if not cls.real_placement(placement):
            return ValueError('Not a valid Placement')

        if not cls.double_placement(placement):
            return placement
        else:
            if placement == cls.CENTER:
                return cls.CENTER, cls.CENTER

            if placement in (cls.TOP_LEFT, cls.TOP_RIGHT):
                vert_direction = cls.TOP
            else:
                vert_direction = cls.BOTTOM

            if placement in (cls.TOP_LEFT, cls.BOTTOM_LEFT):
                hor_direction = cls.LEFT
            else:
                hor_direction = cls.RIGHT

            return hor_direction, vert_direction

class Frame:
    _frame: int = 0

    @classmethod
    def increase(cls, amount: int = 1) -> int:
        if isinstance(amount, int):
            cls._frame += amount
            return cls._frame
        else:
            return NotImplemented("Frame can only increase using intergers")

    @classmethod
    def set(cls, amount: int = 0) -> int:
        if isinstance(amount, int):
            cls._frame = amount
            return cls._frame
        else:
            return NotImplemented("Frame can only be set to an integer")

    @classmethod
    def get(cls) -> int:
        return cls._frame

    @classmethod
    def get_delta(cls, value: int) -> int:
        if not isinstance(value, int):
            return NotImplemented
        return cls.get() - value

    def __repr__(self) -> str:
        return f'Frame: {Frame.get()}'

class Display:
    CLOCK = pygame.time.Clock()
    fps: ClassVar[int] = 60
    _win: None = None

    def __init__(self, size: tuple[int, int], title: str | None = None, *args) -> None:
        self.size = size
        self.title = title
        self.flags = args

        self.display = pygame.display.set_mode(self.size, *self.flags)
        pygame.display.set_caption(self.title)

        Display._win = self.display

    @property
    def width(self) -> int:
        return self.display.get_width()

    @property
    def height(self) -> int:
        return self.display.get_height()

    def fill(self, color: T_COLOR) -> None:
        self.display.fill(color)

    def update(self) -> None:
        pygame.display.update()

    @classmethod
    def tick_frame(cls, increase_frame: int = 1):
        cls.CLOCK.tick(cls.fps)
        Frame.increase(increase_frame)

@dataclass(kw_only=True)
class Shape:
    color: T_COLOR = (0, 0, 0)
    border: int = 0

    def __repr__(self) -> str:
        return f'Shape: {self.color}'

@dataclass
class Rect(Shape):
    _corner_placement_names: ClassVar[dict[int, str]] = {
        Placement.TOP_LEFT: 'border_top_left_radius',
        Placement.TOP_RIGHT: 'border_top_right_radius',
        Placement.BOTTOM_LEFT: 'border_bottom_left_radius',
        Placement.BOTTOM_RIGHT: 'border_bottom_right_radius'
    }
    _rect: ClassVar[None] = None
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    corner_radius_all: int = 0
    corner_radius_specific: dict[int, int] | None = None

    def __post_init__(self) -> None:
        self._rect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def rect(self) -> pygame.Rect:
        return self._rect

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key in ['x', 'y', 'width', 'height'] and self._rect is not None:
            self._rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        if self.corner_radius_specific is None:
            pygame.draw.rect(display, self.color, self.rect, self.border, self.corner_radius_all)
        else:
            corner_radius = {Rect._corner_placement_names[key]: value for key, value in
                             self.corner_radius_specific.items()}
            pygame.draw.rect(display, self.color, self.rect, self.border, self.corner_radius_all,
                             **corner_radius)

    def __repr__(self) -> str:
        return f'Rect: ({self.x}, {self.y}) - ({self.width}, {self.height})'

@dataclass
class Circle(Shape):
    _corner_placement_names: ClassVar[dict[int, str]] = {
        Placement.TOP_LEFT: 'draw_top_left',
        Placement.TOP_RIGHT: 'draw_top_right',
        Placement.BOTTOM_LEFT: 'draw_bottom_left',
        Placement.BOTTOM_RIGHT: 'draw_bottom_right'
    }
    corner_base_dict: ClassVar[dict[int, bool]] = {Placement.TOP_LEFT: True, Placement.TOP_RIGHT: True,
                                                         Placement.BOTTOM_LEFT: True, Placement.BOTTOM_RIGHT: True}
    _circle: ClassVar[None] = None
    x: int = 0
    y: int = 0
    _radius: int = 0
    remove_corner_specific: dict[int, bool] | None = None

    def __post_init__(self):
        self._circle: Sequence[int, int, int] = (self.x, self.y, self._radius)

    @property
    def circle(self) -> tuple[int, int, int]:
        return self._circle

    @property
    def center(self) -> tuple[int, int]:
        return tuple(self.circle[:2])

    @property
    def radius(self) -> int:
        return self.circle[2]

    @radius.setter
    def radius(self, value: object) -> None:
        if isinstance(value, int | float):
            self._radius = value
        else:
            return NotImplemented

    @property
    def diameter(self) -> int:
        return self.radius * 2

    @diameter.setter
    def diameter(self, value: object) -> None:
        if isinstance(value, int | float):
            self.radius = 0.5 * value

    @property
    def width(self) -> int:
        return self.diameter

    @width.setter
    def width(self, value: object) -> None:
        self.diameter = value

    @property
    def height(self) -> int:
        return self.diameter

    @height.setter
    def height(self, value: object) -> None:
        self.diameter = value

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key in ['x', 'y', '_radius'] and self._circle is not None:
            self._circle = (self.x, self.y, self._radius)

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        if self.remove_corner_specific is None:
            pygame.draw.circle(display, self.color, self.center, self.radius, self.border)
        else:
            draw_corners = Circle.corner_base_dict.copy()
            draw_corners.update(self.remove_corner_specific)
            draw_corners_strings = {Circle._corner_placement_names[key]: value for key, value in draw_corners.items()}
            pygame.draw.circle(display, self.color, self.center, self.radius, self.border,
                             **draw_corners_strings)

    def __repr__(self) -> str:
        return f'Circle: ({self.center}) - ({self.radius})'

@dataclass
class Polygon(Shape):
    polygon_points: MutableSequence[Sequence[int, int], Sequence[int, int], Sequence[int, int], ...] | None \
        = None

    def __post_init__(self) -> None:
        self.polygon_points = self.polygon_points if self.polygon_points is not None else [(0, 0), (0, 0), (0, 0)]

    def insert_point(self, coordinate: Sequence[int, int], point_index: int = -1) -> None:
        if not isinstance(self.polygon_points, MutableSequence):
            raise TypeError('Polygon point insertion only possible on MutableSequence')
        elif not isinstance(coordinate, Sequence):
            raise TypeError('Polygon points must be Sequence[int, int] type')

        if coordinate not in self.polygon_points:
            self.polygon_points.insert(point_index, coordinate)

    def remove_point(self, coordinate: Sequence[int, int] = (0, 0)) -> int | None:
        if not isinstance(self.polygon_points, MutableSequence):
            raise TypeError('Polygon point removal only possible on MutableSequence')
        if not isinstance(coordinate, Sequence):
            raise TypeError('Polygon points must be Sequence[int, int] type')

        if coordinate in self.polygon_points:
            point_index = self.polygon_points.index(coordinate)
            self.polygon_points.remove(coordinate)
            return point_index
        else:
            return

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        pygame.draw.polygon(display, self.color, self.polygon_points, self.border)

    def __repr__(self) -> str:
        return f'Polygon: ({len(self.polygon_points)} - {self.polygon_points})'

@dataclass
class Ellipse(Shape):
    _ellipse: ClassVar[None] = None
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0

    def __post_init__(self) -> None:
        self._ellipse: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def ellipse(self) -> pygame.Rect:
        return self._ellipse

    def __setattr__(self, key, value) -> None:
        super().__setattr__(key, value)
        if key in ['x', 'y', 'width', 'height'] and self._ellipse is not None:
            self._ellipse = pygame.Rect(self.x, self.y, self.width, self.height)

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        pygame.draw.ellipse(display, self.color, self.ellipse, self.border)

    def __repr__(self) -> str:
        return f'Ellipse: ({self.x}, {self.y}) - ({self.width}, {self.height})'

@dataclass
class Text:
    text: str = ''
    x: int = 0
    y: int = 0
    color: T_COLOR = (0, 0, 0)
    font: str = 'helvetica'
    font_size: int | None = None
    bold: bool = False
    italic: bool = False
    alignment: int = Placement.CENTER
    _text_font_processed: int | None = None
    resize_max_width: int | None = None
    resize_max_height: int | None = None
    margin: int = 20
    dynamic_multi_line: bool = False
    multi_line_splitted: MutableSequence[str, ...] | None = None

    multi_line_height_factor: ClassVar[int] = 0.75
    multi_line_spacing_factor: ClassVar[int] = 1.4

    def __post_init__(self) -> None:
        if self.dynamic_multi_line:
            if None in [self.resize_max_width, self.resize_max_height]:
                raise ValueError('Provide resize_max_width and resize_max_height arguments to use dynamic multilines')

            self.multi_line_splitted = []
            lines = self.text.splitlines(False)

            longest_line = max(lines, key=lambda  text: len(text))
            test_for_resize = Text(longest_line, font=self.font, bold=self.bold, italic=self.italic,
                                   resize_max_width=self.resize_max_width, resize_max_height=self.resize_max_height,
                                   margin=self.margin)
            max_font_size = min(test_for_resize.font_size,
                                int(self.resize_max_height / len(lines) * Text.multi_line_height_factor))
            line_size = int(max_font_size * Text.multi_line_spacing_factor)

            for n_line, line in enumerate(lines):
                line_text_obj = Text(line, self.x, self.y + n_line * line_size, self.color, self.font, bold=self.bold,
                                     italic=self.italic, alignment=self.alignment, font_size=max_font_size,
                                     margin=self.margin)
                self.multi_line_splitted.append(line_text_obj)

        else:
            if self.font_size is None:
                self.font_size = 300
                self.update_font()
                self.auto_size_font()
            self.update_font()

    def auto_size_font(self, resize: bool = True) -> int:
        temp_text = self._text_font_processed.render(self.text, True, self.color)

        size_factor_w = size_factor_h = 1
        if self.resize_max_width is not None and temp_text.get_width() != 0:
            size_factor_w = (self.resize_max_width - self.margin) / temp_text.get_width()
        if self.resize_max_height is not None and temp_text.get_height() != 0:
            size_factor_h = (self.resize_max_height - self.margin) / temp_text.get_height()

        font_size = int(self.font_size * min(size_factor_w, size_factor_h))
        if resize:
            self.font_size = font_size
            self.update_font()
        return font_size

    def update_font(self) -> None:
        self._text_font_processed = pygame.font.SysFont(self.font, self.font_size, self.bold, self.italic)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: object) -> None:
        if isinstance(value, str):
            self._text = value

            if self.resize_max_width is not None or self.resize_max_height is not None:
                self.auto_size_font()
        else:
            raise NotImplemented

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        if self.dynamic_multi_line:
            for text_obj in self.multi_line_splitted:
                text_obj.render(display)

        else:
            text_render = self._text_font_processed.render(self.text, True, self.color)

            text_y = self.y - text_render.get_height() // 2

            if Placement.double_placement(self.alignment):
                x_align, y_align = Placement.split(self.alignment)

                if y_align == Placement.CENTER:
                    text_y = self.y - (text_render.get_height() - self.margin) // 2
                elif y_align == Placement.TOP:
                    text_y = self.y + self.margin // 2
                elif y_align == Placement.BOTTOM:
                    text_y = self.y - (text_render.get_height() - self.margin) // 2
                else:
                    return NotImplemented("Unusable text alignment")
            else:
                x_align = self.alignment

            if x_align == Placement.CENTER:
                text_x = self.x - (text_render.get_width() - self.margin) // 2
            elif x_align == Placement.LEFT:
                text_x = self.x + self.margin // 2
            elif x_align == Placement.RIGHT:
                text_x = self.x - (text_render.get_width() - self.margin) // 2
            else:
                return NotImplemented("Unusable text alignment")


            display.blit(text_render, (text_x, text_y))

    def __repr__(self):
        return f'"{self.text}", ({self.x}, {self.y}), {self.color}, size={self.font_size}'

@dataclass
class InputField:
    active_input: ClassVar[None] = None
    rect_not_active_color: ClassVar[T_COLOR | None] = None

    input_rect: Sequence[int, int, int, int, T_COLOR] | Rect = (0, 0, 0, 0, (0, 0, 0))
    rect_active_color: T_COLOR | None = None

    _text: Text | None = None
    _empty_text: Text | None = None
    replace_text_char: str | None = True
    _hidden_text: str = ''

    character_max: int | None = None
    restricted_characters: str = ''
    allow_letters: bool = False
    allow_numbers: bool = False
    allow_special: str = ''

    exit_esc: bool = True
    submit_return: bool = True
    clear_on_submit: bool = True
    can_del: bool = True
    select_on_init: bool = False

    def __post_init__(self) -> None:
        if isinstance(self.input_rect, Sequence):
            self.input_rect = Rect(*self.input_rect[:4], color=self.input_rect[4])

        self.rect_not_active_color = self.input_rect.color
        if self.select_on_init and self.rect_active_color is not None:
            self.input_rect.color = self.rect_active_color

        if self.select_on_init:
            InputBox.active_input = self

    @property
    def text(self) -> str:
        return self._text.text

    @text.setter
    def text(self, value) -> None:
        if isinstance(value, str):
            if self.replace_text_char:
                self._text.text = len(value) * self.replace_text_char
                self._hidden_text = value
            else:
                self._text.text = value
        else:
            return NotImplemented

    @property
    def text_raw(self) -> Text:
        return self._text

    @text_raw.setter
    def text_raw(self, value) -> None:
        if isinstance(value, Text):
            self._text = value
        else:
            return NotImplemented

    @property
    def text_hidden(self) -> str:
        if self.replace_text_char:
            return self._hidden_text
        else:
            return self.text

    @property
    def empty_text(self) -> Text:
        return self._empty_text.text

    @empty_text.setter
    def empty_text(self, value) -> None:
        if isinstance(value, str):
            self._empty_text.text = value
        else:
            return NotImplemented

    @property
    def empty_text_raw(self) -> Text:
        return self._empty_text

    @empty_text_raw.setter
    def empty_text_raw(self, value) -> None:
        if isinstance(value, Text):
            self._empty_text = value
        else:
            return NotImplemented

    @property
    def rect_color(self) -> T_COLOR:
        return self._rect_color

    def is_allowed(self, char: str) -> bool:
        if char in self.restricted_characters:
            return False
        if not self.allow_numeric and not self.allow_letters and self.allow_special == '':
            return True

        if self.allow_numeric and char.isnumeric():
            return True
        if self.allow_letters and char.isalpha():
            return True
        if char in self.allow_special:
            return True
        return False

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        self.input_rect.render(display)

        text_x, text_y = self.input_rect.x, self.input_rect.y + self.input_rect.height // 2
        if self.text == '' and not self == InputField.active_input:
            self.empty_text_raw.x, self.empty_text_raw.y = text_x, text_y
            self.empty_text_raw.render(display)
        else:
            self.text_raw.x, self.text_raw.y = text_x, text_y
            self.text_raw.render(display)

    @classmethod
    def activate(cls, field) -> None:
        if cls.active_input is not None:
            cls.active_input.input_rect.color = field.rect_not_active_color

        cls.active_input = field
        if field is not None and field.rect_active_color is not None:
            field.input_rect.color = field.rect_active_color

    def activate(self) -> None:
        InputField.activate(self)

    @classmethod
    def deactivate(cls) -> None:
        if cls.active_input is not None:
            cls.active_input.input_rect.color = cls.active_input.rect_not_active_color
            cls.active_input = None

    @classmethod
    def process_input(cls, event) -> None | str:
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_BACKSPACE):
            if event.key == pygame.K_ESCAPE and cls.active_input.exit_esc:
                cls.deactivate()
                return

            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                return_text = None

                if cls.active_input.submit_return:
                    return_text = cls.active_input.text_hidden

                if cls.active_input.clear_on_submit:
                    cls.active_input.text = ''

                return return_text

            elif event.key == pygame.K_BACKSPACE and cls.active_input.can_del:
                if len(cls.active_input.text) >= 1:
                    cls.active_input.text = cls.active_input.text[:-1]
                return

        elif len(cls.active_input.text) < cls.active_input.character_max and \
                cls.active_input.is_allowed(event.unicode):
            cls.active_input.text += event.unicode
            return

        print(f'Input processing is not implemented for {event.unicode}')
        return

    def __repr__(self) -> str:
        return f'pos: ({self.x}, {self.y}) - text: {self.text}'

@dataclass
class Image:
    assests_folder_path: ClassVar[str | None] = None
    image: ClassVar[None] = None

    _path: str = ''
    x: int = 0
    y: int = 0
    resize: Sequence[int, int] | None = None

    alpha: T_COLOR | None = None
    hide: bool = False
    direct_path: bool = False

    border: int = 0
    border_color: T_COLOR = (0, 0, 0)

    def __post_init__(self) -> None:
        self.image = pygame.image.load(self.path)

        if self.resize is not None:
            self.image.resize(self.resize)

        self.set_border()

    @property
    def width(self) -> int:
        if self.image is not None:
            return self.image.get_width()

    @width.setter
    def width(self, value) -> None:
        if isinstance(value, int) and self.image is not None:
            self.image.width = value

    @property
    def height(self) -> int:
        if self.image is not None:
            return self.image.get_height()

    @height.setter
    def height(self, value) -> None:
        if isinstance(value, int) and self.image is not None:
            self.image.height = value

    @property
    def path(self) -> str:
        if Image.assests_folder_path is not None and not self.direct_path:
            if Image.assests_folder_path[-1] != '\\':
                return Image.assests_folder_path + '\\' + self._path
            else:
                return Image.assests_folder_path + self._path
        else:
            return self._path

    def set_border(self) -> None:
        if self.border > 0:
            self.border_rect = Rect(self.x - self.border, self.y - self.border, self.width + 2 * self.border,
                                    self.height + 2 * self.border, color=self.border_color, border=self.border)

    def resize(self, size: Sequence[int | None, int | None] | None = None) -> None:
        size = size if size is not None else self.resize

        if None not in size:
            size = (max(0, size[0]), max(0, size[1]))
            self.image = pygame.transform.scale(self.image, size)
        elif size[1] is None:
            factor = size[0] / self.width
            self.image = pygame.transform.scale_by(self.image, factor)
        elif size[0] is None:
            factor = size[1] / self.height
            self.image = pygame.transform.scale_by(self.image, factor)

        self.set_border()

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        if not self.hide:
            display.blit(self.image, (self.x, self.y))
            if self.border > 0:
                self.border_rect.render(display)

    def __repr__(self) -> str:
        return f'pos: ({self.x}, {self.y}) - hidden: {self.hide} - src: {self.path}'


class ObjectAnimation:
    @dataclass
    class Action:
        display_fps: ClassVar[int] = Display.fps if Display.fps is not None else 60

        SCALE: int = 0
        SCALE_TO: int = 1
        MOVE: int = 2
        MOVE_TO: int = 3
        CHANGE_CORNER_RADIUS: int = 4
        CHANGE_CORNER_RADIUS_TO: int = 5
        CHANGE_OBJECT: int = 6

        @staticmethod
        def execute(objects, index, start_time, action: int = None, **kwargs):
            wait_time = 0
            object_index = None
            cur_object = objects[index]

            if action is None:
                return wait_time, object_index

            if 'time' in kwargs.keys():
                wait_time = kwargs['time']
                time_left = start_time + wait_time - Frame.get()
                transform_factor = max(time_left, 1)
            else:
                transform_factor = 1

            if action == Action.SCALE:
                if 'width' in kwargs.keys():
                    step_size = kwargs['width'] // transform_factor
                    cur_object.width += step_size
                if 'height' in kwargs.keys():
                    step_size = kwargs['height'] // transform_factor
                    cur_object.height += step_size

                if 'width' not in kwargs.keys() and 'height' not in kwargs.keys():
                    raise KeyError('width and/or height key should be given to use SCALE action')

            elif action == Action.SCALE_TO:
                if 'width' in kwargs.keys():
                    delta_w = cur_object.width - kwargs['width']
                    step_size = delta_w // transform_factor
                    cur_object.width += step_size
                if 'height' in kwargs.keys():
                    delta_h = cur_object.height - kwargs['height']
                    step_size = delta_h // transform_factor
                    cur_object.height += step_size

                if 'width' not in kwargs.keys() and 'height' not in kwargs.keys():
                    raise KeyError('width and/or height key should be given to use SCALE_TO action')

            elif action == Action.MOVE:
                if 'x' in kwargs.keys():
                    step_size = kwargs['x'] // transform_factor
                    cur_object.x += step_size
                if 'y' in kwargs.keys():
                    step_size = kwargs['y'] // transform_factor
                    cur_object.y += step_size

                if 'x' not in kwargs.keys() and 'y' not in kwargs.keys():
                    raise KeyError('x and/or y key should be given to use MOVE action')

            elif action == Action.MOVE_TO:
                if 'x' in kwargs.keys():
                    delta_x = cur_object.x - kwargs['x']
                    step_size = delta_x // transform_factor
                    cur_object.x += step_size
                if 'y' in kwargs.keys():
                    delta_y = cur_object.y - kwargs['y']
                    step_size = delta_y // transform_factor
                    cur_object.y += step_size

                if 'x' not in kwargs.keys() and 'y' not in kwargs.keys():
                    raise KeyError('x and/or y key should be given to use MOVE_TO action')

            elif action == Action.CHANGE_CORNER_RADIUS:
                if 'radius' in kwargs.keys():
                    step_size = kwargs['radius'] // transform_factor
                    cur_object.corner_radius_all += step_size
                else:
                    raise KeyError('radius key should be given to use CHANGE_CORNER_RADIUS action')

            elif action == Action.CHANGE_CORNER_RADIUS_TO:
                if 'radius' in kwargs.keys():
                    delta_r = cur_object.corner_radius_all - kwargs['radius']
                    step_size = delta_r // transform_factor
                    cur_object.corner_radius_all += step_size
                else:
                    raise KeyError('radius key should be given to use CHANGE_CORNER_RADIUS_TO action')

            elif action == Action.CHANGE_OBJECT:
                try:
                    object_index = kwargs['index']

                    if cur_object.trace:
                        objects[object_index].width = cur_object.width
                        objects[object_index].height = cur_object.height

                except KeyError:
                    raise KeyError('index key should be given to use CHANGE_OBJECT action')

            return wait_time, object_index


    running_animations: MutableSequence = []

    def __init__(self, action_sequence: MutableSequence[Sequence[int, dict[str, int]]],
                 animation_objects: Sequence, trace_objects: bool = True):
        self.action_sequence = action_sequence
        self.animation_objects = animation_objects
        self._start_object_setting = animation_objects.copy()
        self.trace = trace_objects
        self.action_index = 0
        self.object_index = 0
        self.start_action_frame = 0
        self.next_frame = 0

    def start(self):
        if self not in ObjectAnimation.running_animations:
            ObjectAnimation.running_animations.append(self)

    def stop(self):
        if self in ObjectAnimation.running_animations:
            ObjectAnimation.running_animations.remove(self)

    def reset(self):
        self.stop()
        self.action_index = 0
        self.object_index = 0
        self.start_action_frame = 0
        self.next_frame = 0
        self.animation_objects = self._start_object_setting.copy()

    def render(self):
        self.animation_objects[self.object_index].render()

    def process_animation(self):
        current_action = self.action_sequence[self.action_index]
        wait_time, object_index = Action.execute(self.animation_objects, self.object_index, self.start_action_frame,
                                                 current_action[0], **current_action[1])

        if object_index is not None:
            self.object_index = object_index

        if Frame.get() >= self.next_frame:
            self.start_action_frame = Frame.get()
            self.next_frame = self.start_action_frame + wait_time
            self.action_index += 1

            if self.action_index > len(self.action_sequence):
                self.stop()
                return

            if wait_time <= 0:
                self.process_animation()

    @classmethod
    def update_animations(cls):
        for animation in cls.running_animations:
            animation.process_animation()


@dataclass
class Transition:
    display_fps: ClassVar[int] = Display.fps if Display.fps is not None else 60
    running_animations: ClassVar[list] = []

    base_size: Sequence[int, int] = (0, 0)
    current_size: Sequence[int, int] = (0, 0)
    x_range: Sequence[int, int] = (0, 0)
    y_range: Sequence[int, int] = (0, 0)

    color: T_COLOR = (0, 0, 0)
    image: Image | None = None

    time_to_use: float = 1.0
    starting_frame: int = Frame.get()

    post_transition_call: Callable | None = None
    post_transition_call_kwargs: dict | None = None

    def __post_init__(self) -> None:
        if self.post_transition_call_kwargs is None:
            self.post_transition_call_kwargs = {}

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        if self in Transition.running_animations:
            if self.image is not None:
                self.image.x = self.x_range[0]
                self.image.y = self.y_range[0]
                self.image.resize(self.current_size)
                self.image.render(display)
            else:
                transition_rect = pygame.Rect(self.x_range[0], self.y_range[0], *self.current_size)
                pygame.draw.rect(display, self.color, transition_rect)

    def start_transition(self, **kwargs) -> None:
        if self.post_transition_call is not None:
            self.post_transition_call_kwargs.update(**kwargs)

        self.starting_frame = Frame.get()
        Transition.running_animations.append(self)

    def process_transition(self) -> None:
        transition_fraction = (Frame.get() - self.starting_frame) / self.time_to_use * self.display_fps

        self.current_size[0] = min(max(self.base_size[0], int((self.x_range[1] - self.x_range[0]) * transition_fraction)
                                       ), self.x_range[1] - self.x_range[0])
        self.current_size[1] = min(max(self.base_size[1], int((self.y_range[1] - self.y_range[0]) * transition_fraction)
                                       ), self.y_range[1] - self.y_range[0])

        if self.current_size[0] == self.x_range[1] - self.x_range[0] and \
                self.current_size[1] == self.y_range[1] - self.y_range[0]:
            Transition.running_animations.remove(self)
            if self.post_transition_call is not None:
                self.post_transition_call(self.post_transition_call_kwargs)

    @classmethod
    def process_running_transitions(cls) -> None:
        for transition in cls.running_animations:
            transition.process_transition()

    def __repr__(self) -> str:
        return f'running: {self in Transition.running_animations}'

@dataclass
class Button:
    BUTTON_TYPES: ClassVar[tuple[str, ...]] = ('switch', 'push')

    active_buttons: ClassVar[list] = []

    rect: Sequence[int, int, int, int, T_COLOR] | Rect = (0, 0, 0, 0, (0, 0, 0))
    pressed_color: T_COLOR | None = None

    _text: Text | None = None
    img: Image | None = None
    img_margin: int = 0
    img_fill_button: bool = True
    img_alignment: int = Placement.CENTER

    button_pressed: bool = False
    button_type: str = 'switch'
    target_scene_on_press: str | None = None
    call_on_press: Callable | None = None
    call_on_press_kwargs: dict | None = None

    def __post_init__(self) -> None:
        if isinstance(self.rect, Sequence):
            self.rect = Rect(*self.rect[:4], color=self.rect[4])

        self.not_pressed_color = self.rect.color
        if self.pressed_color is not None:
            self.rect.color = self.pressed_color

        if self.img is not None:
            if self.img_fill_button:
                self.img.resize((self.rect.width - 2 * self.img_margin, self.rect.height - 2 * self.img_margin))

            else:
                if self.img_alignment in (Placement.LEFT, Placement.TOP_LEFT, Placement.BOTTOM_LEFT):
                    self.img.x = self.rect.x + self.img_margin
                elif self.img_alignment in (Placement.RIGHT, Placement.TOP_RIGHT, Placement.BOTTOM_RIGHT):
                    self.img.x = self.rect.x + self.rect.width - self.img.width - self.img_margin
                else:
                    self.img.x = self.rect.x + (self.rect.width - self.img.width) // 2

                if self.img_alignment in (Placement.TOP, Placement.TOP_LEFT, Placement.TOP_RIGHT):
                    self.img.y = self.rect.y + self.img_margin
                elif self.img_alignment in (Placement.BOTTOM, Placement.BOTTOM_LEFT, Placement.BOTTOM_RIGHT):
                    self.img.y = self.rect.y + self.rect.width - self.img.width - self.img_margin
                else:
                    self.img_y = self.rect.y + (self.rect.width - self.img.width) // 2

        if self.post_transition_call_kwargs is None:
            self.post_transition_call_kwargs = {}

    @property
    def text(self) -> str:
        return self._text.text

    @text.setter
    def text(self, value) -> None:
        if isinstance(value, str):
            self._text.text = value
        else:
            return NotImplemented

    @property
    def text_raw(self) -> Text:
        return self._text

    @text_raw.setter
    def text_raw(self, value) -> None:
        if isinstance(value, Text):
            self._text = value
        else:
            return NotImplemented

    def call_func(self, **kwargs) -> None:
        if self.call_on_press is not None:
            self.call_on_press_kwargs.update(**kwargs)
            self.call_on_press(**self.call_on_press_kwargs)

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        self.rect.render(display)
        self.img.render(display)
        self.text.render(display)

    def check_collision(self, event_pos, **func_kwargs) -> bool:
        if self.rect.rect.collidepoint(event_pos):
            self.button_pressed = not self.button_pressed
            self.call_func(**func_kwargs)

            return True
        return False

    @classmethod
    def release_push_buttons(cls) -> None:
        for button in cls.active_buttons:
            if button.type == 'push' and button.pressed is True:
                button.pressed = False

    def __repr__(self) -> str:
        return f'Button: ({self.rect.x}, {self.rect.y}) - target: {self.target_scene_on_press}'

@dataclass
class Bar:
    display_fps: ClassVar[int] = Display.fps if Display.fps is not None else 60
    moving_bars: ClassVar[dict[int, list[list[float, float], bool]]] = {}
    bar_id_counter: ClassVar[int] = 0
    save_bars: ClassVar[list] = []

    rect: Sequence[int, int, int, int, T_COLOR] | Rect = (0, 0, 0, 0, (0, 0, 0))
    value_range: Sequence[float, float] = (0.0, 100.0)
    display_range: MutableSequence[float] | None = None

    bar_color: T_COLOR = (0, 0, 0)
    _text: Text | None = None
    bar_bg_img: Image | None = None

    bar_closed: bool = False

    start_fill_side: int = Placement.LEFT
    time_to_use: float = 3.0
    starting_frame: int = Frame.get()

    _bar_id = bar_id_counter

    def __post_init__(self) -> None:
        Bar.bar_id_counter += 1
        Bar.save_bars.append(self)

        if isinstance(self.rect, Sequence):
            self.rect = Rect(*self.rect[:4], color=self.rect[4])

        if self.display_range is None:
            self.display_range = list(self.value_range)
            print(self.display_range)

        if self.start_fill_side not in (Placement.LEFT, Placement.BOTTOM):
            self.start_fill_side = Placement.LEFT

        if self.bar_bg_img is not None:
            self.bar_bg_img.x, self.bar_bg_img.y = self.rect.x + self.rect.border, self.rect.y + self.rect.border

    @property
    def text(self) -> str:
        return self._text.text

    @text.setter
    def text(self, value: object) -> None:
        if isinstance(value, str):
            self._text.text = value
        else:
            return NotImplemented

    @property
    def text_raw(self) -> Text:
        return self._text

    @text_raw.setter
    def text_raw(self, value: object) -> None:
        if isinstance(value, Text):
            self._text = value
        else:
            return NotImplemented

    @property
    def value(self) -> float:
        return self.display_range[1]

    @property
    def target_range(self) -> list[list[float, float], bool]:
        if self._bar_id in Bar.moving_bars.keys():
            return [Bar.moving_bars[self._bar_id][0], True]
        return [self.display_range, False]

    def set_value(self, value: float, set_instant: bool = False, set_bottom: bool = False) -> None:
        set_value = min(max(value, self.value_range[0]), self.value_range[1])
        if self._bar_id in Bar.moving_bars.keys():
            current_goal = Bar.moving_bars[self._bar_id][0]
        else:
            current_goal = self.display_range

        if not set_bottom:
            if self.value != set_value:
                if not set_instant:
                    Bar.moving_bars.update({self._bar_id: [[current_goal[0], set_value], set_bottom]})
                    self.starting_frame = Frame.get()
                else:
                    self.display_range[1] = set_value
        else:
            if self.display_range[0] != set_value:
                if not set_instant:
                    Bar.moving_bars.update({self._bar_id: [[set_value, current_goal[1]], set_bottom]})
                    self.starting_frame = Frame.get()
                else:
                    self.display_range[0] = set_value

    def modify_value(self, value: float, set_instant: bool = False, set_bottom: bool = False) -> None:
        if self._bar_id not in Bar.moving_bars.keys():
            if not set_bottom:
                self.set_value(self.display_range[1] + value, set_instant, set_bottom)
            else:
                self.set_value(self.display_range[0] + value, set_instant, set_bottom)
        else:
            if not set_bottom:
                self.set_value(Bar.moving_bars[self._bar_id][0][1] + value, set_instant, set_bottom)
            else:
                self.set_value(Bar.moving_bars[self._bar_id][0][0] + value, set_instant, set_bottom)

    def set_percentage(self, percentage: float, set_instant: bool = False, set_bottom: bool = False) -> None:
        value_for_percent = percentage / 100 * self.value_range[1]
        self.set_value(value_for_percent, set_instant, set_bottom)

    def modify_percentage(self, percentage: float, set_instant: bool = False, set_bottom: bool = False) -> None:
        value_for_percent = percentage / 100 * self.value_range[1]
        self.modify_value(value_for_percent, set_instant, set_bottom)

    def get_bar_width(self, value: float) -> float:
        bg_width = self.rect.width - 2 * self.rect.border
        ratio_filled = value / self.value_range[1]
        return bg_width * ratio_filled

    def get_bar_height(self, value: float) -> float:
        bg_height = self.rect.height - 2 * self.rect.border
        ratio_filled = value / self.value_range[1]
        return bg_height * ratio_filled

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        self.rect.render(display)

        if self.bar_bg_img is not None:
            if self.start_fill_side == Placement.LEFT:
                self.bar_bg_img.x = self.display_range[0]
                self.bar_bg_img.resize(self.get_bar_width(self.display_range[1] - self.display_range[0]),
                                       self.rect.height - 2 * self.rect.border)
            else:
                self.bar_bg_img.y = self.display_range[0]
                self.bar_bg_img.resize(self.rect.width - 2 * self.rect.border,
                                       self.get_bar_height(self.display_range[1] - self.display_range[0]))
            self.bar_bg_img.render(display)
        else:
            if self.start_fill_side == Placement.LEFT:
                bar_rect = Rect(self.rect.x + self.rect.border + self.get_bar_width(self.display_range[0]),
                                self.rect.y + self.rect.border, self.get_bar_width(self.display_range[1]
                                                                                   - self.display_range[0]),
                                self.rect.height - 2 * self.rect.border, color=self.bar_color)
            else:
                bar_rect = Rect(self.rect.x + self.rect.border, self.rect.y + self.rect.height - self.rect.border
                                - self.get_bar_height(self.display_range[1] - self.display_range[0]),
                                self.rect.width - 2 * self.rect.border,
                                self.get_bar_height(self.display_range[1] - self.display_range[0]),
                                color=self.bar_color)
            bar_rect.render(display)

        if self.bar_closed:
            if self.value > self.value_range[0] + self.rect.border and self.value != self.value_range[1]:
                if self.start_fill_side == Placement.LEFT:
                    bar_close_block = Rect(self.rect.x + self.rect.border + self.get_bar_width(self.display_range[1]),
                                           self.rect.y + self.rect.border, self.rect.border, self.rect.height
                                           - 2 * self.rect.border, color=self.rect.color)
                else:
                    bar_close_block = Rect(self.rect.x + self.rect.border,
                                           self.rect.y + self.rect.border
                                           + self.get_bar_height(self.value_range[1] - self.display_range[1]),
                                           self.rect.width - self.rect.border, self.rect.border, color=self.rect.color)
                bar_close_block.render(display)

            if self.display_range[0] > self.value_range[0] + self.rect.border and \
                    self.display_range[0] != self.value_range[1]:
                if self.start_fill_side == Placement.LEFT:
                    bar_close_block = Rect(self.rect.x + self.get_bar_width(self.display_range[0])
                                           + self.rect.border, self.rect.y + self.rect.border, self.rect.border,
                                           self.rect.height - 2 * self.rect.border, color=self.rect.color)
                else:
                    bar_close_block = Rect(self.rect.x, self.rect.y + self.get_bar_height(self.value_range[1]
                                                                                         - self.value_range[0])
                                           - self.rect.border, self.rect.width, self.rect.border, color=self.rect.color)
                bar_close_block.render(display)

        if self.text_raw is not None:
            self.text_raw.render(display)

    def process_bar_movement(self) -> None:
        if self._bar_id in Bar.moving_bars.keys():
            if not Bar.moving_bars[self._bar_id][1]:
                target_value = Bar.moving_bars[self._bar_id][0][1]
            else:
                target_value = Bar.moving_bars[self._bar_id][0][0]

            if self.value == target_value:
                Bar.moving_bars.pop(self._bar_id)
            else:
                step_size = Frame.get_delta(self.starting_frame) / self.display_fps * self.time_to_use

                if not Bar.moving_bars[self._bar_id][1]:
                    d_value = self.value - target_value

                    if abs(d_value) < step_size:
                        self.display_range[1] = target_value
                    else:
                        if self.value < target_value:
                            self.display_range[1] += step_size
                        else:
                            self.display_range[1] -= step_size
                else:
                    d_value = self.display_range[0] - target_value

                    if abs(d_value) < step_size:
                        self.display_range[0] = target_value
                    else:
                        if self.display_range[0] < target_value:
                            self.display_range[0] += step_size
                        else:
                            self.display_range[0] -= step_size

    @classmethod
    def process_all_bar_movement(cls) -> None:
        moving_bars_ids = list(cls.moving_bars.keys())
        for bar_id in moving_bars_ids:
            Bar.save_bars[bar_id].process_bar_movement()

class Scene:
    current_scene: MutableSequence | None = []
    all_scenes: MutableSequence | None = []
    universal_objects: Sequence | None = []

    def __init__(self, name: str | None = None, bg_color: T_COLOR | None = (0, 0, 0),
                 objects: Iterable | MutableMapping | None = None) -> None:
        if name in [scene.name for scene in Scene.all_scenes]:
            raise ValueError('name already taken')
        else:
            self.name = name
        self.bg_color = bg_color
        self.objects = objects
        Scene.all_scenes.append(self)

    @property
    def objects_list(self) -> list:
        if isinstance(self.objects, Mapping):
            objects_list = self.objects.values()
        elif isinstance(Iterable):
            objects_list = self.objects
        else:
            return NotImplemented
        return objects_list

    def activate(self, deactivate_all: bool = True, order_index: int = -1) -> None:
        if deactivate_all:
            Scene.current_scene = [self]
        else:
            Scene.current_scene.insert(-1, self)

    def deactivate(self, deactivate_all: bool = False) -> None:
        if deactivate_all:
            Scene.current_scene = []
        else:
            if self in Scene.current_scene:
                Scene.current_scene.remove(self)

    def render(self, display: pygame.Surface | None = None) -> None:
        display = display if display is not None else Display._win
        if display is None:
            raise ValueError('Display argument missing')

        if self.bg_color is not None:
            display.fill(self.bg_color)

        render_objects = self.objects_list + Scene.universal_objects

        for obj in render_objects:
            if isinstance(obj, DisplayObject):
                obj.render(display)
            else:
                raise NotImplementedError('Cannot render objects which are not DisplayObject')

    def detect_object(self, obj: object) -> bool:
        return obj in self.objects_list

    def detect_object_key(self, obj: Hashable) -> bool:
        if isinstance(self.objects, Mapping):
            return obj in self.objects.keys()
        else:
            return NotImplemented

    @classmethod
    def find_scene(cls, name: str) -> 'Scene':
        for scene in cls.all_scenes:
            if name == scene.name:
                return scene
        return
