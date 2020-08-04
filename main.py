import pygame
from collections import defaultdict

from tetris import Tetris, Faller

FAST_FALL_DELAY = 50  # ms between falls when holding down
MOVE_DELAY = 180  # ms between moves when holding left/right
STARTING_FALL_DELAY = 1000  # ms between falls


class GuiMain:
    """ the window and timing for the game """
    def __init__(self, game: Tetris):
        pygame.display.set_caption("tetris")
        self.screen = pygame.display.set_mode((700, 700), pygame.RESIZABLE)
        self.game = game
        self.running = False

        self.fps = 60
        self.keys = defaultdict(lambda: False)
        self.delay = STARTING_FALL_DELAY  # milliseconds between each down tick
        self.move_allowed_after = 0  # ms between moves left/right

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
                    self.move_allowed_after = \
                        pygame.time.get_ticks() + MOVE_DELAY * 2
                elif event.key == pygame.K_RIGHT:
                    self.game.move(1)
                    self.move_allowed_after = \
                        pygame.time.get_ticks() + MOVE_DELAY * 2
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

            now = pygame.time.get_ticks()
            ms_between_fall = FAST_FALL_DELAY if self.keys[pygame.K_DOWN] \
                else self.delay
            if now > last_fall + ms_between_fall:
                new_piece = self.game.fall()
                # pretend down key is released when making a new piece
                self.keys[pygame.K_DOWN] = \
                    self.keys[pygame.K_DOWN] and (not new_piece)
                # speed up every time a new piece enters
                self.delay = max(self.delay * (1 - int(new_piece)/100),
                                 FAST_FALL_DELAY)
                last_fall = now
            if now > self.move_allowed_after:
                if self.keys[pygame.K_LEFT]:
                    self.game.move(-1)
                    self.move_allowed_after = now + MOVE_DELAY
                if self.keys[pygame.K_RIGHT]:
                    self.game.move(1)
                    self.move_allowed_after = now + MOVE_DELAY

            self.process_events()

            self.screen.fill((180, 180, 160))

            self.draw()

            pygame.display.flip()

    def draw(self):
        block_w = 20

        """ draw field and faller on screen """
        for y, row in enumerate(self.game.grid.rows):
            for x, block in enumerate(row):
                pygame.draw.rect(self.screen,
                                 (36 * block,
                                  255 - (36 * block) if block else 0, 0),
                                 pygame.Rect(x * block_w + block_w,
                                             y * block_w + block_w,
                                             block_w - 1, block_w - 1))

        # faller
        if self.game.faller.shape != Faller.Shape.COUNT:
            for block in self.game.faller.get_blocks():
                x = self.game.faller.x + block[0]
                y = self.game.faller.y + block[1]
                color_base = self.game.faller.shape + 1
                pygame.draw.rect(self.screen,
                                 (36 * color_base, 255 - (36 * color_base), 0),
                                 pygame.Rect(x * block_w + block_w,
                                             y * block_w + block_w,
                                             block_w - 1, block_w - 1))

        # next piece
        for block in Faller.BLOCKS[self.game.next_shape][0]:
            x = self.game.grid.w + 1 + block[0]
            y = 1 + block[1]
            color_base = self.game.next_shape + 1
            pygame.draw.rect(self.screen,
                             (36 * color_base, 255 - (36 * color_base), 0),
                             pygame.Rect((x + 1.5) * block_w,
                                         y * block_w + block_w,
                                         block_w - 1, block_w - 1))


if __name__ == "__main__":
    pygame.init()
    t = GuiMain(Tetris())
    t.run()
    pygame.quit()
