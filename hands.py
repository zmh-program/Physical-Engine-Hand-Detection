from typing import List
from camera import WIDTH, HEIGHT
import pygame
import pymunk

HAND_POINTS = 21
HAND_LINES = 21
MAX_USE_CACHE_TIMES = 0

HAND_SPEED = 50.
LINE_RADIUS = 3.
MARK_RADIUS = 8.


class handsHandler(object):
    def __init__(self, space: pymunk.Space, hand_paser, surface: pygame.Surface, debug=True):
        self.hands: List["hand"] = []
        self.space = space
        self._parser = hand_paser
        self.surface = surface
        self.debug = debug

    def create_new_hand(self, nums):
        [self.hands.append(hand(self.space, parent=self)) for _ in range(nums)]

    def convert_the_coordinates(self, image):
        image.flags.writeable = False
        resp = self._parser.process(image)
        image.flags.writeable = True
        multi_hand_landmarks = resp.multi_hand_landmarks
        return [[(int(hand_landmarks.landmark[idx].x * WIDTH), int(hand_landmarks.landmark[idx].y * HEIGHT))
                 for idx in range(HAND_POINTS)] for hand_landmarks in
                reversed(multi_hand_landmarks)] if multi_hand_landmarks else []

    def parser(self, image):
        landmarks = self.convert_the_coordinates(image)
        hands_number = len(landmarks)
        cmp_hand = hands_number - len(self.hands)
        if cmp_hand > 0:
            self.create_new_hand(cmp_hand)
        for _hand, _mark in zip(self.hands[:hands_number], landmarks):
            _hand.update(_mark)
        for _hand in self.hands[hands_number:]:
            _hand.update()

        if self.debug:
            self.debug_hands_lines()

    def debug_hands_lines(self):
        for _hand in self.hands:
            _hand.debug_hand_lines(self.surface)

        # for n, pos in enumerate(numbers):
        #     x, y = pos
        #     screen.blit(font.render(str(n), True, (255, 255, 255)), (x - 16, y - 16))


class hand(object):
    fingers_obj: List[pymunk.Body]
    fingers_shp: List[pymunk.Circle]
    hdlines_obj: List[pymunk.Body]
    hdlines_shp: List[pymunk.Segment]

    def __init__(self, space: pymunk.Space, parent: handsHandler = None):
        # pymunk AssertionError: The shape's body must be added to the space before (or at the same time) as the shape.
        self.cache = []
        self.use_cache_times = 0
        self.parent = parent
        self.space = space
        assert isinstance(parent, handsHandler)

        self.add()

    def create_ball_shape(self, finger: pymunk.Body) -> pymunk.Circle:
        shape = pymunk.Circle(finger, MARK_RADIUS)
        shape.friction = 1
        shape.elasticity = 0.7
        self.space.add(finger, shape)
        return shape

    def create_line_shape(self, line: pymunk.Body) -> pymunk.Segment:
        shape = pymunk.Segment(line, (0., 0.), (0., 0.), LINE_RADIUS)
        shape.friction = 1
        shape.elasticity = 0.7
        self.space.add(line, shape)
        return shape

    def add(self):
        self.fingers_obj = [pymunk.Body(10, 1666, body_type=pymunk.Body.KINEMATIC) for _ in range(HAND_POINTS)]
        self.fingers_shp = [self.create_ball_shape(finger) for finger in self.fingers_obj]
        self.hdlines_obj = [pymunk.Body(10, 1666, body_type=pymunk.Body.KINEMATIC) for _ in range(HAND_LINES)]
        self.hdlines_shp = [self.create_line_shape(line) for line in self.hdlines_obj]

    def remove(self):
        for body, shape in zip(self.fingers_obj, self.fingers_shp):
            self.space.remove(body, shape)
        for body, shape in zip(self.hdlines_obj, self.hdlines_shp):
            self.space.remove(body, shape)

        self.fingers_obj = []
        self.hdlines_obj = []
        self.fingers_shp = []
        self.hdlines_shp = []

    @staticmethod
    def as_bone_fingers(tensors):
        return [tensors[17]] + tensors[0:5], [tensors[2]] + tensors[5:9], [tensors[5]] + tensors[9:13], \
               [tensors[9]] + tensors[13:17], [tensors[13]] + tensors[17:21]

    @staticmethod
    def as_fingers(tensors):
        return tensors[0:5], tensors[5:9], tensors[9:13], tensors[13:17], tensors[17:21]

    @staticmethod
    def to_line_points(tensors):
        if len(tensors) < 2:
            return
        last = tensors[0]
        for n in tensors[1:]:
            yield last, n
            last = n

    def debug_hand_lines(self, surface: pygame.Surface):
        if self.cache:
            for body, shape, tensor in zip(self.hdlines_obj,
                                           self.hdlines_shp,
                                           [tensor for tensors in self.as_bone_fingers(self.cache)
                                            for tensor in self.to_line_points(tensors)]):
                # pygame.draw.line(surface, (255, 255, 255), *tensor, 5)
                shape.unsafe_set_endpoints(*tensor)

    def update(self, hand_landmarks=None):
        if hand_landmarks:
            if not self.cache:
                self.add()
            self.update_landmarks(hand_landmarks)
            self.cache = hand_landmarks
            self.use_cache_times = 0
        else:
            self.use_cache_times += 1
            if self.use_cache_times <= MAX_USE_CACHE_TIMES:
                self.update_landmarks(self.cache)
            elif self.cache:
                self.cache = []
                self.remove()
        return self.cache

    def update_landmarks(self, hand_landmarks):
        for landmark, finger in zip(hand_landmarks, self.fingers_obj):
            # converting the coordinates
            x, y = landmark
            # update the velocity
            finger.velocity = HAND_SPEED * (x - finger.position[0]), HAND_SPEED * (y - finger.position[1])
