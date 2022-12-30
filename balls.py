from typing import List
import numpy
import pymunk

from camera import WIDTH, HEIGHT
from colors import get_rdcolor

BALL_RADIUS = 12


class balls(object):
    def __init__(self, space: pymunk.Space):
        self.shapes: List[pymunk.Circle] = []
        self.bodies: List[pymunk.Body] = []
        self.space = space

    def create(self, nums=1) -> None:
        for num, data in enumerate([(300 + numpy.random.uniform(-30, 30), -10) for _ in range(nums)]):
            body = pymunk.Body(100.0, 1666, body_type=pymunk.Body.DYNAMIC)
            body.velocity = 0, 500
            body.position = data
            shape = pymunk.Circle(body, BALL_RADIUS)
            shape.friction = 1
            shape.color = *get_rdcolor(), 0
            self.space.add(body, shape)
            self.shapes.append(shape)
            self.bodies.append(body)

    def detect(self):
        for body in self.bodies:
            x, y = body.position
            if x + BALL_RADIUS > WIDTH or y + BALL_RADIUS > HEIGHT:
                self.delete(body)

    def delete(self, body: pymunk.Body):
        if body in self.bodies:
            shape = self.shapes[self.bodies.index(body)]
            if body in self.space.bodies:
                self.space.remove(body, shape)
            self.bodies.remove(body)
            self.shapes.remove(shape)

    def update(self):
        self.detect()
        if numpy.random.uniform() > 0.94:
            self.create(numpy.random.randint(2, 5))
