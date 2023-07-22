import pygame
import sys
import random
from dataclasses import dataclass

pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 36)
pygame.mixer.init() 

WIDTH, HEIGHT = 800, 600
GROUND = HEIGHT - 50
WINSCORE = 10

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

@dataclass
class DifficultySettings:
    min_speed: int
    max_speed: int    
    min_height: int
    max_height: int
    frequency: int
    
DIFFICULTY_SETTINGS = {
    'easy': DifficultySettings(min_speed=10, max_speed=15, min_height=40, max_height=50, frequency=45),
    'normal': DifficultySettings(min_speed=16, max_speed=25, min_height=30, max_height=40, frequency=50),
    'hard': DifficultySettings(min_speed=26, max_speed=50, min_height=20, max_height=40, frequency=75),
    'impossible': DifficultySettings(min_speed=51, max_speed=75, min_height=10, max_height=50, frequency=100)
}

class Player:
    SIZE = 50
    JUMP_SPEED = 15
    GRAVITY = 1

    def __init__(self, x, y, shape):
        self.rect = pygame.Rect(x, y, self.SIZE, self.SIZE)
        self.jumping = False
        self.jump_speed = self.JUMP_SPEED
        self.colliding = False
        self.shape = shape

    def draw(self, screen):
        if self.shape == 'square':
            pygame.draw.rect(screen, RED, self.rect)
        elif self.shape == 'circle':
            pygame.draw.circle(screen, RED, self.rect.center, self.SIZE // 2)
        elif self.shape == 'triangle':
            pygame.draw.polygon(screen, RED, [(self.rect.x, self.rect.y + self.SIZE), (self.rect.x + self.SIZE // 2, self.rect.y), (self.rect.x + self.SIZE, self.rect.y + self.SIZE)])

    def update(self):
        if self.jumping:
            self.rect.y -= self.jump_speed
            self.jump_speed -= self.GRAVITY
            if self.rect.y >= GROUND:
                self.rect.y = GROUND
                self.jumping = False
                self.jump_speed = self.JUMP_SPEED

    def jump(self):
        if not self.jumping:
            self.jumping = True
            pygame.mixer.music.load("media/jump.wav")
            pygame.mixer.music.play()

    def collides_with(self, obstacle):
        collision = self.rect.colliderect(obstacle.rect)
        if collision and not self.colliding:
            self.colliding = True
            pygame.mixer.music.load("media/collision.wav")
            pygame.mixer.music.play()
            return True
        elif not collision:
            self.colliding = False
        return False

class Obstacle:

    WIDTH = 50

    def __init__(self, x, y, height, speed):
        self.HEIGHT = height
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.passed = False
        self.speed = speed

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)

    def update(self):
        self.rect.x -= self.speed

    def is_passed_by(self, player):
        if self.rect.x < player.rect.x and not self.passed:
            self.passed = True
            return True
        return False


class Game:
    def __init__(self, shape, difficulty):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.player = Player(WIDTH // 4, GROUND, shape)
        self.difficulty = difficulty
        self.obstacle = self.create_obstacle()  # create the first obstacle
        self.score = 0
        self.collisions = 0
        self.frame = 0
        self.obstacle_frequency_counter = 0  # Initialize the counter

    def display_status(self):
        score_text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))
        for i in range(2 - self.collisions):
            heart = pygame.image.load('media/heart_16x16_alpha.png')
            heart = pygame.transform.scale(heart, (30, 30))
            self.screen.blit(heart, (10 + i * 40, 10))

    def create_obstacle(self):  # function to create a new obstacle
        difficulty_settings = DIFFICULTY_SETTINGS[self.difficulty]
        obstacle_height = random.randint(difficulty_settings.min_height, difficulty_settings.max_height)
        obstacle_speed = random.randint(difficulty_settings.min_speed, difficulty_settings.max_speed)
        return Obstacle(WIDTH, GROUND - obstacle_height, obstacle_height, obstacle_speed)


    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()

            self.screen.fill(WHITE)
            self.display_status()

            self.player.update()
            self.player.draw(self.screen)

            if self.obstacle.rect.x < -self.obstacle.WIDTH or self.obstacle_frequency_counter >= DIFFICULTY_SETTINGS[self.difficulty].frequency: 
                self.obstacle = self.create_obstacle()  # create a new obstacle when the old one is off the screen
                self.obstacle_frequency_counter = 0  # reset the counter

            self.obstacle.update()
            self.obstacle.draw(self.screen)

            pygame.time.delay(50)

            if self.player.collides_with(self.obstacle):
                self.collisions += 1
                self.score -= 1
                print("Collisions: " + str(self.collisions) + " of 2")
                if self.collisions > 1:
                    pygame.mixer.music.load("media/youlose.wav")
                    pygame.mixer.music.play()
                    pygame.time.delay(2000)
                    print("Game Over")
                    pygame.quit()
                    sys.exit()
            elif self.obstacle.is_passed_by(self.player):
                self.score += 1
                print("Score: " + str(self.score))

            if self.score == WINSCORE:
                pygame.mixer.music.load("media/youwin.wav")
                pygame.mixer.music.play()
                pygame.time.delay(2000)
                print("You win!")
                pygame.quit()
                sys.exit()

            pygame.display.flip()
            self.frame += 1
            self.obstacle_frequency_counter += 1  # increment the counter


def start_menu():
    shape_options = {1: 'square', 2: 'circle', 3: 'triangle'}
    difficulty_options = {1: 'easy', 2: 'normal', 3: 'hard', 4: 'impossible'}

    shape_choice = int(input("Choose shape: 1 for square, 2 for circle, 3 for triangle: "))
    difficulty_choice = int(input("Choose difficulty: 1 for easy, 2 for normal, 3 for hard, 4 for impossible: "))
    
    shape = shape_options.get(shape_choice, 'square')  # defaults to 'square' if an invalid number is entered
    difficulty = difficulty_options.get(difficulty_choice, 'easy')  # defaults to 'easy' if an invalid number is entered

    game = Game(shape, difficulty)
    game.run()

    
if __name__ == "__main__":
    start_menu()
