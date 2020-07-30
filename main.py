import pygame
from collections import defaultdict

from tetris import Tetris, Faller


class GuiMain:
    """ the window and timing for the game """
    def __init__(self, game: Tetris):
        pygame.display.set_caption("tetris")
        self.screen = pygame.display.set_mode((700, 700), pygame.RESIZABLE)
        self.game = game
        self.running = False

        self.fps = 60
        self.keys = defaultdict(lambda: False)
        self.down_key = False
        self.delay = 1000  # milliseconds between each down tick

    def process_events(self):
        """ window events """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.VIDEORESIZE:
                # https://stackoverflow.com/questions/11603222/allowing-resizing-window-pygame
                old_surface_saved = self.screen
                self.screen = pygame.display.set_mode((event.w, event.h),
                                                      pygame.RESIZABLE)
                self.screen.blit(old_surface_saved, (0, 0))
                del old_surface_saved
                # note this pygame bug with resizing window:
                # https://github.com/pygame/pygame/issues/201
                # Resizing from the corner of the window doesn't work.
            if event.type == pygame.KEYDOWN:
                self.keys[event.key] = True
                if event.key == pygame.K_LEFT:
                    self.game.move(-1)
                elif event.key == pygame.K_RIGHT:
                    self.game.move(1)
                elif event.key == pygame.K_KP9:
                    self.game.rotate(1)
                elif event.key == pygame.K_KP6:
                    self.game.rotate(-1)
            elif event.type == pygame.KEYUP:
                self.keys[event.key] = False

    def run(self):
        """ main control loop """
        self.running = True
        pygame_clock = pygame.time.Clock()
        last_fall = pygame.time.get_ticks()

        while self.running:
            pygame_clock.tick(self.fps)

            ms_between_fall = 50 if self.keys[pygame.K_DOWN] else self.delay
            if pygame.time.get_ticks() > last_fall + ms_between_fall:
                new_piece = self.game.fall()
                # speed up every time a new piece enters
                self.delay = max(self.delay - int(new_piece), 50)
                last_fall = pygame.time.get_ticks()

            self.process_events()

            self.screen.fill((180, 180, 160))

            self.draw()

            pygame.display.flip()

    def draw(self):
        """ draw field and faller on screen """
        for y, row in enumerate(self.game.grid.rows):
            for x, block in enumerate(row):
                pygame.draw.rect(self.screen,
                                 (36 * block,
                                  255 - (36 * block) if block else 0, 0),
                                 pygame.Rect(x * 20 + 20, y * 20 + 20, 18, 18))

        # faller
        if self.game.faller.shape != Faller.Shape.COUNT:
            for block in self.game.faller.get_blocks():
                x = self.game.faller.x + block[0]
                y = self.game.faller.y + block[1]
                shape = self.game.faller.shape + 1
                pygame.draw.rect(self.screen,
                                 (36 * shape, 255 - (36 * shape), 0),
                                 pygame.Rect(x * 20 + 20, y * 20 + 20, 18, 18))


if __name__ == "__main__":
    pygame.init()
    t = GuiMain(Tetris())
    t.run()
    pygame.quit()
