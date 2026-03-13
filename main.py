import pygame
import random
import sys
import os

# --- Inicialização ---
pygame.init()

SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640
FPS = 60

# --- Cores ---
WHITE = (245, 245, 245)     
BLACK = (10, 10, 16)        
RED_ENEMY = (255, 0, 0)     
RED_HEART = (220, 20, 60)   
YELLOW_TEXT = (255, 215, 0) 
BULLET_PLAYER = (255, 255, 255) 

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Descida Perigosa na Cachoeira")
clock = pygame.time.Clock()

try:
    font_main = pygame.font.SysFont('Arial', 24, bold=True)
    font_title = pygame.font.SysFont('Arial', 48, bold=True)
except:
    font_main = pygame.font.Font(None, 32)
    font_title = pygame.font.Font(None, 64)

# --- Funções de Utilidade ---

def generate_heart_image():
    heart_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
    pixels = [(2,6), (3,6), (4,6), (8,6), (9,6), (10,6), (1,7), (2,7), (3,7), (4,7), (5,7), (7,7), (8,7), (9,7), (10,7), (11,7), (0,8), (1,8), (2,8), (3,8), (4,8), (5,8), (6,8), (7,8), (8,8), (9,8), (10,8), (11,8), (12,8), (0,9), (1,9), (2,9), (3,9), (4,9), (5,9), (6,9), (7,9), (8,9), (9,9), (10,9), (11,9), (12,9), (1,10), (2,10), (3,10), (4,10), (5,10), (6,10), (7,10), (8,10), (9,10), (10,10), (11,10), (2,11), (3,11), (4,11), (5,11), (6,11), (7,11), (8,11), (9,11), (10,11), (3,12), (4,12), (5,12), (6,12), (7,12), (8,12), (9,12), (4,13), (5,13), (6,13), (7,13), (8,13), (5,14), (6,14), (7,14), (6,15)]
    for px, py in pixels: pygame.draw.rect(heart_surf, RED_HEART, (px*1.8, py*1.2, 2, 2))
    return heart_surf

def load_image(name, scale=None):
    try:
        image = pygame.image.load(name).convert_alpha()
    except:
        if "plane" in name:
            surf = pygame.Surface(scale if scale else (50, 50), pygame.SRCALPHA)
            pygame.draw.polygon(surf, RED_ENEMY, [(0, 40), (25, 0), (50, 40)])
            return surf
        elif "heart" in name: return generate_heart_image()
        surf = pygame.Surface(scale if scale else (50, 50)); surf.fill((255, 0, 255))
        return surf
    if scale: image = pygame.transform.scale(image, scale)
    return image

def draw_text_shaded(surface, text, font, color, x, y, anchor="topleft"):
    msg_shadow = font.render(text, True, BLACK)
    rect_shadow = msg_shadow.get_rect(**{anchor: (x+2, y+2)})
    surface.blit(msg_shadow, rect_shadow)
    msg_main = font.render(text, True, color)
    rect_main = msg_main.get_rect(**{anchor: (x, y)})
    surface.blit(msg_main, rect_main)

# --- Assets ---
player_img = load_image('player.png', (50, 60))
player_left_img = load_image('player_left.png', (50, 60))
player_right_img = load_image('player_right.png', (50, 60))
enemy_img = load_image('enemy.png', (40, 40))
rock_img = load_image('rock.png', (80, 70))
plane_img = load_image('plane.png', (60, 60)) 
heart_img = load_image('heart.png', (40, 30))
background_img = load_image('waterfall.png', (SCREEN_WIDTH, SCREEN_HEIGHT))
boss_img = load_image('boss.png', (200, 150))



rock_break_imgs = []
for i in range(5):
    surf = pygame.Surface((80, 70), pygame.SRCALPHA)
    # Desenha estilhaços cinzas simulando a pedra quebrando
    color = (100, 100, 100)
    for _ in range(10 - i*2):
        rx = random.randint(10, 70)
        ry = random.randint(10, 60)
        pygame.draw.rect(surf, color, (rx, ry, 15 - i*2, 15 - i*2))
    rock_break_imgs.append(surf)

# --- Classes ---

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, color=WHITE, speed=7, is_super=False):
        super().__init__()
        self.is_super = is_super
        self.image = pygame.Surface((10, 20) if is_super else (6, 12))
        self.image.fill(YELLOW_TEXT if is_super else color)
        self.rect = self.image.get_rect(centerx=x, y=y)
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = direction
        self.speed = speed
        self.dx = 0

    def update(self):
        self.rect.y += self.speed * self.direction
        self.rect.x += self.dx
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT: self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Guardamos todas as variações
        self.img_center = player_img
        self.img_right = player_left_img
        self.img_left = player_right_img
        
        self.image = self.img_center
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-80))
        self.mask = pygame.mask.from_surface(self.image)
        self.cooldown = 0
        self.invincible = 0

    def update(self, current_speed):
        global is_power_active, power_active_timer, power_charges, show_special_alert
        keys = pygame.key.get_pressed()
        
        # --- Lógica do Poder ---
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and power_charges > 0 and not is_power_active:
            is_power_active = True
            power_charges -= 1
            power_active_timer = 180 # 2 segundos a 60 FPS
            show_special_alert = False # O jogador já usou, então o alerta some

        if is_power_active:
            power_active_timer -= 1
            if power_active_timer <= 0:
                is_power_active = False
        
        # Resetamos para a imagem central a cada frame
        self.image = self.img_center
        
        if keys[pygame.K_LEFT] and self.rect.left > 40: 
            self.rect.x -= current_speed
            self.image = self.img_left # Muda para imagem da esquerda
            
        elif keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH - 40: 
            self.rect.x += current_speed
            self.image = self.img_right # Muda para imagem da direita

        # Atualiza a máscara de colisão caso as imagens tenham formatos diferentes
        self.mask = pygame.mask.from_surface(self.image)

        # Lógica de tiro
        if keys[pygame.K_SPACE] and self.cooldown == 0:
            # Se o poder estiver ativo, tiro é SUPER e mais rápido
            s_speed = 12 if is_power_active else 9
            bullet = Bullet(self.rect.centerx, self.rect.top, -1, color=BULLET_PLAYER, speed=s_speed, is_super=is_power_active)
            all_sprites.add(bullet); player_bullets.add(bullet)
            self.cooldown = 5 if is_power_active else 15
        
        if self.cooldown > 0: self.cooldown -= 1
        
        # Lógica de invencibilidade (piscando)
        if self.invincible > 0: 
            self.invincible -= 1
            self.image.set_alpha(150 if self.invincible % 10 < 5 else 255)
        else: 
            self.image.set_alpha(255)

class Rock(pygame.sprite.Sprite):
    def __init__(self): # Removido o argumento existing_rocks
        super().__init__()
        self.image = rock_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        # Sorteia uma posição X que não seja colada na borda
        self.rect.x = random.randint(50, SCREEN_WIDTH - 130)
        # Faz a pedra nascer um pouco acima da tela para entrar deslizando
        self.rect.y = random.randint(-200, -80)

    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, anchor_rock=None):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.anchor = anchor_rock
        if self.anchor: self.rect.center = self.anchor.rect.center
        else:
            self.rect.x = random.choice([20, SCREEN_WIDTH - 60])
            self.rect.y = -100
        self.fire_counter = 0 

    def update(self, fire_rate, bullet_speed, scroll_speed, p_rect): # Adicionamos p_rect
        if self.anchor:
            self.rect.center = self.anchor.rect.center
            if not self.anchor.alive(): self.kill() 
        else: self.rect.y += scroll_speed
        
        self.fire_counter += 1
        if self.fire_counter >= fire_rate:
            # Lógica de mira: Calcula se o jogador está para a esquerda ou direita
            # Isso faz com que os tiros não sejam apenas verticais
            dx = 0
            if p_rect.centerx < self.rect.centerx - 20: dx = -1.5 # Atira diagonal esq
            elif p_rect.centerx > self.rect.centerx + 20: dx = 1.5 # Atira diagonal dir
            
            bullet = Bullet(self.rect.centerx, self.rect.bottom, 1, color=RED_ENEMY, speed=bullet_speed)
            bullet.dx = dx # Precisamos adicionar dx na classe Bullet
            all_sprites.add(bullet); enemy_bullets.add(bullet)
            self.fire_counter = 0
        if self.rect.top > SCREEN_HEIGHT: self.kill()

class RockExplosion(pygame.sprite.Sprite):
    def __init__(self, x, y, frames):
        super().__init__()
        self.frames = frames
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.timer = 0

    def update(self, scroll_speed):
        self.timer += 1
        if self.timer > 5: # Velocidade da animação
            self.timer = 0
            self.index += 1
            if self.index < len(self.frames):
                self.image = self.frames[self.index]
            else:
                self.kill()
        self.rect.y += scroll_speed

class Plane(pygame.sprite.Sprite):
    def __init__(self, speed_boost, distance, can_shoot=True):
        super().__init__()
        self.image = plane_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randint(20, SCREEN_WIDTH - 70)
        self.rect.y = -100
        self.speed = 6 + speed_boost
        self.can_shoot = can_shoot
        self.fire_rate = max(60 - (distance // 1000), 20)
        self.fire_counter = 0
    def update(self, current_distance):
        self.rect.y += self.speed
        if self.can_shoot:
            self.fire_counter += 1
            if self.fire_counter >= self.fire_rate:
                bullet = Bullet(self.rect.centerx, self.rect.bottom, 1, color=RED_ENEMY, speed=self.speed + 2)
                all_sprites.add(bullet); enemy_bullets.add(bullet)
                self.fire_counter = 0
        if self.rect.top > SCREEN_HEIGHT: self.kill()

class HeartItem(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = heart_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randint(80, SCREEN_WIDTH - 80)
        self.rect.y = -50
    def update(self, speed):
        self.rect.y += speed 
        if self.rect.top > SCREEN_HEIGHT: self.kill()
class Boss(pygame.sprite.Sprite):
    def __init__(self, distance):
        super().__init__()
        self.image = boss_img
        self.rect = self.image.get_rect(midtop=(SCREEN_WIDTH//2, -self.image.get_height()))
        self.mask = pygame.mask.from_surface(self.image)
        
        # Atributos de Vida e Estado (ajustados para a nova imagem)
        self.max_health = 50 + (distance // 5000) * 20 # Aumentei a vida base, já que é um boss real
        self.health = self.max_health
        self.speed = 2 # Um pouco mais lento por ser maior
        self.direction = 1
        self.target_y = 50 # Onde ele para na tela
        self.is_active = False
        self.fire_counter = 0

    def update(self, player_x):
        # Entrada triunfal: desce até o target_y
        if self.rect.y < self.target_y:
            self.rect.y += 1
        else:
            self.is_active = True

        if self.is_active:
            # Movimentação padrão: segue o jogador levemente
            if self.rect.centerx < player_x: self.rect.x += 1
            elif self.rect.centerx > player_x: self.rect.x -= 1

            # Ataque
            self.fire_counter += 1
            if self.fire_counter > 50: # Atira um pouco mais rápido
                bullet = Bullet(self.rect.centerx, self.rect.bottom - 10, 1, color=RED_ENEMY, speed=8)
                all_sprites.add(bullet); enemy_bullets.add(bullet)
                self.fire_counter = 0

    def draw_health_bar(self, surface):
        # Desenha a barra de vida no topo, centralizada
        bar_width = 250
        bar_height = 15
        fill = (self.health / self.max_health) * bar_width
        
        # Centraliza a barra horizontalmente
        bar_x = (SCREEN_WIDTH // 2) - (bar_width // 2)
        bar_y = self.rect.top - 25 # 25 pixels acima do sprite do boss

        outline_rect = pygame.Rect((bar_x, bar_y), (bar_width, bar_height))
        fill_rect = pygame.Rect((bar_x, bar_y), (fill, bar_height))
        
        # Desenha o fundo preto, o preenchimento vermelho e a borda branca
        pygame.draw.rect(surface, BLACK, outline_rect)
        pygame.draw.rect(surface, RED_ENEMY, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)
def show_tutorial():
    screen.fill(BLACK)
    draw_text_shaded(screen, "COMO JOGAR", font_title, YELLOW_TEXT, SCREEN_WIDTH//2, 80, "center")
    instructions = [
        "SETAS: Mover para Esquerda/Direita",
        "ESPAÇO: Atirar",
        "SHIFT: Ativar Especial (quando pronto)",
        "",
        "OBJETIVO:",
        "Destrua inimigos para ganhar Pontos.",
        "A cada 1500 pontos, ganhe um ESPECIAL!",
        "O Especial destrói até as Pedras.",
        "",
        "Pressione [ ENTER ] para Iniciar"
    ]
    for i, line in enumerate(instructions):
        draw_text_shaded(screen, line, font_main, WHITE, SCREEN_WIDTH//2, 180 + (i * 35), "center")
    pygame.display.flip()
    wait = True
    while wait:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: wait = False
        clock.tick(FPS)
# --- Lógica Principal ---

def reset_game():
    global all_sprites, enemies, rocks, planes, player_bullets, enemy_bullets, hearts_group, effects_group
    global player, score, distance, bg_y, lives, last_heart_distance, screen_shake, boss
    global power_charges, is_power_active, power_active_timer, last_power_score
    global show_special_alert

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    planes = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    hearts_group = pygame.sprite.Group() 
    effects_group = pygame.sprite.Group()
    show_special_alert = False
    

    score = 0; 
    distance = 0; 
    bg_y = 0; 
    lives = 3
    last_heart_distance = 1000 
    screen_shake = 0
    boss = None

    power_charges = 0        # Quantos "Shifts" o jogador tem
    power_active_timer = 0   # Tempo restante do poder (em frames)
    is_power_active = False  # Estado do poder
    last_power_score = 0     # Auxiliar para saber quando dar o próximo poder

    player = Player()
    all_sprites.add(player)
def show_menu():
    screen.fill(BLACK)
    draw_text_shaded(screen, "DESCIDA", font_title, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100, "midbottom")
    draw_text_shaded(screen, "PERIGOSA", font_title, YELLOW_TEXT, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40, "midbottom")
    draw_text_shaded(screen, "Pressione [ ENTER ]", font_main, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 120, "midtop")
    pygame.display.flip()
    wait = True
    while wait:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: wait = False
        clock.tick(FPS)

# --- Início do Jogo ---
bg_y = 0
show_menu()      # Mostra o título do jogo
show_tutorial()  # Mostra as instruções antes de começar
reset_game()     # Inicia os grupos e variáveis
game_over = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            reset_game(); game_over = False

    if not game_over:
        distance += 1 
        scroll_speed = 3 + (distance // 1000)
        current_player_speed = min(5 + (distance // 2000), 10)
        current_fire_rate = max(100 - (distance // 80), 10)    
        current_enemy_bullet_speed = min(6 + (distance // 500), 18) 
        rock_spawn_chance = min(0.02 + (distance / 25000), 0.18)   
        # Updates
        player.update(current_player_speed)
        enemies.update(current_fire_rate, current_enemy_bullet_speed, scroll_speed, player.rect)        
        planes.update(distance) 
        rocks.update(scroll_speed)
        hearts_group.update(scroll_speed)
        player_bullets.update()
        enemy_bullets.update()
        effects_group.update(scroll_speed)
        
        bg_y = (bg_y + scroll_speed) % SCREEN_HEIGHT

        # --- Spawns ---
        # Aumentamos o limite de pedras e simplificamos o nascimento
        if len(rocks) < 6 and random.random() < rock_spawn_chance:
            r = Rock()
            # Verifica se a nova pedra não nasce em cima de outra já existente
            if not pygame.sprite.spritecollide(r, rocks, False):
                rocks.add(r)
                all_sprites.add(r)
                
                # Chance de ter um inimigo na pedra
                if random.random() < 0.7:
                    e = Enemy(anchor_rock=r)
                    enemies.add(e)
                    all_sprites.add(e)

        if distance > 1000 and random.random() < 0.005:
            p = Plane(distance // 3000, distance)
            planes.add(p); all_sprites.add(p)

        if distance - last_heart_distance > 2000:
            h = HeartItem(); hearts_group.add(h); all_sprites.add(h)
            last_heart_distance = distance

        # --- Colisões ---
        
        if pygame.sprite.spritecollide(player, hearts_group, True, pygame.sprite.collide_mask):
            lives = min(lives + 1, 3); score += 500

        if player.invincible <= 0:
            # Bateu na pedra: A pedra explode e o player perde vida
            rock_hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_mask)
            bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_mask)
            plane_hits = pygame.sprite.spritecollide(player, planes, True, pygame.sprite.collide_mask)
            
            if rock_hits or bullet_hits or plane_hits:
                lives -= 1
                player.invincible = 90
                screen_shake = 10
                # Se foi pedra, cria a animação de quebra específica
                for r in rock_hits:
                    expl = RockExplosion(r.rect.centerx, r.rect.centery, rock_break_imgs)
                    effects_group.add(expl); all_sprites.add(expl)
                
                if lives <= 0: game_over = True
        

        # Tiros do Player
        pygame.sprite.groupcollide(planes, player_bullets, True, True, pygame.sprite.collide_mask)
        
        # Tiro na pedra mata inimigo em cima
        for b in player_bullets:
            if hasattr(b, 'is_super') and b.is_super:
                # Super tiro destrói pedras e ganha pontos extras
                rock_hits = pygame.sprite.spritecollide(b, rocks, True, pygame.sprite.collide_mask)
                for r in rock_hits:
                    score += 50 # Ganha score ao destruir pedra com poder
                    expl = RockExplosion(r.rect.centerx, r.rect.centery, rock_break_imgs)
                    effects_group.add(expl); all_sprites.add(expl)

        rock_shot = pygame.sprite.groupcollide(rocks, player_bullets, False, True, pygame.sprite.collide_mask)

        for r in rock_shot:
            for e in enemies:
                if e.anchor == r: 
                    e.kill(); score += 100
        

        pygame.sprite.groupcollide(enemies, player_bullets, True, True, pygame.sprite.collide_mask)

        for b in player_bullets:
            if b.is_super:
                rock_hits = pygame.sprite.spritecollide(b, rocks, True, pygame.sprite.collide_mask)
                for r in rock_hits:
                    # Cria a explosão da pedra
                    expl = RockExplosion(r.rect.centerx, r.rect.centery, rock_break_imgs)
                    effects_group.add(expl); all_sprites.add(expl)
                    score += 50
        
        flash_alpha = 128 + 127 * (pygame.time.get_ticks() % 500 < 250)
        
        # --- LÓGICA DO BOSS ---
        if distance % 2000 == 0 and distance > 0 and boss is None:
            boss = Boss(distance)
            all_sprites.add(boss)

        if boss:
            boss.update(player.rect.centerx)
            
            # Colisão: Tiro do Player no Boss
            hits = pygame.sprite.spritecollide(boss, player_bullets, True, pygame.sprite.collide_mask)
            if hits:
                boss.health -= 1
                score += 50
                if boss.health <= 0:
                    score += 5000
                    boss.kill()
                    boss = None
                    screen_shake = 30 # Explosão épica!
        
        # No loop principal, onde você ganha o poder:
        if score > 0 and score // 1500 > last_power_score:
            power_charges += 1
            last_power_score = score // 1500
            show_special_alert = True # Ativa o alerta visual
            screen_shake = 10

        
    # --- Desenho ---
    screen.blit(background_img, (0, bg_y))
    screen.blit(background_img, (0, bg_y - SCREEN_HEIGHT))

    # --- Lógica de Tremida de Tela ---
    render_offset = [0, 0]
    if screen_shake > 0:
        render_offset[0] = random.randint(-screen_shake, screen_shake)
        render_offset[1] = random.randint(-screen_shake, screen_shake)
        screen_shake -= 1 # Diminui a tremida gradualmente

    # --- DESENHO ---
    # 1. Fundo
    screen.blit(background_img, (render_offset[0], bg_y + render_offset[1]))
    screen.blit(background_img, (render_offset[0], bg_y - SCREEN_HEIGHT + render_offset[1]))
    
    # 2. Todos os Sprites (usando o offset do tremor)
    for sprite in all_sprites:
        if sprite.alive() and not isinstance(sprite, Boss):
            screen.blit(sprite.image, (sprite.rect.x + render_offset[0], sprite.rect.y + render_offset[1]))
    if boss and boss.alive():
        screen.blit(boss.image, (boss.rect.x + render_offset[0], boss.rect.y + render_offset[1]))
        boss.draw_health_bar(screen)
    # 3. UI (Texto e Vidas)
    draw_text_shaded(screen, f"Score: {score}", font_main, YELLOW_TEXT, 20, 20)
    draw_text_shaded(screen, f"{distance}m", font_main, WHITE, SCREEN_WIDTH//2, 20, "midtop")
    
    for i in range(lives):
        screen.blit(heart_img, (SCREEN_WIDTH - 40 - (i*30), 20))

    # if boss and boss.alive():
    #     boss.draw_health_bar(screen)
    
    # --- Desenho da UI de Poder ---
    if show_special_alert and not is_power_active:
        # Pisca apenas se o alerta estiver ligado e o poder não estiver em uso
        if (pygame.time.get_ticks() // 250) % 2 == 0:
            draw_text_shaded(screen, "ESPECIAL PRONTO [SHIFT]!", font_main, YELLOW_TEXT, SCREEN_WIDTH//2, 120, "midtop")

    # O contador de cargas continua lá no cantinho, mas discreto
    power_color = YELLOW_TEXT if power_charges > 0 else (100, 100, 100)

    if is_power_active:
        draw_text_shaded(screen, "!!! MODO DESTRUIÇÃO !!!", font_main, RED_ENEMY, SCREEN_WIDTH//2, 120, "midtop")
        
        bar_width = (power_active_timer / 120) * 200
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 100, 150, 200, 10))
        pygame.draw.rect(screen, YELLOW_TEXT, (SCREEN_WIDTH//2 - 100, 150, bar_width, 10))

    if game_over:
        draw_text_shaded(screen, "FIM DE JOGO", font_title, RED_ENEMY, SCREEN_WIDTH//2, SCREEN_HEIGHT//2, "center")
        draw_text_shaded(screen, "Aperte 'R' para Reiniciar", font_main, WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, "center")

    pygame.display.flip()
    clock.tick(FPS)