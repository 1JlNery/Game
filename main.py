import pygame
import random
import math

pygame.init()

# Dimensões da tela
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Survivor")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Classe do Jogador
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 30))
        self.image.fill("#3e3b3b")
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 3
        self.shoot_delay = 500 
        self.last_shot = pygame.time.get_ticks()
        self.ammo = 10  
        self.health = 50

    # define os controles de movimento
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed
        
        # impede que o player saia da "arena"
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, HEIGHT - self.rect.height))
        
        # cria um delay na quantidade de tiro
        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and now - self.last_shot > self.shoot_delay and self.ammo > 0:
            self.last_shot = now
            self.ammo -= 1
            mouse_pos = pygame.mouse.get_pos()
            weapon = Weapon(self.rect.center, mouse_pos)
            all_sprites.add(weapon)
            weapons.add(weapon)

        # Recarrega quando a tecla R é pressionada
        if keys[pygame.K_r] and self.ammo <= 9:
            self.ammo = 10  
        if self.health <= 0:
            self.kill()  
            game_over_screen.show()

# Classe da Arma
class Weapon(pygame.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = start_pos
        self.speed = 7
        self.angle = math.atan2(target_pos[1] - start_pos[1], target_pos[0] - start_pos[0])

    # mecánica de tiro 
    def update(self):
        self.rect.x += self.speed * math.cos(self.angle)
        self.rect.y += self.speed * math.sin(self.angle)
        if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()

# Classe do Inimigo
class Enemy(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.speed = random.randint(1, 3)
        self.player = player
        self.spawn_random_position()

    # spawn de forma aleatoria na "arena"
    def spawn_random_position(self):
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = 0
        elif side == "bottom":
            self.rect.x = random.randint(0, WIDTH)
            self.rect.y = HEIGHT
        elif side == "left":
            self.rect.x = 0
            self.rect.y = random.randint(0, HEIGHT)
        elif side == "right":
            self.rect.x = WIDTH
            self.rect.y = random.randint(0, HEIGHT)

    def update(self):
        direction = pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(self.rect.center)
        direction.normalize_ip()
        self.rect.x += direction.x * self.speed
        self.rect.y += direction.y * self.speed

        # Verifica se o inimigo saiu da tela
        if self.rect.right < 0 or self.rect.left > WIDTH or self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.spawn_random_position()

# Tela de início
class StartScreen:
    def __init__(self):
        self.font = pygame.font.Font('font/MedievalSharp-Regular.ttf', 30)
        self.font2 = pygame.font.Font('font/MedievalSharp-Regular.ttf', 205)
        self.name = self.font2.render("Survivor", True, WHITE)
        self.name_rect = self.name.get_rect(center=(WIDTH // 2, HEIGHT // 3))  
        self.title = self.font.render("Pressione ESPAÇO para Iniciar", True, WHITE)
        self.title_rect = self.title.get_rect(center=(WIDTH // 2, HEIGHT // 1.5))

    def draw(self, screen):
        screen.fill(BLACK)
        screen.blit(self.name, self.name_rect)
        screen.blit(self.title, self.title_rect)

# Tela de Game over 
class GameOverScreen:
    def __init__(self):
        self.font = pygame.font.Font('font/MedievalSharp-Regular.ttf', 50)
        self.title = self.font.render("Game Over", True, WHITE)
        self.title_rect = self.title.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    def show(self):
        screen.blit(self.title, self.title_rect)
        pygame.display.flip()
        pygame.time.delay(2000)

# Grupos de sprites
start_screen = StartScreen()
all_sprites = pygame.sprite.Group()
player = Player(WIDTH // 2, HEIGHT - 50)
all_sprites.add(player)
weapons = pygame.sprite.Group()
enemies = pygame.sprite.Group()

in_start_screen = True
game_over_screen = GameOverScreen() 

run = True
clock = pygame.time.Clock()

player_dead = False
game_over = False

# Loop principal
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and in_start_screen:
            in_start_screen = False 

    all_sprites.update()

    screen.fill(BLACK)

    if in_start_screen:
        start_screen.draw(screen)
    else:
        screen.fill("#9aa0a3")
        all_sprites.draw(screen)

    if not player_dead: 
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, player.health * 2, 20))
            
        font = pygame.font.Font(None, 36)
        ammo_text = font.render(f"Munição: {player.ammo}", True, WHITE)
        screen.blit(ammo_text, (10, 40))

        if random.randint(0, 100) < 1 and len(enemies) < 5:  
            enemy = Enemy(player)
            all_sprites.add(enemy)
            enemies.add(enemy)
            enemy.spawn_random_position()

        # Cria inimigos
        if random.randint(0, 100) < 1 and len(enemies) < 5:  
            enemy = Enemy(player)
            all_sprites.add(enemy)
            enemies.add(enemy) 
        
        hits = pygame.sprite.groupcollide(weapons, enemies, True, False)
        for weapon, hit_enemies in hits.items():
            for enemy in hit_enemies:
                enemy.kill()

        hits = pygame.sprite.spritecollide(player, enemies, False)
        for enemy in hits:
            player.health -= 10
            enemy.spawn_random_position()

        if player.health <= 0:
            player_dead = True  
            game_over_screen.show()
            in_start_screen = True

    pygame.display.flip()
    clock.tick(60)

pygame.quit()