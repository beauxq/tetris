import pygame

from tetris import Tetris, Faller


class GuiMain:
    def __init__(self, game: Tetris):
        pygame.display.set_caption("tetris")
        self.screen = pygame.display.set_mode((700, 700), pygame.RESIZABLE)
        self.game = game
        self.running = False

        self.fps = 60
        self.down_key = False

    def process_events(self):
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
                if event.key == pygame.K_LEFT:
                    self.game.move(-1)
                elif event.key == pygame.K_RIGHT:
                    self.game.move(1)
                elif event.key == pygame.K_DOWN:
                    self.down_key = True
                elif event.key == pygame.K_KP9:
                    self.game.rotate(1)
                elif event.key == pygame.K_KP6:
                    self.game.rotate(-1)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    self.down_key = False

    def run(self):
        self.running = True
        pygame_clock = pygame.time.Clock()
        last_fall = pygame.time.get_ticks()

        while self.running:
            pygame_clock.tick(self.fps)

            ms_between_fall = 100 if self.down_key else 1000
            if pygame.time.get_ticks() > last_fall + ms_between_fall:
                self.game.fall()
                last_fall = pygame.time.get_ticks()

            self.process_events()

            self.screen.fill((180, 180, 160))

            self.draw()

            pygame.display.flip()

    def draw(self):
        for y, row in enumerate(self.game.grid.rows):
            for x, block in enumerate(row):
                pygame.draw.rect(self.screen,
                                 (36 * block, 255 - (36 * block) if block else 0, 0),
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
