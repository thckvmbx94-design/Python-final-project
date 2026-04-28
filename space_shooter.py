"""
Abdul and Shoaib's Ship

A beginner-friendly space shooter made with pygame.

Controls:
- Left / Right or A / D: move the ship
- Up / Down or W / S: move the ship
- Space: shoot
- P: pause or unpause
- R: restart after game over
- Esc: quit

To run:
1. Install pygame if needed: pip install pygame
2. Open this file in IDLE
3. Press F5 to run the game
"""

import random
import sys

import pygame


# -----------------------------
# Screen size and game speed
# -----------------------------
WIDTH = 900
HEIGHT = 700
FPS = 60


# -----------------------------
# Colors
# -----------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
RED = (220, 50, 50)
YELLOW = (255, 220, 70)
ORANGE = (255, 150, 60)
BLUE = (70, 130, 255)
LIGHT_BLUE = (160, 210, 255)
GREEN = (70, 190, 90)
DARK_GREEN = (20, 120, 50)


class Star:
    """A tiny star that moves down the screen."""

    def __init__(self):
        self.reset()
        self.y = random.randint(0, HEIGHT)

    def reset(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.size = random.randint(1, 2)
        self.speed = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.reset()

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (self.x, self.y), self.size)


class Bullet:
    """Bullet fired by the player."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 3, y - 12, 6, 16)
        self.speed = 10

    def update(self):
        self.rect.y -= self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, YELLOW, self.rect)
        pygame.draw.rect(screen, RED, self.rect, 1)


class EnemyBullet:
    """Bullet fired by an enemy ship."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 4, y, 8, 18)
        self.speed = 6

    def update(self):
        self.rect.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)
        pygame.draw.rect(screen, YELLOW, self.rect, 1)


class Explosion:
    """A simple circle effect when something gets hit."""

    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 8
        self.timer = 15

    def update(self):
        self.radius += 2
        self.timer -= 1

    def draw(self, screen):
        if self.timer > 0:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius, 2)


class Player:
    """The player ship controlled by the keyboard."""

    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 28, HEIGHT - 100, 56, 60)
        self.speed = 7
        self.health = 5
        self.max_health = 5
        self.shoot_cooldown = 0
        self.shield_timer = 0
        self.rapid_fire_timer = 0

    def update(self, keys):
        # Move the player based on the arrow keys or WASD keys.
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.rect.y += self.speed

        # Keep the ship inside the window.
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        # Count down timers each frame.
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.shield_timer > 0:
            self.shield_timer -= 1
        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1

    def shoot(self):
        """Return a new bullet when the player is allowed to shoot."""
        if self.shoot_cooldown > 0:
            return None

        if self.rapid_fire_timer > 0:
            self.shoot_cooldown = 6
        else:
            self.shoot_cooldown = 12

        return Bullet(self.rect.centerx, self.rect.top)

    def has_shield(self):
        return self.shield_timer > 0

    def draw(self, screen):
        # Draw the main body of Abdul and Shoaib's ship.
        body_points = [
            (self.rect.centerx, self.rect.y),
            (self.rect.right - 2, self.rect.bottom - 12),
            (self.rect.centerx, self.rect.bottom - 25),
            (self.rect.left + 2, self.rect.bottom - 12),
        ]
        pygame.draw.polygon(screen, RED, body_points)
        pygame.draw.polygon(screen, YELLOW, body_points, 2)

        # Draw the cockpit.
        cockpit = pygame.Rect(self.rect.x + 18, self.rect.y + 16, 20, 18)
        pygame.draw.ellipse(screen, LIGHT_BLUE, cockpit)
        pygame.draw.ellipse(screen, WHITE, cockpit, 2)

        # Draw small engine flames.
        left_fire = [(self.rect.x + 10, self.rect.bottom - 16), (self.rect.x + 18, self.rect.bottom - 16), (self.rect.x + 14, self.rect.bottom)]
        right_fire = [(self.rect.right - 18, self.rect.bottom - 16), (self.rect.right - 10, self.rect.bottom - 16), (self.rect.right - 14, self.rect.bottom)]
        pygame.draw.polygon(screen, ORANGE, left_fire)
        pygame.draw.polygon(screen, ORANGE, right_fire)

        # If the shield is active, draw a circle around the player.
        if self.has_shield():
            pygame.draw.circle(screen, YELLOW, self.rect.center, 38, 3)


class Enemy:
    """A UFO enemy that moves down and can shoot back."""

    def __init__(self, level):
        width = random.randint(52, 70)
        height = random.randint(28, 38)
        x = random.randint(20, WIDTH - width - 20)
        y = random.randint(-220, -60)

        self.rect = pygame.Rect(x, y, width, height)
        self.speed = random.randint(2, 4) + level // 2
        self.direction = random.choice([-1, 1])
        self.side_speed = random.randint(1, 2)
        self.color = random.choice([RED, ORANGE, YELLOW])
        self.value = 10 + level * 2
        self.shoot_timer = random.randint(50, 130)

    def update(self):
        # Move the UFO downward.
        self.rect.y += self.speed

        # Move the UFO a little side to side.
        self.rect.x += self.direction * self.side_speed
        if self.rect.left <= 5 or self.rect.right >= WIDTH - 5:
            self.direction *= -1

        # Count down until the enemy can shoot again.
        self.shoot_timer -= 1

    def ready_to_shoot(self):
        """Return True when the enemy should fire a bullet."""
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(70, 140)
            return True
        return False

    def draw(self, screen):
        # Draw the bottom saucer shape.
        pygame.draw.ellipse(screen, self.color, self.rect)
        pygame.draw.ellipse(screen, WHITE, self.rect, 2)

        # Draw the glass dome on top.
        dome = pygame.Rect(self.rect.x + 12, self.rect.y - 8, self.rect.width - 24, self.rect.height // 2)
        pygame.draw.ellipse(screen, GRAY, dome)
        pygame.draw.ellipse(screen, WHITE, dome, 2)

        # Draw lights on the UFO.
        light_y = self.rect.bottom - 6
        for light_x in range(self.rect.x + 10, self.rect.right - 8, 14):
            pygame.draw.circle(screen, YELLOW, (light_x, light_y), 3)


class PowerUp:
    """A falling item that helps the player."""

    def __init__(self, x, y):
        self.kind = random.choice(["shield", "rapid", "heal"])
        self.rect = pygame.Rect(x, y, 28, 28)
        self.speed = 3

    def update(self):
        self.rect.y += self.speed

    def apply(self, player):
        if self.kind == "shield":
            player.shield_timer = FPS * 5
        elif self.kind == "rapid":
            player.rapid_fire_timer = FPS * 5
        elif self.kind == "heal":
            player.health = min(player.max_health, player.health + 1)

    def draw(self, screen):
        if self.kind == "shield":
            color = YELLOW
        elif self.kind == "rapid":
            color = ORANGE
        else:
            color = GREEN

        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)

        # Draw a symbol on the power-up so the player knows what it does.
        center_x = self.rect.centerx
        center_y = self.rect.centery

        if self.kind == "shield":
            pygame.draw.circle(screen, BLACK, (center_x, center_y), 7, 2)
        elif self.kind == "rapid":
            pygame.draw.line(screen, BLACK, (center_x - 5, center_y - 6), (center_x + 3, center_y), 3)
            pygame.draw.line(screen, BLACK, (center_x + 3, center_y), (center_x - 1, center_y), 3)
            pygame.draw.line(screen, BLACK, (center_x - 1, center_y), (center_x + 5, center_y + 6), 3)
        else:
            pygame.draw.line(screen, BLACK, (center_x - 6, center_y), (center_x + 6, center_y), 3)
            pygame.draw.line(screen, BLACK, (center_x, center_y - 6), (center_x, center_y + 6), 3)


class Game:
    """This class controls the whole game."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Abdul and Shoaib's Ship")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("arial", 52, bold=True)
        self.main_font = pygame.font.SysFont("arial", 28)
        self.small_font = pygame.font.SysFont("arial", 22)

        self.stars = []
        for _ in range(90):
            self.stars.append(Star())

        self.running = True
        self.state = "start"
        self.reset_game()

    def reset_game(self):
        """Set the game back to the starting values."""
        self.player = Player()
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.powerups = []
        self.explosions = []
        self.score = 0
        self.level = 1
        self.paused = False
        self.enemy_spawn_timer = 0
        self.message = ""
        self.message_timer = 0

    def run(self):
        """Main loop that keeps the game running."""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        """Check for keyboard and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.state == "start" and event.key == pygame.K_RETURN:
                    self.state = "playing"
                elif self.state == "game_over" and event.key == pygame.K_r:
                    self.reset_game()
                    self.state = "playing"
                elif self.state == "playing" and event.key == pygame.K_p:
                    self.paused = not self.paused

    def update(self):
        """Update the game each frame."""
        for star in self.stars:
            star.update()

        if self.state != "playing" or self.paused:
            return

        self.level = 1 + self.score // 180

        keys = pygame.key.get_pressed()
        self.player.update(keys)

        # Hold space to keep shooting.
        if keys[pygame.K_SPACE]:
            bullet = self.player.shoot()
            if bullet is not None:
                self.player_bullets.append(bullet)

        self.spawn_enemies()
        self.update_player_bullets()
        self.update_enemies()
        self.update_enemy_bullets()
        self.update_powerups()
        self.update_explosions()

        if self.message_timer > 0:
            self.message_timer -= 1

        if self.player.health <= 0:
            self.state = "game_over"

    def spawn_enemies(self):
        """Create new enemies over time."""
        self.enemy_spawn_timer += 1
        spawn_delay = max(20, 60 - self.level * 2)

        if self.enemy_spawn_timer >= spawn_delay:
            self.enemy_spawn_timer = 0
            self.enemies.append(Enemy(self.level))

    def update_player_bullets(self):
        """Move player bullets and check if they hit enemies."""
        for bullet in self.player_bullets[:]:
            bullet.update()

            if bullet.rect.bottom < 0:
                self.player_bullets.remove(bullet)
                continue

            for enemy in self.enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if bullet in self.player_bullets:
                        self.player_bullets.remove(bullet)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)

                    self.score += enemy.value
                    self.explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery, enemy.color))

                    # Sometimes an enemy drops a power-up.
                    if random.random() < 0.15:
                        self.powerups.append(PowerUp(enemy.rect.centerx - 14, enemy.rect.centery - 14))
                    break

    def update_enemies(self):
        """Move enemies and let them shoot at the player."""
        for enemy in self.enemies[:]:
            enemy.update()

            if enemy.ready_to_shoot():
                self.enemy_bullets.append(EnemyBullet(enemy.rect.centerx, enemy.rect.bottom))

            # If an enemy gets past the player, the player loses health.
            if enemy.rect.top > HEIGHT:
                self.enemies.remove(enemy)
                self.player.health -= 1
                self.explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery, RED))
                continue

            # If an enemy crashes into the player, damage the player.
            if enemy.rect.colliderect(self.player.rect):
                self.enemies.remove(enemy)
                if not self.player.has_shield():
                    self.player.health -= 1
                self.explosions.append(Explosion(enemy.rect.centerx, enemy.rect.centery, enemy.color))

    def update_enemy_bullets(self):
        """Move enemy bullets and check if they hit the player."""
        for bullet in self.enemy_bullets[:]:
            bullet.update()

            if bullet.rect.top > HEIGHT:
                self.enemy_bullets.remove(bullet)
                continue

            if bullet.rect.colliderect(self.player.rect):
                self.enemy_bullets.remove(bullet)
                if not self.player.has_shield():
                    self.player.health -= 1
                self.explosions.append(Explosion(self.player.rect.centerx, self.player.rect.centery, YELLOW))

    def update_powerups(self):
        """Move power-ups and apply them if the player touches one."""
        for powerup in self.powerups[:]:
            powerup.update()

            if powerup.rect.top > HEIGHT:
                self.powerups.remove(powerup)
                continue

            if powerup.rect.colliderect(self.player.rect):
                powerup.apply(self.player)
                self.powerups.remove(powerup)
                self.show_message(powerup.kind)

    def update_explosions(self):
        """Update and remove old explosion effects."""
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.timer <= 0:
                self.explosions.remove(explosion)

    def show_message(self, kind):
        """Show text when the player picks up a power-up."""
        if kind == "shield":
            self.message = "Shield Activated!"
        elif kind == "rapid":
            self.message = "Rapid Fire!"
        else:
            self.message = "Health Restored!"

        self.message_timer = FPS * 2

    def draw_background(self):
        """Draw space, stars, and a planet in the background."""
        self.screen.fill(BLACK)

        for star in self.stars:
            star.draw(self.screen)

        self.draw_earth()

    def draw_earth(self):
        """Draw a simple Earth in the corner of the screen."""
        planet_center = (WIDTH - 110, 120)

        pygame.draw.circle(self.screen, BLUE, planet_center, 70)
        pygame.draw.circle(self.screen, LIGHT_BLUE, (planet_center[0] - 18, planet_center[1] - 20), 20)

        land1 = [(planet_center[0] - 25, planet_center[1] - 10), (planet_center[0] - 10, planet_center[1] - 35), (planet_center[0] + 5, planet_center[1] - 10), (planet_center[0] - 5, planet_center[1] + 12)]
        land2 = [(planet_center[0] + 12, planet_center[1] + 5), (planet_center[0] + 35, planet_center[1] - 8), (planet_center[0] + 28, planet_center[1] + 22), (planet_center[0] + 5, planet_center[1] + 25)]
        land3 = [(planet_center[0] - 40, planet_center[1] + 18), (planet_center[0] - 18, planet_center[1] + 5), (planet_center[0] - 8, planet_center[1] + 32), (planet_center[0] - 28, planet_center[1] + 38)]

        pygame.draw.polygon(self.screen, GREEN, land1)
        pygame.draw.polygon(self.screen, DARK_GREEN, land2)
        pygame.draw.polygon(self.screen, GREEN, land3)
        pygame.draw.circle(self.screen, WHITE, planet_center, 70, 2)

    def draw_hud(self):
        """Draw score, level, and health on the screen."""
        score_text = self.main_font.render("Score: " + str(self.score), True, WHITE)
        level_text = self.main_font.render("Level: " + str(self.level), True, WHITE)
        self.screen.blit(score_text, (20, 15))
        self.screen.blit(level_text, (20, 48))

        # Draw health hearts.
        for i in range(self.player.max_health):
            if i < self.player.health:
                color = RED
            else:
                color = GRAY

            heart_x = WIDTH - 180 + i * 30
            pygame.draw.circle(self.screen, color, (heart_x, 30), 9)
            pygame.draw.circle(self.screen, color, (heart_x + 12, 30), 9)
            pygame.draw.polygon(
                self.screen,
                color,
                [(heart_x - 10, 34), (heart_x + 22, 34), (heart_x + 6, 52)],
            )

        shield_text = self.small_font.render("Shield: " + str(max(0, self.player.shield_timer // FPS)), True, WHITE)
        rapid_text = self.small_font.render("Rapid: " + str(max(0, self.player.rapid_fire_timer // FPS)), True, WHITE)
        self.screen.blit(shield_text, (WIDTH - 200, 60))
        self.screen.blit(rapid_text, (WIDTH - 200, 90))

        if self.message_timer > 0:
            message_text = self.main_font.render(self.message, True, YELLOW)
            self.screen.blit(message_text, (WIDTH // 2 - message_text.get_width() // 2, 20))

    def draw_start_screen(self):
        """Draw the first screen the player sees."""
        title = self.title_font.render("Abdul and Shoaib's Ship", True, YELLOW)
        subtitle = self.main_font.render("Defend space from the enemy UFO fleet.", True, WHITE)

        lines = [
            "Move with Arrow Keys or W A S D",
            "Press Space to shoot",
            "Enemy ships shoot back, so keep dodging",
            "Collect power-ups for shield, rapid fire, and health",
            "Press Enter to start",
        ]

        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 170))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 245))

        for i, line in enumerate(lines):
            text = self.small_font.render(line, True, WHITE)
            self.screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 330 + i * 40))

    def draw_pause_screen(self):
        """Draw the pause message."""
        pause_text = self.title_font.render("Paused", True, YELLOW)
        info_text = self.small_font.render("Press P to continue", True, WHITE)
        self.screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 60))
        self.screen.blit(info_text, (WIDTH // 2 - info_text.get_width() // 2, HEIGHT // 2 + 10))

    def draw_game_over(self):
        """Draw the game over screen."""
        title = self.title_font.render("Game Over", True, RED)
        score = self.main_font.render("Final Score: " + str(self.score), True, YELLOW)
        restart = self.small_font.render("Press R to play again", True, WHITE)

        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 230))
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, 305))
        self.screen.blit(restart, (WIDTH // 2 - restart.get_width() // 2, 360))

    def draw(self):
        """Draw everything on the screen."""
        self.draw_background()

        if self.state == "start":
            self.draw_start_screen()
        else:
            for bullet in self.player_bullets:
                bullet.draw(self.screen)

            for bullet in self.enemy_bullets:
                bullet.draw(self.screen)

            for enemy in self.enemies:
                enemy.draw(self.screen)

            for powerup in self.powerups:
                powerup.draw(self.screen)

            for explosion in self.explosions:
                explosion.draw(self.screen)

            self.player.draw(self.screen)
            self.draw_hud()

            if self.paused:
                self.draw_pause_screen()

            if self.state == "game_over":
                self.draw_game_over()

        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
