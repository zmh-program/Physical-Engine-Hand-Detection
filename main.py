import balls
import mediapipe
import pygame
import sys
import pymunk.pygame_util
import hands
from camera import *

fps = 60
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
space = pymunk.Space()
space.gravity = 0, 500

options = pymunk.pygame_util.DrawOptions(screen)
clock = pygame.time.Clock()


def cvimage_to_pygame(image) -> pygame.Surface:
    """
    Convert cvimage into a pygame image
    -> Stack Overflow: `OpenCV cv2 image to PyGame image? `
    | https://stackoverflow.com/questions/19306211/opencv-cv2-image-to-pygame-image
    """
    return pygame.image.frombuffer(image.tobytes(), image.shape[1::-1], "RGB")


def terminate():
    capture.release()
    pygame.display.quit()
    sys.exit()


def read_capture():
    success, image = capture.read()
    if not success:
        terminate()
    image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
    return image


with mediapipe.solutions.hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hand_parser:
    _hands = hands.handsHandler(space, hand_parser, screen)
    _balls = balls.balls(space)
    while True:
        _balls.update()
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
        if cv2.waitKey(10) & 0xFF == 27:
            terminate()

        surf = read_capture()
        screen.blit(cvimage_to_pygame(surf), [0, 0])
        space.step(1 / fps)
        space.debug_draw(options)
        _hands.parser(surf)
        clock.tick(fps)

        pygame.display.update()
