import pygame
import sys
import time

pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 36)
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
GROUND = HEIGHT - 50

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

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
            return True
        elif not collision:
            self.colliding = False
        return False

class Obstacle:
    WIDTH, HEIGHT = 50, 50
    SPEED = 10

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.passed = False

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.rect)

    def update(self):
        self.rect.x -= self.SPEED
        if self.rect.x < -self.WIDTH:
            self.rect.x = WIDTH
            self.passed = False

    def is_passed_by(self, player):
        if self.rect.x < player.rect.x and not self.passed:
            self.passed = True
            return True
        return False


def display_status(screen, score, lives):
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))  # Render the score as text
    screen.blit(score_text, (WIDTH - score_text.get_width() - 10, 10))  # Draw the score on the right side of the screen

    for i in range(lives):  # Draw one heart for each remaining life
        heart = pygame.image.load('media/heart_16x16_alpha.png')  # Load the heart image
        heart = pygame.transform.scale(heart, (30, 30))  # Scale it to the right size
        screen.blit(heart, (10 + i * 40, 10))  # Draw the heart on the left side of the screen


screen = pygame.display.set_mode((WIDTH, HEIGHT))

player = Player(WIDTH // 4, GROUND, 'circle')
obstacle = Obstacle(WIDTH, GROUND)

score = 0
collisions = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump()

    screen.fill(WHITE)
    display_status(screen, score, 2 - collisions)

    player.update()
    player.draw(screen)
    obstacle.update()
    obstacle.draw(screen)

    pygame.time.delay(50)

    if player.collides_with(obstacle):
        collisions += 1
        score -= 1
        print("Collisions: " + str(collisions) + " of 2")
        if collisions > 1:
            print("Game Over")
            pygame.quit()
            sys.exit()
        time.sleep(0.5)
    elif obstacle.is_passed_by(player):
        score += 1
        print("Score: " + str(score))

    if score == 10:
        print("You win!")
        pygame.quit()
        sys.exit()

    pygame.display.flip()
