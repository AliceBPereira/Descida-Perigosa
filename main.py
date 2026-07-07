import pygame
import random
import sys
import os
import math
import struct

# --- Caminhos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, 'assets', 'images')

# --- Inicialização ---
pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=1)
except Exception as e:
    print(f"[AVISO] Não foi possível inicializar o mixer de som: {e}")

# --- Sintetizador de Som Dinâmico ---
snd_shoot = None
snd_explosion = None
snd_hit = None
snd_powerup = None
snd_special_ready = None
snd_special_active = None
snd_gameover = None
snd_phase_clear = None
snd_boss_siren = None
snd_rock_crack = None
snd_shield_up = None
snd_shield_break = None

def generate_synth_sounds():
    global snd_shoot, snd_explosion, snd_hit, snd_powerup, snd_special_ready, snd_special_active, snd_gameover
    global snd_phase_clear, snd_boss_siren, snd_rock_crack, snd_shield_up, snd_shield_break
    sample_rate = 22050
    
    def synth_sound(duration, func):
        num_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(num_samples):
            t = i / sample_rate
            val = func(t, duration)
            buf.extend(struct.pack('<h', max(-32768, min(32767, int(val)))))
        try:
            return pygame.mixer.Sound(buffer=buf)
        except Exception as e:
            print(f"[AVISO] Erro ao criar Sound buffer: {e}")
            return None

    # Shoot: varredura de 900Hz para 200Hz
    snd_shoot = synth_sound(0.12, lambda t, dur: 12000 * math.sin(2 * math.pi * (900 - 700 * (t/dur)) * t))
    
    # Explosion: decaimento de ruído branco
    snd_explosion = synth_sound(0.35, lambda t, dur: (15000 * (1.0 - t/dur)) * random.uniform(-1.0, 1.0))
    
    # Hit: ruído misturado com baixa frequência áspera
    snd_hit = synth_sound(0.18, lambda t, dur: (20000 * (1.0 - t/dur)) * (random.uniform(-0.6, 0.6) + 0.4 * math.sin(2 * math.pi * 100 * t)))
    
    # Powerup / Coração: arpeggio ascendente (notas dó, mi, sol, dó)
    def powerup_wave(t, dur):
        note = int((t / dur) * 4)
        freqs = [261.63, 329.63, 392.00, 523.25]
        freq = freqs[min(note, 3)]
        return 12000 * (1.0 - t/dur) * math.sin(2 * math.pi * freq * t)
    snd_powerup = synth_sound(0.35, powerup_wave)
    
    # Special Ready: sino agudo (chime)
    snd_special_ready = synth_sound(0.4, lambda t, dur: 10000 * (1.0 - t/dur) * (math.sin(2 * math.pi * 880 * t) + 0.5 * math.sin(2 * math.pi * 1320 * t)))
    
    # Special Active: varredura laser rápida para cima
    snd_special_active = synth_sound(0.45, lambda t, dur: 12000 * math.sin(2 * math.pi * (250 + 1000 * (t/dur)) * t))
    
    # Game Over: escala melancólica descendente
    def gameover_wave(t, dur):
        note = int((t / dur) * 4)
        freqs = [392.00, 349.23, 311.13, 261.63]
        freq = freqs[min(note, 3)]
        return 12000 * (1.0 - t/dur) * math.sin(2 * math.pi * freq * t)
    snd_gameover = synth_sound(0.7, gameover_wave)

    # Phase Clear: arpejo triunfante ascendente (C5-E5-G5-C6-E6-G6)
    def phase_clear_wave(t, dur):
        note = int((t / dur) * 6)
        freqs = [261.63, 329.63, 392.00, 523.25, 659.25, 783.99]
        freq = freqs[min(note, 5)]
        return 10000 * (1.0 - t/dur) * (math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(2 * math.pi * freq * 2 * t))
    snd_phase_clear = synth_sound(0.6, phase_clear_wave)

    # Boss Siren: sirene grave e intimidante
    def boss_siren_wave(t, dur):
        freq = 150 + 85 * math.sin(2 * math.pi * 4.5 * t)
        return 14000 * math.sin(2 * math.pi * freq * t)
    snd_boss_siren = synth_sound(1.2, boss_siren_wave)

    # Rock Crack: som áspero de pedra rachando
    snd_rock_crack = synth_sound(0.15, lambda t, dur: (18000 * (1.0 - t/dur)) * (random.uniform(-0.8, 0.8) + 0.2 * math.sin(2 * math.pi * 80 * t)))

    # Shield Up: sintetizador ascendente e futurista
    snd_shield_up = synth_sound(0.4, lambda t, dur: 10000 * (1.0 - t/dur) * math.sin(2 * math.pi * (300 + 600 * (t/dur)) * t))

    # Shield Break: som de escudo de energia quebrando (shatter)
    snd_shield_break = synth_sound(0.3, lambda t, dur: (15000 * (1.0 - t/dur)) * (random.uniform(-0.9, 0.9) * math.sin(2 * math.pi * 2500 * t)))

generate_synth_sounds()

def play_sound(snd):
    if snd:
        try:
            snd.play()
        except:
            pass

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

def asset_path(filename):
    """Retorna o caminho completo para um asset na pasta assets/images/"""
    return os.path.join(ASSETS_DIR, filename)

def generate_heart_image():
    heart_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
    pixels = [(2,6), (3,6), (4,6), (8,6), (9,6), (10,6), (1,7), (2,7), (3,7), (4,7), (5,7), (7,7), (8,7), (9,7), (10,7), (11,7), (0,8), (1,8), (2,8), (3,8), (4,8), (5,8), (6,8), (7,8), (8,8), (9,8), (10,8), (11,8), (12,8), (0,9), (1,9), (2,9), (3,9), (4,9), (5,9), (6,9), (7,9), (8,9), (9,9), (10,9), (11,9), (12,9), (1,10), (2,10), (3,10), (4,10), (5,10), (6,10), (7,10), (8,10), (9,10), (10,10), (11,10), (2,11), (3,11), (4,11), (5,11), (6,11), (7,11), (8,11), (9,11), (10,11), (3,12), (4,12), (5,12), (6,12), (7,12), (8,12), (9,12), (4,13), (5,13), (6,13), (7,13), (8,13), (5,14), (6,14), (7,14), (6,15)]
    for px, py in pixels: pygame.draw.rect(heart_surf, RED_HEART, (px*1.8, py*1.2, 2, 2))
    return heart_surf

def load_image(name, scale=None):
    try:
        image = pygame.image.load(name).convert_alpha()
    except Exception as e:
        print(f"[AVISO] Não foi possível carregar '{name}': {e}")
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
player_img = load_image(asset_path('player.png'), (50, 60))
player_left_img = load_image(asset_path('player_left.png'), (50, 60))
player_right_img = load_image(asset_path('player_right.png'), (50, 60))
enemy_img = load_image(asset_path('enemy.png'), (40, 40))
rock_img = load_image(asset_path('rock.png'), (80, 70))
plane_img = load_image(asset_path('plane.png'), (60, 60)) 
heart_img = load_image(asset_path('heart.png'), (40, 30))
background_img = load_image(asset_path('waterfall.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
boss_img = load_image(asset_path('boss.png'), (200, 150))



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
        self.has_shield = False

    def update(self, current_speed):
        global is_power_active, power_active_timer, power_charges, show_special_alert
        keys = pygame.key.get_pressed()
        
        # --- Lógica do Poder ---
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and power_charges > 0 and not is_power_active:
            is_power_active = True
            power_charges -= 1
            power_active_timer = 180 # 2 segundos a 60 FPS
            show_special_alert = False # O jogador já usou, então o alerta some
            play_sound(snd_special_active)

        if is_power_active:
            power_active_timer -= 1
            if power_active_timer <= 0:
                is_power_active = False
        
        # Resetamos para a imagem central a cada frame
        self.image = self.img_center
        
        # Movimentação Horizontal (Arrow keys ou A/D)
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.rect.left > 40: 
            self.rect.x -= current_speed
            self.image = self.img_left # Muda para imagem da esquerda
            
        elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.rect.right < SCREEN_WIDTH - 40: 
            self.rect.x += current_speed
            self.image = self.img_right # Muda para imagem da direita

        # Movimentação Vertical (Arrow keys ou W/S)
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and self.rect.top > SCREEN_HEIGHT - 180:
            self.rect.y -= max(1, current_speed - 2)
        elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.rect.bottom < SCREEN_HEIGHT - 20:
            self.rect.y += max(1, current_speed - 2)

        # Atualiza a máscara de colisão caso as imagens tenham formatos diferentes
        self.mask = pygame.mask.from_surface(self.image)

        # Lógica de tiro
        if keys[pygame.K_SPACE] and self.cooldown == 0:
            # Se o poder estiver ativo, tiro é SUPER e mais rápido
            s_speed = 12 if is_power_active else 9
            bullet = Bullet(self.rect.centerx, self.rect.top, -1, color=BULLET_PLAYER, speed=s_speed, is_super=is_power_active)
            all_sprites.add(bullet); player_bullets.add(bullet)
            play_sound(snd_shoot)
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
        # Copia a rocha para podermos desenhar rachaduras sem alterar o original
        self.image = rock_img.copy()
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        
        # Sorteia uma posição X e Y segura usando nosso algoritmo de segurança
        safe_x = 50
        proposed_y = random.randint(-200, -80)
        # Tenta achar uma posição horizontal segura 15 vezes
        for _ in range(15):
            test_x = random.randint(50, SCREEN_WIDTH - 130)
            if check_rock_spawning_safety(test_x, proposed_y, rocks):
                safe_x = test_x
                break
        self.rect.x = safe_x
        # Faz a pedra nascer um pouco acima da tela para entrar deslizando
        self.rect.y = proposed_y
        
        # Atributos de Vida
        self.max_health = 3
        self.health = self.max_health

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            return True # Morreu
            
        # Redesenha a rocha limpa e aplica as rachaduras
        self.image = rock_img.copy()
        if self.health == 2:
            pygame.draw.line(self.image, (30, 30, 30), (25, 25), (45, 40), 3)
            pygame.draw.line(self.image, (30, 30, 30), (45, 40), (55, 35), 2)
        elif self.health == 1:
            pygame.draw.line(self.image, (30, 30, 30), (25, 25), (45, 40), 3)
            pygame.draw.line(self.image, (30, 30, 30), (45, 40), (55, 35), 2)
            pygame.draw.line(self.image, (30, 30, 30), (50, 45), (35, 60), 3)
            pygame.draw.line(self.image, (30, 30, 30), (40, 20), (55, 15), 2)
            
        self.mask = pygame.mask.from_surface(self.image)
        return False

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
def draw_key_icon(surface, text, x, y, width=70, height=36):
    """Desenha um ícone estilo tecla de teclado"""
    # Sombra da tecla
    shadow_rect = pygame.Rect(x - width//2, y - height//2 + 3, width, height)
    pygame.draw.rect(surface, (30, 30, 40), shadow_rect, border_radius=6)
    # Corpo da tecla
    key_rect = pygame.Rect(x - width//2, y - height//2, width, height)
    pygame.draw.rect(surface, (50, 55, 70), key_rect, border_radius=6)
    # Borda superior mais clara (efeito 3D)
    top_rect = pygame.Rect(x - width//2 + 2, y - height//2 + 2, width - 4, height - 8)
    pygame.draw.rect(surface, (70, 75, 95), top_rect, border_radius=4)
    # Texto da tecla
    key_font = pygame.font.SysFont('Arial', 14, bold=True)
    key_text = key_font.render(text, True, WHITE)
    key_text_rect = key_text.get_rect(center=(x, y - 1))
    surface.blit(key_text, key_text_rect)

def draw_divider(surface, y, width=300):
    """Desenha uma linha divisória decorativa"""
    cx = SCREEN_WIDTH // 2
    # Gradiente central
    for i in range(width // 2):
        alpha = max(0, 255 - (i * 255 // (width // 2)))
        color = (255, 215, 0, alpha)
        line_surf = pygame.Surface((2, 2), pygame.SRCALPHA)
        line_surf.fill(color)
        surface.blit(line_surf, (cx - i, y))
        surface.blit(line_surf, (cx + i, y))

class WaterParticle:
    """Partícula de água para efeito visual no menu"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-20, -5)
        self.speed = random.uniform(2, 5)
        self.size = random.randint(1, 3)
        self.alpha = random.randint(80, 200)
        self.drift = random.uniform(-0.3, 0.3)
    
    def update(self):
        self.y += self.speed
        self.x += self.drift
        if self.y > SCREEN_HEIGHT:
            self.reset()
    
    def draw(self, surface):
        particle_surf = pygame.Surface((self.size, self.size * 3), pygame.SRCALPHA)
        particle_surf.fill((180, 220, 255, self.alpha))
        surface.blit(particle_surf, (self.x, self.y))

# Cria partículas de água reutilizáveis
menu_particles = [WaterParticle() for _ in range(60)]

def show_tutorial():
    menu_bg_y = 0
    alpha_fade = 0  # Para fade-in

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: return

        # Fundo rolando (cachoeira)
        menu_bg_y = (menu_bg_y + 1) % SCREEN_HEIGHT
        screen.blit(background_img, (0, menu_bg_y))
        screen.blit(background_img, (0, menu_bg_y - SCREEN_HEIGHT))

        # Overlay escuro semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((5, 5, 20, 200))
        screen.blit(overlay, (0, 0))

        # Partículas
        for p in menu_particles:
            p.update()
            p.draw(screen)

        # Fade-in
        if alpha_fade < 255:
            alpha_fade = min(alpha_fade + 5, 255)

        # --- TÍTULO ---
        ticks = pygame.time.get_ticks()
        title_y = 40
        draw_text_shaded(screen, "COMO JOGAR", font_title, YELLOW_TEXT, SCREEN_WIDTH//2, title_y, "center")
        draw_divider(screen, title_y + 30)

        # --- SEÇÃO: CONTROLES ---
        section_y = 100
        draw_text_shaded(screen, "CONTROLES", font_main, YELLOW_TEXT, SCREEN_WIDTH//2, section_y, "center")
        
        small_font = pygame.font.SysFont('Arial', 16)
        
        # Tecla ← →  + descrição
        control_y = section_y + 35
        draw_key_icon(screen, "←", SCREEN_WIDTH//2 - 45, control_y, 40, 30)
        draw_key_icon(screen, "→", SCREEN_WIDTH//2 + 5, control_y, 40, 30)
        desc = small_font.render("Mover", True, (200, 200, 210))
        screen.blit(desc, desc.get_rect(midleft=(SCREEN_WIDTH//2 + 40, control_y)))

        # Tecla ESPAÇO + descrição
        control_y += 38
        draw_key_icon(screen, "ESPAÇO", SCREEN_WIDTH//2 - 20, control_y, 90, 30)
        desc = small_font.render("Atirar", True, (200, 200, 210))
        screen.blit(desc, desc.get_rect(midleft=(SCREEN_WIDTH//2 + 35, control_y)))

        # Tecla SHIFT + descrição
        control_y += 38
        draw_key_icon(screen, "SHIFT", SCREEN_WIDTH//2 - 20, control_y, 80, 30)
        desc = small_font.render("Poder Especial", True, (200, 200, 210))
        screen.blit(desc, desc.get_rect(midleft=(SCREEN_WIDTH//2 + 30, control_y)))

        # --- SEÇÃO: OBJETIVO ---
        draw_divider(screen, control_y + 25)
        obj_y = control_y + 40
        draw_text_shaded(screen, "OBJETIVO", font_main, YELLOW_TEXT, SCREEN_WIDTH//2, obj_y, "center")

        tips = [
            "Destrua inimigos para ganhar pontos",
            "A cada 1500 pts, ganhe um ESPECIAL!",
            "O Especial destrói até pedras!",
            "Colete corações para recuperar vida",
            "Derrote os BOSSES que aparecem!",
        ]
        tip_font = pygame.font.SysFont('Arial', 15)
        for i, tip in enumerate(tips):
            bullet_color = YELLOW_TEXT if i < 3 else RED_HEART if i == 3 else (100, 200, 255)
            pygame.draw.circle(screen, bullet_color, (80, obj_y + 35 + i * 22), 3)
            tip_surf = tip_font.render(tip, True, (220, 220, 230))
            screen.blit(tip_surf, (92, obj_y + 27 + i * 22))

        # --- SEÇÃO: PREVIEW DOS INIMIGOS ---
        enemies_top = obj_y + 155
        draw_divider(screen, enemies_top)
        preview_label_y = enemies_top + 15
        draw_text_shaded(screen, "CONHEÇA OS PERIGOS", font_main, YELLOW_TEXT, SCREEN_WIDTH//2, preview_label_y, "center")

        preview_y = preview_label_y + 35
        enemies_preview = [
            (enemy_img, "Inimigo", 80),
            (rock_img, "Pedra", 190),
            (plane_img, "Avião", 300),
            (boss_img, "BOSS", 400),
        ]
        label_font = pygame.font.SysFont('Arial', 12, bold=True)
        for img, name, px in enemies_preview:
            preview_size = (32, 32) if name != "BOSS" else (46, 32)
            preview = pygame.transform.scale(img, preview_size)
            float_offset = int(2 * math.sin(ticks / 400.0 + px * 0.05))
            img_rect = preview.get_rect(center=(px, preview_y + float_offset))
            screen.blit(preview, img_rect)
            label = label_font.render(name, True, WHITE)
            screen.blit(label, label.get_rect(center=(px, preview_y + 25)))

        # --- BOTÃO ENTER PULSANTE ---
        pulse = abs((ticks % 1200) - 600) / 600.0
        enter_y = SCREEN_HEIGHT - 30
        btn_font = pygame.font.SysFont('Arial', 18, bold=True)
        
        btn_width = 340
        btn_height = 42
        btn_surf = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
        btn_surf.fill((255, 215, 0, int(40 * pulse)))
        btn_rect = btn_surf.get_rect(center=(SCREEN_WIDTH//2, enter_y))
        screen.blit(btn_surf, btn_rect)
        
        border_rect = pygame.Rect(0, 0, btn_width, btn_height)
        border_rect.center = (SCREEN_WIDTH//2, enter_y)
        pygame.draw.rect(screen, (255, 215, 0, int(150 + 105 * pulse)), border_rect, 2, border_radius=8)
        
        enter_color = (
            int(255 * (0.7 + 0.3 * pulse)),
            int(215 * (0.7 + 0.3 * pulse)),
            0
        )
        draw_text_shaded(screen, "Pressione [ ENTER ] para Jogar", btn_font, enter_color, SCREEN_WIDTH//2, enter_y, "center")

        # Fade-in overlay
        if alpha_fade < 255:
            fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surf.fill(BLACK)
            fade_surf.set_alpha(255 - alpha_fade)
            screen.blit(fade_surf, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

class CanyonBlock(pygame.sprite.Sprite):
    def __init__(self, side, y):
        super().__init__()
        self.side = side # 'left' or 'right'
        # Margins are 40px wide, so block width can vary from 35 to 48
        width = random.randint(35, 48)
        height = random.randint(70, 110)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Desenha a rocha base
        color = (55 + random.randint(-5, 5), 55 + random.randint(-5, 5), 60 + random.randint(-5, 5))
        if side == 'left':
            points = [
                (0, 0), (width - 10, 0), (width, height // 3), 
                (width - 4, 2 * height // 3), (width - 12, height), (0, height)
            ]
        else:
            points = [
                (width, 0), (10, 0), (0, height // 3), 
                (4, 2 * height // 3), (12, height), (width, height)
            ]
        pygame.draw.polygon(self.image, color, points)
        
        # Borda rochosa iluminada
        edge_color = (110, 115, 125)
        if side == 'left':
            edge_points = [
                (width - 10, 0), (width, height // 3), 
                (width - 4, 2 * height // 3), (width - 12, height)
            ]
        else:
            edge_points = [
                (10, 0), (0, height // 3), 
                (4, 2 * height // 3), (12, height)
            ]
        pygame.draw.lines(self.image, edge_color, False, edge_points, 3)
        
        # Desenha vegetação (musgo/folhagem)
        moss_color = (34, 120, 50)
        for _ in range(random.randint(1, 3)):
            mx = random.randint(0, width - 15) if side == 'left' else random.randint(15, width)
            my = random.randint(10, height - 20)
            pygame.draw.ellipse(self.image, moss_color, (mx, my, random.randint(8, 14), random.randint(6, 12)))
            
        x_pos = 0 if side == 'left' else SCREEN_WIDTH - width
        self.rect = self.image.get_rect(topleft=(x_pos, y))
        self.mask = pygame.mask.from_surface(self.image)
        
    def update(self, speed):
        self.rect.y += speed
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class WaterFoam:
    def __init__(self):
        self.reset(random_y=True)
    def reset(self, random_y=False):
        self.x = random.randint(45, SCREEN_WIDTH - 45)
        self.y = random.randint(-80, SCREEN_HEIGHT) if random_y else random.randint(-80, -20)
        self.speed = random.uniform(9, 15)
        self.length = random.randint(20, 35)
        self.alpha = random.randint(60, 160)
    def update(self, scroll_speed):
        self.y += self.speed + scroll_speed
        if self.y > SCREEN_HEIGHT:
            self.reset()
    def draw(self, surface):
        surf = pygame.Surface((2, self.length), pygame.SRCALPHA)
        surf.fill((255, 255, 255, self.alpha))
        surface.blit(surf, (self.x, self.y))

class WakeParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.2, 1.2)
        self.vy = random.uniform(1.5, 3.5)
        self.size = random.randint(2, 5)
        self.alpha = 255
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 9
        if self.alpha < 0:
            self.alpha = 0
    def draw(self, surface):
        surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (240, 245, 255, self.alpha), (self.size, self.size), self.size)
        surface.blit(surf, (self.x - self.size, self.y - self.size))

class FloatingText(pygame.sprite.Sprite):
    def __init__(self, text, x, y, color=YELLOW_TEXT, size=20):
        super().__init__()
        # Usamos SysFont seguro
        self.font = pygame.font.SysFont('Arial', size, bold=True)
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.vy = -1.5
        self.alpha = 255
        self.update_image()
        
    def update_image(self):
        text_surf = self.font.render(self.text, True, self.color)
        self.image = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
        temp_surf = text_surf.copy()
        temp_surf.set_alpha(self.alpha)
        self.image.blit(temp_surf, (0, 0))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def update(self, scroll_speed):
        self.y += self.vy + (scroll_speed * 0.1)
        self.alpha -= 8
        if self.alpha <= 0:
            self.kill()
        else:
            self.update_image()

class Whirlpool(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.radius = 45
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(random.randint(80, SCREEN_WIDTH - 80), -60))
        self.angle = 0
        self.pull_radius = 120
        self.max_pull = 2.2
        self.draw_vortex()
        
    def draw_vortex(self):
        self.image.fill((0, 0, 0, 0))
        # Desenha círculos concêntricos e braços de espiral azul-esverdeados
        for i in range(4):
            start_angle = math.radians(self.angle + i * 90)
            points = []
            for r in range(5, self.radius, 3):
                theta = start_angle + (r * 0.1)
                px = self.radius + r * math.cos(theta)
                py = self.radius + r * math.sin(theta)
                points.append((px, py))
            if len(points) > 1:
                # Cor esmaece nas bordas
                alpha = int(180 * (1.0 - len(points)/15.0))
                alpha = max(30, min(180, alpha))
                color = (130, 200, 255, alpha)
                pygame.draw.lines(self.image, color, False, points, 2)
                
    def update(self, scroll_speed):
        self.rect.y += scroll_speed
        self.angle += 8
        self.draw_vortex()
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class ExplosionParticle(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.size = random.randint(3, 7)
        self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (self.size, self.size), self.size)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.alpha = 255
        self.color = color
        
    def update(self, scroll_speed):
        self.rect.x += self.vx
        self.rect.y += self.vy + (scroll_speed * 0.2)
        self.alpha -= 10
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.fill((0, 0, 0, 0))
            r, g, b = self.color[:3]
            pygame.draw.circle(self.image, (r, g, b, self.alpha), (self.size, self.size), self.size)

def spawn_explosion_particles(x, y, count=12):
    colors = [(255, 100, 50), (255, 200, 50), (255, 50, 50), (240, 240, 255)]
    for _ in range(count):
        p = ExplosionParticle(x, y, random.choice(colors))
        effects_group.add(p); all_sprites.add(p)

# --- Classes de Movimento e Efeitos do Rio ---

class RiverCurrent:
    def __init__(self, y=None):
        self.y = y if y is not None else random.randint(-100, SCREEN_HEIGHT)
        self.x_base = random.randint(50, SCREEN_WIDTH - 90)
        self.speed_mult = random.uniform(1.2, 1.8)
        self.length = random.randint(80, 200)
        self.wave_frequency = random.uniform(0.01, 0.03)
        self.wave_amplitude = random.uniform(8, 20)
        self.phase_offset = random.uniform(0, math.pi * 2)
        self.color = (
            random.randint(180, 220),
            random.randint(220, 255),
            255,
            random.randint(25, 70)
        )
        self.width = random.randint(1, 3)

    def update(self, scroll_speed):
        self.y += scroll_speed * self.speed_mult
        if self.y - self.length > SCREEN_HEIGHT:
            self.y = random.randint(-150, -50)
            self.x_base = random.randint(50, SCREEN_WIDTH - 90)
            self.speed_mult = random.uniform(1.2, 1.8)
            self.length = random.randint(80, 200)
            self.phase_offset = random.uniform(0, math.pi * 2)
            self.color = (
                random.randint(180, 220),
                random.randint(220, 255),
                255,
                random.randint(25, 70)
            )
            self.width = random.randint(1, 3)

    def draw(self, surface, time_ticks):
        points = []
        for step in range(0, self.length, 10):
            curr_y = self.y - step
            if 0 <= curr_y <= SCREEN_HEIGHT:
                angle = curr_y * self.wave_frequency + (time_ticks * 0.004) + self.phase_offset
                curr_x = self.x_base + math.sin(angle) * self.wave_amplitude
                curr_x = max(45, min(SCREEN_WIDTH - 45, curr_x))
                points.append((curr_x, curr_y))
        
        if len(points) > 1:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            min_x, max_x = int(min(xs)), int(max(xs))
            min_y, max_y = int(min(ys)), int(max(ys))
            w = max_x - min_x + 6
            h = max_y - min_y + 6
            if w > 0 and h > 0:
                surf = pygame.Surface((w, h), pygame.SRCALPHA)
                offset_points = [(p[0] - min_x + 3, p[1] - min_y + 3) for p in points]
                pygame.draw.lines(surf, self.color, False, offset_points, self.width)
                surface.blit(surf, (min_x - 3, min_y - 3))

class RiverDebris:
    def __init__(self, y=None):
        self.y = y if y is not None else random.randint(-50, SCREEN_HEIGHT)
        self.x_base = random.randint(50, SCREEN_WIDTH - 90)
        self.type = random.choice(['bubble', 'leaf', 'twig'])
        self.speed_mult = random.uniform(1.0, 1.4)
        self.size = random.randint(3, 8)
        self.angle = random.uniform(0, 360)
        self.rot_speed = random.uniform(-2, 2)
        self.wave_amp = random.uniform(4, 12)
        self.wave_freq = random.uniform(0.01, 0.03)
        self.color = self.get_color()

    def get_color(self):
        if self.type == 'bubble':
            return (240, 248, 255, random.randint(40, 100))
        elif self.type == 'leaf':
            return (random.randint(34, 100), random.randint(100, 150), 34, random.randint(120, 200))
        else:
            return (139, 69, 19, random.randint(120, 200))

    def update(self, scroll_speed):
        self.y += scroll_speed * self.speed_mult
        self.angle += self.rot_speed
        if self.y > SCREEN_HEIGHT + 20:
            self.y = random.randint(-100, -20)
            self.x_base = random.randint(50, SCREEN_WIDTH - 90)
            self.type = random.choice(['bubble', 'leaf', 'twig'])
            self.size = random.randint(3, 8)
            self.color = self.get_color()
            self.rot_speed = random.uniform(-2, 2)

    def draw(self, surface, time_ticks):
        angle = self.y * self.wave_freq + (time_ticks * 0.003)
        curr_x = self.x_base + math.sin(angle) * self.wave_amp
        curr_x = max(45, min(SCREEN_WIDTH - 45, curr_x))
        
        if 0 <= self.y <= SCREEN_HEIGHT:
            surf = pygame.Surface((self.size * 2 + 4, self.size * 2 + 4), pygame.SRCALPHA)
            cx, cy = self.size + 2, self.size + 2
            
            if self.type == 'bubble':
                pygame.draw.circle(surf, self.color, (cx, cy), self.size, 1)
            elif self.type == 'leaf':
                rad = math.radians(self.angle)
                dx = self.size * math.cos(rad)
                dy = self.size * math.sin(rad)
                pygame.draw.line(surf, self.color, (cx - dx, cy - dy), (cx + dx, cy + dy), 3)
            else:
                rad = math.radians(self.angle)
                dx = self.size * 1.2 * math.cos(rad)
                dy = self.size * 1.2 * math.sin(rad)
                pygame.draw.line(surf, self.color, (cx - dx, cy - dy), (cx + dx, cy + dy), 2)
                
            surface.blit(surf, (curr_x - cx, self.y - cy))

# --- Lógica Principal ---

# --- Variáveis Globais (estado do jogo) ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
rocks = pygame.sprite.Group()
planes = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
hearts_group = pygame.sprite.Group()
effects_group = pygame.sprite.Group()
canyons_group = pygame.sprite.Group()
whirlpools_group = pygame.sprite.Group()
water_foams = []
wake_particles = []
river_currents = []
river_debris = []
combo_multiplier = 1
combo_count = 0

player = None
score = 0
distance = 0
bg_y = 0
max_lives = 1500
lives = 1500
last_heart_distance = 1000
screen_shake = 0
damage_flash_timer = 0
boss = None
game_over = False

power_charges = 0
is_power_active = False
power_active_timer = 0
last_power_score = 0
show_special_alert = False

# --- Algoritmo de Prevenção de Bloqueio das Pedras ---
def check_rock_spawning_safety(proposed_x, proposed_y, rocks_group):
    # Projeta o intervalo horizontal ocupado pela nova rocha (largura 80)
    new_left = proposed_x
    new_right = proposed_x + 80
    
    # Coleta os intervalos de todas as rochas próximas verticalmente (dentro de 140 pixels)
    intervals = [[new_left, new_right]]
    for r in rocks_group:
        if abs(r.rect.y - proposed_y) < 140:
            intervals.append([r.rect.left, r.rect.right])
            
    # Ordena os intervalos pelo ponto inicial
    intervals.sort(key=lambda x: x[0])
    
    # Mescla os intervalos que se sobrepõem
    merged = []
    for interval in intervals:
        if not merged or merged[-1][1] < interval[0]:
            merged.append(interval)
        else:
            merged[-1][1] = max(merged[-1][1], interval[1])
            
    # Verifica se existe pelo menos um corredor livre com largura >= 110 pixels no espaço jogável (40 a 440)
    current_left = 40
    has_safe_gap = False
    
    for left, right in merged:
        if left > current_left:
            gap = left - current_left
            if gap >= 110:
                has_safe_gap = True
                break
        current_left = max(current_left, right)
        
    if 440 - current_left >= 110:
        has_safe_gap = True
        
    return has_safe_gap

# --- Configurações do Sistema de Fases ---
PHASES = {
    1: {
        "name": "Vale das Cachoeiras",
        "target": 1500,          # Distância para o boss da Fase 1
        "boss_health": 30,
        # Tema visual: DIA ensolarado
        "sky_color": (80, 180, 255, 0),    # Azul claro diurno (sem overlay)
        "rain_intensity": 0,               # Sem chuva
        "lightning": False,
        "description": "DIA - Céu Azul"
    },
    2: {
        "name": "Corredeiras da Tarde",
        "target": 3500,          # Distância para o boss da Fase 2
        "boss_health": 60,
        # Tema visual: TARDE com chuva
        "sky_color": (200, 100, 30, 80),   # Laranja-avermelhado com 80 de alpha
        "rain_intensity": 60,              # 60 gotas na tela
        "lightning": False,
        "description": "TARDE - Chuva"
    },
    3: {
        "name": "Cachoeira da Tempestade",
        "target": 5000,    # Boss aparece aqui na Fase 3
        "boss_health": 100,
        # Tema visual: NOITE com tempestade
        "sky_color": (10, 10, 40, 140),    # Azul-escuro noturno com 140 de alpha
        "rain_intensity": 150,             # Chuva intensa
        "lightning": True,
        "description": "NOITE - Tempestade"
    }
}

# Distância final da Fase 3: quando chega aqui, o barco chega à terra firme!
VICTORY_DISTANCE = 6500  # 6.500m = fim do jogo

# --- Sistema de Clima / Partículas de Chuva ---
class RainDrop:
    """Gota de chuva simples com velocidade diagonal."""
    def __init__(self, phase_num=1):
        self.reset(phase_num)

    def reset(self, phase_num=1):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(-SCREEN_HEIGHT, 0)
        # Fase 3: chuva mais rápida e diagonal
        speed_mult = 2.0 if phase_num == 3 else 1.0
        self.vy = random.uniform(10, 16) * speed_mult
        self.vx = random.uniform(-2, -4) * speed_mult
        self.length = random.randint(8, 18) if phase_num == 3 else random.randint(5, 12)
        self.alpha = random.randint(120, 200)
        self.phase = phase_num

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.y > SCREEN_HEIGHT or self.x < -10:
            self.reset(self.phase)

    def draw(self, surface):
        color = (150, 200, 255, self.alpha) if self.phase < 3 else (180, 180, 220, self.alpha)
        end_x = int(self.x + self.vx * 0.6)
        end_y = int(self.y + self.vy * 0.6)
        pygame.draw.line(surface, color[:3], (int(self.x), int(self.y)), (end_x, end_y), 1)

# Variáveis globais de clima
rain_drops = []
lightning_timer = 0
lightning_flash = 0

current_phase = 1
phase_transition_timer = 0
phase_transition_text1 = ""
phase_transition_text2 = ""
max_lives = 1500

def start_phase_transition(phase_num):
    global current_phase, phase_transition_timer, phase_transition_text1, phase_transition_text2, lives, max_lives
    # Garante que phase_num não ultrapasse 3
    phase_num = min(phase_num, 3)
    current_phase = phase_num
    phase_transition_timer = 180  # 3 segundos a 60 FPS
    
    # Texto e ícone de cada fase
    phase_icons = {1: "☀ DIA", 2: "🌅 TARDE", 3: "🌩 TEMPESTADE"}
    icon = phase_icons.get(phase_num, "")
    
    if phase_num == 1:
        phase_transition_text1 = "PREPARE-SE!"
    else:
        phase_transition_text1 = f"FASE {phase_num - 1} CONCLUÍDA!"
    phase_transition_text2 = f"{icon}  FASE {phase_num}: {PHASES[phase_num]['name']}"
    
    if phase_num > 1:
        lives = min(lives + 2, max_lives)
        play_sound(snd_phase_clear)
        if player:
            ft = FloatingText("+2 VIDAS!", player.rect.centerx, player.rect.top - 50, color=(100, 255, 100), size=24)
            effects_group.add(ft)
            all_sprites.add(ft)
            
        # Partículas de celebração coloridas no centro da tela
        for _ in range(30):
            color = (random.randint(100, 255), random.randint(150, 255), random.randint(150, 255))
            p = ExplosionParticle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, color)
            effects_group.add(p)
            all_sprites.add(p)


def increase_combo(amount=1):
    global combo_count, combo_multiplier
    combo_count += amount
    new_mult = min(5, 1 + combo_count // 5)
    if new_mult > combo_multiplier:
        ft_up = FloatingText(f"COMBO x{new_mult}!", player.rect.centerx, player.rect.top - 40, color=(100, 255, 100), size=24)
        effects_group.add(ft_up); all_sprites.add(ft_up)
    combo_multiplier = new_mult

def reset_game():
    global all_sprites, enemies, rocks, planes, player_bullets, enemy_bullets, hearts_group, effects_group
    global player, score, distance, bg_y, lives, last_heart_distance, screen_shake, boss
    global power_charges, is_power_active, power_active_timer, last_power_score
    global show_special_alert
    global canyons_group, water_foams, wake_particles
    global combo_multiplier, combo_count
    global whirlpools_group, damage_flash_timer
    global river_currents, river_debris
    global current_phase, phase_transition_timer, phase_transition_text1, phase_transition_text2, max_lives
    global rain_drops, lightning_timer, lightning_flash

    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    planes = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    hearts_group = pygame.sprite.Group() 
    effects_group = pygame.sprite.Group()
    canyons_group = pygame.sprite.Group()
    whirlpools_group = pygame.sprite.Group()
    show_special_alert = False
    damage_flash_timer = 0
    
    # Inicializa as espumas de correnteza
    water_foams = [WaterFoam() for _ in range(25)]
    wake_particles = []
    combo_multiplier = 1
    combo_count = 0
    
    # Inicializa as correntes e detritos do rio
    river_currents = [RiverCurrent() for _ in range(12)]
    river_debris = [RiverDebris() for _ in range(15)]
    
    # Preenche a tela inicial com blocos de canyon nas margens
    y = -100
    while y < SCREEN_HEIGHT:
        canyons_group.add(CanyonBlock('left', y))
        canyons_group.add(CanyonBlock('right', y))
        y += 75
    

    score = 0; 
    distance = 0; 
    bg_y = 0; 
    
    max_lives = 6
    lives = 3 # Começa com 3 vidas
    last_heart_distance = 0 
    screen_shake = 0
    boss = None

    power_charges = 0        # Quantos "Shifts" o jogador tem
    power_active_timer = 0   # Tempo restante do poder (em frames)
    is_power_active = False  # Estado do poder
    last_power_score = 0     # Auxiliar para saber quando dar o próximo poder

    # Reinicia clima
    rain_drops = []
    lightning_timer = 0
    lightning_flash = 0

    player = Player()
    all_sprites.add(player)
    
    # Inicia a transição da primeira fase
    start_phase_transition(1)

def show_victory(final_score, final_distance):
    """Cena de vitória animada: barco chega, personagem pula e corre para a montanha."""

    # ── Fogos de Artifício ──────────────────────────────────────────────────
    class Firework:
        def __init__(self):
            self.x = random.randint(50, SCREEN_WIDTH - 50)
            self.y = random.randint(40, SCREEN_HEIGHT // 2)
            self.color = (
                random.randint(180, 255),
                random.randint(100, 255),
                random.randint(80,  255)
            )
            self.trail = []   # trilha de lançamento
            self.particles = []
            self.done = False
            self._burst()

        def _burst(self):
            for _ in range(55):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(1.0, 5.5)
                self.particles.append({
                    'x': float(self.x), 'y': float(self.y),
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed - 1.0,
                    'life': random.randint(30, 70),
                    'max_life': 70,
                    'size': random.randint(1, 3)
                })

        def update(self):
            alive = []
            for p in self.particles:
                p['x']  += p['vx']
                p['y']  += p['vy']
                p['vy'] += 0.10
                p['vx'] *= 0.96
                p['life'] -= 1
                if p['life'] > 0:
                    alive.append(p)
            self.particles = alive
            if not self.particles:
                self.done = True

        def draw(self, surf):
            for p in self.particles:
                frac = p['life'] / p['max_life']
                cr = min(255, int(self.color[0] * frac + 255 * (1 - frac)))
                cg = min(255, int(self.color[1] * frac))
                cb = min(255, int(self.color[2] * frac))
                alpha_c = int(230 * frac)
                s = pygame.Surface((p['size']*2+1, p['size']*2+1), pygame.SRCALPHA)
                pygame.draw.circle(s, (cr, cg, cb, alpha_c), (p['size'], p['size']), p['size'])
                surf.blit(s, (int(p['x']) - p['size'], int(p['y']) - p['size']))

    # ── Construção dos fundos estáticos ────────────────────────────────────
    W, H = SCREEN_WIDTH, SCREEN_HEIGHT

    # Céu estrelado
    sky = pygame.Surface((W, H))
    for row in range(H):
        t = row / H
        r = int(5  + 20 * t)
        g = int(5  + 15 * t)
        b = int(25 + 40 * t)
        pygame.draw.line(sky, (r, g, b), (0, row), (W, row))

    # Estrelas fixas
    stars = [(random.randint(0, W), random.randint(0, H * 2 // 3),
              random.randint(1, 2), random.randint(150, 255)) for _ in range(80)]
    for sx, sy, sr, sb in stars:
        pygame.draw.circle(sky, (sb, sb, sb), (sx, sy), sr)

    # Lua
    pygame.draw.circle(sky, (240, 240, 200), (W - 75, 65), 38)
    pygame.draw.circle(sky, (5,   5,   28),  (W - 55, 52), 36)

    # Cenário: montanhas + terra + água
    scene = pygame.Surface((W, H), pygame.SRCALPHA)

    # Montanhas fundo (mais claras = mais distantes)
    pygame.draw.polygon(scene, (35, 50, 35), [
        (0, H), (W//2 - 30, H//2 - 60), (W//2 + 90, H), (0, H)
    ])
    pygame.draw.polygon(scene, (50, 68, 50), [
        (W//2 + 10, H), (W - 50, H//2 + 20), (W, H)
    ])
    pygame.draw.polygon(scene, (28, 42, 28), [
        (W//4, H), (W//4 + 60, H//2 + 10), (W//4 + 120, H)
    ])

    # Neve no pico da montanha principal
    pygame.draw.polygon(scene, (220, 230, 240), [
        (W//2 - 30, H//2 - 60),
        (W//2 - 10, H//2 - 25),
        (W//2 + 10, H//2 - 25),
        (W//2 + 18, H//2 - 60),
    ])

    # Chão / margem (faixa verde)
    shore_y = H - 80
    pygame.draw.rect(scene, (25, 80, 25), (0, shore_y, W, H - shore_y))
    # Faixa de areia/margem do rio
    pygame.draw.rect(scene, (160, 130, 80), (0, shore_y - 12, W, 14))

    # ── Funções para desenhar barco e personagem ───────────────────────────
    def draw_boat(surf, bx, by):
        """Barquinho com casco, janela e mastro."""
        # Casco (hull)
        pygame.draw.polygon(surf, (80, 50, 20), [
            (bx, by + 22), (bx + 60, by + 22),
            (bx + 64, by + 32), (bx - 4, by + 32)
        ])
        # Superestrutura
        pygame.draw.rect(surf, (140, 95, 40), (bx + 8, by, 44, 22))
        # Janela
        pygame.draw.circle(surf, (100, 200, 220), (bx + 30, by + 11), 6)
        pygame.draw.circle(surf, (180, 230, 240), (bx + 28, by + 9), 3)
        # Mastro + bandeira
        pygame.draw.line(surf, (60, 35, 10), (bx + 32, by), (bx + 32, by - 28), 2)
        pygame.draw.polygon(surf, (220, 50, 50), [
            (bx + 32, by - 28), (bx + 48, by - 20), (bx + 32, by - 12)
        ])

    def draw_char(surf, cx, cy, frame, jumping=False, vy=0):
        """Personagem estilizado: cabeça + corpo + pernas animadas."""
        # Sombra
        pygame.draw.ellipse(surf, (0, 0, 0, 80),
                            (cx - 10, cy + 28, 20, 6))
        # Cabeça
        pygame.draw.circle(surf, (240, 190, 130), (cx, cy), 8)
        # Chapéu
        pygame.draw.rect(surf, (50, 30, 10), (cx - 9, cy - 12, 18, 5))
        pygame.draw.rect(surf, (70, 45, 15), (cx - 5, cy - 19, 10, 8))
        # Corpo
        pygame.draw.rect(surf, (30, 100, 180), (cx - 6, cy + 8, 12, 14))
        # Braços: se pulando, braços levantados
        if jumping:
            pygame.draw.line(surf, (240, 190, 130), (cx - 6, cy + 10), (cx - 14, cy + 2), 2)
            pygame.draw.line(surf, (240, 190, 130), (cx + 6, cy + 10), (cx + 14, cy + 2), 2)
        else:
            swing = math.sin(frame * 0.3) * 8
            pygame.draw.line(surf, (240, 190, 130), (cx - 6, cy + 10), (cx - 12, cy + 18 + swing), 2)
            pygame.draw.line(surf, (240, 190, 130), (cx + 6, cy + 10), (cx + 12, cy + 18 - swing), 2)
        # Pernas
        leg = math.sin(frame * 0.4) * 7 if not jumping else 10
        pygame.draw.line(surf, (20, 60, 120), (cx - 3, cy + 22), (cx - 6, cy + 30 + leg), 3)
        pygame.draw.line(surf, (20, 60, 120), (cx + 3, cy + 22), (cx + 6, cy + 30 - leg), 3)

    # ── Fontes ─────────────────────────────────────────────────────────────
    try:
        font_big  = pygame.font.SysFont('Arial', 52, bold=True)
        font_med  = pygame.font.SysFont('Arial', 20)
        font_sub  = pygame.font.SysFont('Arial', 16)
    except:
        font_big  = pygame.font.Font(None, 68)
        font_med  = pygame.font.Font(None, 26)
        font_sub  = pygame.font.Font(None, 22)

    # ── Estado da animação ─────────────────────────────────────────────────
    # ESTADO 0: barco chegando da direita
    # ESTADO 1: personagem pula do barco (arco parabólico)
    # ESTADO 2: personagem corre para a montanha
    # ESTADO 3: fogos + texto final

    state      = 0
    frame      = 0

    boat_x     = float(W + 80)           # barco chega da direita
    boat_y     = float(shore_y - 35)     # nível da água/margem
    boat_stop  = float(W // 2 + 20)      # onde o barco para

    # Personagem: começa no barco
    char_x     = float(boat_stop + 30)
    char_y     = float(boat_y - 10)
    char_vy    = 0.0
    char_ground = float(shore_y - 32)    # altura do chão

    run_target = float(W // 4)           # destino: em direção à montanha

    fireworks  = []
    fw_timer   = 0
    alpha_fade = 0
    text_delay = 0

    clock_v = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if state >= 3:
                    running = False

        frame += 1

        # ── Fundo ──
        screen.blit(sky, (0, 0))
        screen.blit(scene, (0, 0))

        # Água animada (ondas sinusoidais)
        water_y = shore_y - 10
        water_surf = pygame.Surface((W, H - water_y), pygame.SRCALPHA)
        for wx in range(0, W, 3):
            wy = int(4 * math.sin((wx + frame * 2) * 0.06))
            pygame.draw.line(water_surf, (30, 100, 180, 160), (wx, 10 + wy), (wx, H - water_y), 1)
        # Reflexo da lua
        for i in range(5):
            rx = W - 75 + random.randint(-8, 8)
            ry = 8 + i * 5
            pygame.draw.line(water_surf, (220, 220, 150, 80), (rx - 15, ry), (rx + 15, ry), 1)
        screen.blit(water_surf, (0, water_y))

        # ── ESTADO 0: barco chegando ──
        if state == 0:
            boat_x -= 2.8
            if boat_x <= boat_stop:
                boat_x = boat_stop
                state = 1
                char_x = boat_stop + 30
                char_y = boat_y - 10
                char_vy = -9.0   # impulso do salto
            draw_boat(screen, int(boat_x), int(boat_y))

        # ── ESTADO 1: personagem pula do barco ──
        elif state == 1:
            draw_boat(screen, int(boat_x), int(boat_y))
            char_x += 3.5
            char_y += char_vy
            char_vy += 0.55   # gravidade
            draw_char(screen, int(char_x), int(char_y), frame, jumping=True, vy=char_vy)
            if char_y >= char_ground:
                char_y = char_ground
                char_vy = 0
                state = 2

        # ── ESTADO 2: corre para a montanha ──
        elif state == 2:
            draw_boat(screen, int(boat_x), int(boat_y))
            if char_x > run_target:
                char_x -= 2.2
                char_y = char_ground - abs(math.sin(frame * 0.35)) * 4   # pequenos pulos de corrida
            else:
                state = 3
                text_delay = frame
            draw_char(screen, int(char_x), int(char_y), frame)

        # ── ESTADO 3: fogos + texto ──
        elif state >= 3:
            draw_boat(screen, int(boat_x), int(boat_y))
            draw_char(screen, int(char_x), int(char_y), frame)

            # Fogos
            fw_timer -= 1
            if fw_timer <= 0:
                fireworks.append(Firework())
                fireworks.append(Firework())
                fw_timer = random.randint(15, 40)

            fw_surf = pygame.Surface((W, H), pygame.SRCALPHA)
            for fw in fireworks:
                fw.update(); fw.draw(fw_surf)
            fireworks = [fw for fw in fireworks if not fw.done]
            screen.blit(fw_surf, (0, 0))

            # Texto com fade-in
            alpha_fade = min(alpha_fade + 4, 255)

            txt1 = font_big.render("VOCÊ CHEGOU!", True, (255, 220, 50))
            s1 = pygame.Surface(txt1.get_size(), pygame.SRCALPHA)
            s1.blit(txt1, (0, 0)); s1.set_alpha(alpha_fade)
            screen.blit(s1, (W // 2 - txt1.get_width() // 2, H // 4 - 20))

            txt2 = font_med.render(f"Score: {final_score}   •   Distância: {final_distance}m", True, (200, 220, 255))
            s2 = pygame.Surface(txt2.get_size(), pygame.SRCALPHA)
            s2.blit(txt2, (0, 0)); s2.set_alpha(alpha_fade)
            screen.blit(s2, (W // 2 - txt2.get_width() // 2, H // 4 + 45))

            if alpha_fade >= 255 and (frame // 30) % 2 == 0:
                txt3 = font_sub.render("Pressione ENTER para jogar novamente", True, (160, 160, 160))
                screen.blit(txt3, (W // 2 - txt3.get_width() // 2, H // 2 + 10))

        pygame.display.flip()
        clock_v.tick(FPS)


def show_game_over(final_score, final_distance):
    """Tela de Game Over animada com estatísticas"""

    menu_bg_y = 0
    alpha_fade = 0
    start_ticks = pygame.time.get_ticks()
    
    # Fontes
    try:
        font_huge = pygame.font.SysFont('Arial', 52, bold=True)
        font_stats = pygame.font.SysFont('Arial', 22, bold=True)
        font_sub = pygame.font.SysFont('Arial', 18)
        font_label = pygame.font.SysFont('Arial', 16)
    except:
        font_huge = pygame.font.Font(None, 64)
        font_stats = pygame.font.Font(None, 28)
        font_sub = pygame.font.Font(None, 24)
        font_label = pygame.font.Font(None, 20)
    
    # Calcula estatísticas
    bosses_killed = final_score // 5000  # Estimativa baseada no score
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                # Pequena pausa antes de sair
                return
        
        ticks = pygame.time.get_ticks()
        elapsed = ticks - start_ticks
        
        # Fundo rolando (cachoeira mais lenta, sombria)
        menu_bg_y = (menu_bg_y + 1) % SCREEN_HEIGHT
        screen.blit(background_img, (0, menu_bg_y))
        screen.blit(background_img, (0, menu_bg_y - SCREEN_HEIGHT))
        
        # Overlay vermelho escuro (tom de derrota)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        # Gradiente: vermelho escuro no topo, preto embaixo
        for row in range(SCREEN_HEIGHT):
            progress = row / SCREEN_HEIGHT
            r = int(40 * (1 - progress))
            alpha = int(180 + 60 * progress)
            pygame.draw.line(overlay, (r, 5, 10, alpha), (0, row), (SCREEN_WIDTH, row))
        screen.blit(overlay, (0, 0))
        
        # Partículas (mais lentas e vermelhas)
        for p in menu_particles:
            p.update()
            # Desenha em vermelho/laranja
            particle_surf = pygame.Surface((p.size, p.size * 3), pygame.SRCALPHA)
            particle_surf.fill((255, 80, 60, p.alpha // 2))
            screen.blit(particle_surf, (p.x, p.y))
        
        # Fade-in
        if alpha_fade < 255:
            alpha_fade = min(alpha_fade + 3, 255)
        
        # --- ÍCONE DE CAVEIRA / X ---
        skull_y = 100
        # Círculo vermelho pulsante atrás
        skull_pulse = 0.7 + 0.3 * abs((ticks % 1500) - 750) / 750.0
        glow_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        glow_color = (255, 40, 40, int(40 * skull_pulse))
        pygame.draw.circle(glow_surf, glow_color, (60, 60), 60)
        screen.blit(glow_surf, glow_surf.get_rect(center=(SCREEN_WIDTH//2, skull_y)))
        
        # X grande
        x_size = 30
        cx, cy = SCREEN_WIDTH//2, skull_y
        pygame.draw.line(screen, (220, 30, 30), (cx - x_size, cy - x_size), (cx + x_size, cy + x_size), 6)
        pygame.draw.line(screen, (220, 30, 30), (cx + x_size, cy - x_size), (cx - x_size, cy + x_size), 6)
        # Borda branca do X
        pygame.draw.line(screen, (255, 80, 80), (cx - x_size, cy - x_size), (cx + x_size, cy + x_size), 3)
        pygame.draw.line(screen, (255, 80, 80), (cx + x_size, cy - x_size), (cx - x_size, cy + x_size), 3)
        
        # --- TÍTULO "FIM DE JOGO" ---
        title_y = 170
        # Glow vermelho
        glow_surf2 = pygame.Surface((380, 70), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf2, (255, 30, 30, int(25 * skull_pulse)), (0, 0, 380, 70))
        screen.blit(glow_surf2, glow_surf2.get_rect(center=(SCREEN_WIDTH//2, title_y)))
        
        draw_text_shaded(screen, "FIM DE JOGO", font_huge, (255, 60, 60), SCREEN_WIDTH//2, title_y, "center")
        
        # Linha decorativa vermelha
        div_y = title_y + 40
        cx = SCREEN_WIDTH // 2
        for i in range(120):
            a = max(0, 255 - (i * 255 // 120))
            line_surf = pygame.Surface((2, 2), pygame.SRCALPHA)
            line_surf.fill((255, 60, 60, a))
            screen.blit(line_surf, (cx - i, div_y))
            screen.blit(line_surf, (cx + i, div_y))
        
        # --- ESTATÍSTICAS ---
        stats_y = 260
        
        # Caixas de estatísticas
        stats = [
            ("PONTUAÇÃO", f"{final_score:,}".replace(',', '.'), YELLOW_TEXT),
            ("DISTÂNCIA", f"{final_distance}m", (100, 200, 255)),
        ]
        
        box_width = 180
        box_height = 80
        total_width = len(stats) * box_width + (len(stats) - 1) * 20
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, (label, value, color) in enumerate(stats):
            bx = start_x + i * (box_width + 20)
            by = stats_y
            
            # Fundo da caixa
            box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            box_surf.fill((20, 20, 35, 180))
            screen.blit(box_surf, (bx, by))
            
            # Borda
            pygame.draw.rect(screen, (60, 60, 80), (bx, by, box_width, box_height), 2, border_radius=8)
            # Borda superior colorida
            pygame.draw.line(screen, color, (bx + 8, by), (bx + box_width - 8, by), 2)
            
            # Label
            lbl = font_label.render(label, True, (150, 150, 170))
            screen.blit(lbl, lbl.get_rect(center=(bx + box_width//2, by + 25)))
            
            # Valor (animação de contagem)
            val_surf = font_stats.render(value, True, color)
            screen.blit(val_surf, val_surf.get_rect(center=(bx + box_width//2, by + 55)))
        
        # --- MENSAGEM MOTIVACIONAL ---
        msg_y = 380
        if final_score >= 10000:
            msg = "Incrível! Você é uma lenda!"
            msg_color = YELLOW_TEXT
        elif final_score >= 5000:
            msg = "Muito bom! Continue assim!"
            msg_color = (100, 255, 100)
        elif final_score >= 1000:
            msg = "Bom trabalho! Tente ir mais longe!"
            msg_color = (100, 200, 255)
        else:
            msg = "Não desista! Tente novamente!"
            msg_color = (200, 200, 200)
        
        msg_surf = font_sub.render(msg, True, msg_color)
        screen.blit(msg_surf, msg_surf.get_rect(center=(SCREEN_WIDTH//2, msg_y)))
        
        # --- PREVIEW DO PLAYER (caído/morto) ---
        preview_y = 440
        dead_player = pygame.transform.scale(player_img, (50, 60))
        # Rotaciona o player para parecer que caiu
        dead_player = pygame.transform.rotate(dead_player, 90)
        dead_player.set_alpha(int(150 + 50 * skull_pulse))
        screen.blit(dead_player, dead_player.get_rect(center=(SCREEN_WIDTH//2, preview_y)))
        
        # --- BOTÃO ENTER PULSANTE ---
        pulse = abs((ticks % 1500) - 750) / 750.0
        enter_y = SCREEN_HEIGHT - 80
        btn_font = pygame.font.SysFont('Arial', 18, bold=True)
        
        # Só mostra o botão depois de 1 segundo
        if elapsed > 1000:
            btn_width = 380
            btn_height = 46
            btn_surf = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
            btn_surf.fill((255, 60, 60, int(20 + 20 * pulse)))
            btn_rect = btn_surf.get_rect(center=(SCREEN_WIDTH//2, enter_y))
            screen.blit(btn_surf, btn_rect)
            
            border_rect = pygame.Rect(0, 0, btn_width, btn_height)
            border_rect.center = (SCREEN_WIDTH//2, enter_y)
            pygame.draw.rect(screen, (255, 80, 80), border_rect, 2, border_radius=10)
            
            enter_color = (
                int(255 * (0.7 + 0.3 * pulse)),
                int(60 * (0.7 + 0.3 * pulse)),
                int(60 * (0.7 + 0.3 * pulse))
            )
            draw_text_shaded(screen, "Pressione [ ENTER ] para Continuar", btn_font, enter_color, SCREEN_WIDTH//2, enter_y, "center")
        
        # Fade-in overlay
        if alpha_fade < 255:
            fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surf.fill(BLACK)
            fade_surf.set_alpha(255 - alpha_fade)
            screen.blit(fade_surf, (0, 0))
        
        pygame.display.flip()
        clock.tick(FPS)

def show_menu():
    menu_bg_y = 0
    alpha_fade = 0

    # Título com fonte maior
    try:
        font_huge = pygame.font.SysFont('Arial', 56, bold=True)
        font_sub = pygame.font.SysFont('Arial', 18)
    except:
        font_huge = pygame.font.Font(None, 72)
        font_sub = pygame.font.Font(None, 24)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN: return

        ticks = pygame.time.get_ticks()

        # Fundo rolando (cachoeira animada)
        menu_bg_y = (menu_bg_y + 2) % SCREEN_HEIGHT
        screen.blit(background_img, (0, menu_bg_y))
        screen.blit(background_img, (0, menu_bg_y - SCREEN_HEIGHT))

        # Overlay com gradiente escuro (mais escuro embaixo)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for row in range(SCREEN_HEIGHT):
            alpha = int(120 + 100 * (row / SCREEN_HEIGHT))
            pygame.draw.line(overlay, (5, 5, 20, alpha), (0, row), (SCREEN_WIDTH, row))
        screen.blit(overlay, (0, 0))

        # Partículas de água
        for p in menu_particles:
            p.update()
            p.draw(screen)

        # --- TÍTULO COM GLOW ---
        title_center_y = SCREEN_HEIGHT // 2 - 80

        # Efeito glow atrás do título
        glow_pulse = 0.7 + 0.3 * abs((ticks % 2000) - 1000) / 1000.0
        glow_surf = pygame.Surface((350, 100), pygame.SRCALPHA)
        glow_radius = 80
        glow_color = (255, 215, 0, int(30 * glow_pulse))
        pygame.draw.ellipse(glow_surf, glow_color, (0, 0, 350, 100))
        glow_rect = glow_surf.get_rect(center=(SCREEN_WIDTH//2, title_center_y + 10))
        screen.blit(glow_surf, glow_rect)

        # Texto "DESCIDA"
        draw_text_shaded(screen, "DESCIDA", font_huge, WHITE, SCREEN_WIDTH//2, title_center_y - 30, "center")
        # Texto "PERIGOSA" (com pulsação sutil)
        yellow_pulse = (
            int(255 * (0.85 + 0.15 * glow_pulse)),
            int(215 * (0.85 + 0.15 * glow_pulse)),
            0
        )
        draw_text_shaded(screen, "PERIGOSA", font_huge, yellow_pulse, SCREEN_WIDTH//2, title_center_y + 40, "center")

        # Linha decorativa
        draw_divider(screen, title_center_y + 80, 250)

        # Subtítulo
        sub_color = (150, 180, 220)
        sub_text = font_sub.render("Uma aventura na cachoeira!", True, sub_color)
        screen.blit(sub_text, sub_text.get_rect(center=(SCREEN_WIDTH//2, title_center_y + 100)))

        # --- PREVIEW DO PLAYER ---
        player_preview_y = SCREEN_HEIGHT // 2 + 70
        # Flutuação suave
        float_y = int(4 * math.sin(ticks / 400.0))
        
        preview_player = pygame.transform.scale(player_img, (60, 72))
        player_rect = preview_player.get_rect(center=(SCREEN_WIDTH//2, player_preview_y + float_y))
        screen.blit(preview_player, player_rect)

        # --- BOTÃO ENTER ANIMADO ---
        pulse = abs((ticks % 1500) - 750) / 750.0
        enter_y = SCREEN_HEIGHT - 100
        btn_font = pygame.font.SysFont('Arial', 18, bold=True)

        btn_width = 300
        btn_height = 46
        btn_surf = pygame.Surface((btn_width, btn_height), pygame.SRCALPHA)
        btn_surf.fill((255, 215, 0, int(25 + 25 * pulse)))
        btn_rect = btn_surf.get_rect(center=(SCREEN_WIDTH//2, enter_y))
        screen.blit(btn_surf, btn_rect)

        border_rect = pygame.Rect(0, 0, btn_width, btn_height)
        border_rect.center = (SCREEN_WIDTH//2, enter_y)
        pygame.draw.rect(screen, YELLOW_TEXT, border_rect, 2, border_radius=10)

        enter_color = (
            int(255 * (0.7 + 0.3 * pulse)),
            int(215 * (0.7 + 0.3 * pulse)),
            0
        )
        draw_text_shaded(screen, "Pressione [ ENTER ]", btn_font, enter_color, SCREEN_WIDTH//2, enter_y, "center")

        # Crédito sutil no rodapé
        credit_font = pygame.font.SysFont('Arial', 12)
        credit = credit_font.render("Feito com Pygame", True, (80, 80, 100))
        screen.blit(credit, credit.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 25)))

        # Fade-in
        if alpha_fade < 255:
            alpha_fade = min(alpha_fade + 4, 255)
            fade_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            fade_surf.fill(BLACK)
            fade_surf.set_alpha(255 - alpha_fade)
            screen.blit(fade_surf, (0, 0))

        pygame.display.flip()
        clock.tick(FPS)

# --- Início do Jogo ---
bg_y = 0
show_menu()
show_tutorial()
reset_game()
game_over = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()
    
    # Se morreu, mostra tela de game over e volta ao menu
    if game_over:
        show_game_over(score, distance)
        show_menu()
        show_tutorial()
        reset_game()
        game_over = False
        continue

    if not game_over:
        # A distância só aumenta se não houver chefão e não estiver em transição de fase
        if boss is None and phase_transition_timer <= 0:
            distance += 1 
            
        # Variáveis de dificuldade suavizadas (mais fáceis e equilibradas)
        scroll_speed = 3 + (distance // 1500)
        current_player_speed = min(6 + (distance // 2500), 10) # Começa mais rápido e ágil (6)
        current_fire_rate = max(120 - (distance // 60), 20) # Inimigos atiram menos no início
        current_enemy_bullet_speed = min(5 + (distance // 600), 10) # Balas inimigas mais lentas
        rock_spawn_chance = min(0.015 + (distance / 16000), 0.10) # Menos pedras na tela
        
        # Updates
        player.update(current_player_speed)
        enemies.update(current_fire_rate, current_enemy_bullet_speed, scroll_speed, player.rect)        
        planes.update(distance) 
        rocks.update(scroll_speed)
        hearts_group.update(scroll_speed)
        player_bullets.update()
        enemy_bullets.update()
        effects_group.update(scroll_speed)
        canyons_group.update(scroll_speed)
        whirlpools_group.update(scroll_speed)
        
        for current in river_currents:
            current.update(scroll_speed)
            
        for debris in river_debris:
            debris.update(scroll_speed)
        
        # Física de atração do redemoinho
        for w in whirlpools_group:
            dx = w.rect.centerx - player.rect.centerx
            dy = w.rect.centery - player.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            if dist < w.pull_radius and dist > 5:
                force = (w.pull_radius - dist) / w.pull_radius * w.max_pull
                player.rect.x += int((dx / dist) * force)
                player.rect.y += int((dy / dist) * force)
                # Limita dentro do canyon
                player.rect.x = max(40, min(SCREEN_WIDTH - 40 - player.rect.width, player.rect.x))
                player.rect.y = max(0, min(SCREEN_HEIGHT - player.rect.height, player.rect.y))
        
        for foam in water_foams:
            foam.update(scroll_speed)
            
        for p in wake_particles:
            p.update()
        wake_particles = [p for p in wake_particles if p.alpha > 0]
        
        # Cria rastro atrás do barco/jogador
        if random.random() < 0.5:
            wake_particles.append(WakeParticle(player.rect.centerx + random.randint(-12, 12), player.rect.bottom - 4))
            
        # Spawn de novos blocos de canyon nas laterais
        max_left_y = min([c.rect.top for c in canyons_group if c.side == 'left'] or [0])
        if max_left_y > -80:
            canyons_group.add(CanyonBlock('left', max_left_y - 75))
            canyons_group.add(CanyonBlock('right', max_left_y - 75))
        
        bg_y = (bg_y + scroll_speed) % SCREEN_HEIGHT

        # --- Spawns ---
        # Só spawna obstáculos se não houver boss ativo e não estiver em transição de fase
        if boss is None and phase_transition_timer <= 0:
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

            if distance > 500 and len(whirlpools_group) < 2 and random.random() < 0.006:
                w = Whirlpool()
                whirlpools_group.add(w); all_sprites.add(w)

        if distance - last_heart_distance > 2000:
            h = HeartItem(); hearts_group.add(h); all_sprites.add(h)
            last_heart_distance = distance

        # --- Colisões ---
        
        # Coleta do Coração / Powerup de Vida ou Escudo
        if pygame.sprite.spritecollide(player, hearts_group, True, pygame.sprite.collide_mask):
            if lives < max_lives:
                lives += 1
                score += 500
                play_sound(snd_powerup)
                ft_heart = FloatingText("+1 VIDA!", player.rect.centerx, player.rect.top - 30, color=(100, 255, 100), size=20)
                effects_group.add(ft_heart); all_sprites.add(ft_heart)
            else:
                if not player.has_shield:
                    player.has_shield = True
                    play_sound(snd_shield_up)
                    ft_shield = FloatingText("ESCUDO ATIVADO!", player.rect.centerx, player.rect.top - 30, color=(100, 200, 255), size=20)
                    effects_group.add(ft_shield); all_sprites.add(ft_shield)
                else:
                    score += 1000
                    play_sound(snd_powerup)
                    ft_pts = FloatingText("+1000 Pontos!", player.rect.centerx, player.rect.top - 30, color=YELLOW_TEXT, size=20)
                    effects_group.add(ft_pts); all_sprites.add(ft_pts)

        # Colisões do player com pedras — a pedra SEMPRE quebra ao colidir,
        # mesmo durante invencibilidade (só o dano ao jogador é ignorado).
        rock_hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_mask)
        if rock_hits:
            # Animação de quebra para todas as pedras atingidas
            for r in rock_hits:
                expl = RockExplosion(r.rect.centerx, r.rect.centery, rock_break_imgs)
                effects_group.add(expl); all_sprites.add(expl)
                spawn_explosion_particles(r.rect.centerx, r.rect.centery, 8)
                # Mata inimigo ancorado na pedra
                for e in list(enemies):
                    if e.anchor == r:
                        e.kill()
                        spawn_explosion_particles(e.rect.centerx, e.rect.centery, 5)
            
            # Só aplica dano ao jogador se não estiver invencível
            if player.invincible <= 0:
                if player.has_shield:
                    player.has_shield = False
                    player.invincible = 45
                    screen_shake = 8
                    play_sound(snd_shield_break)
                    for _ in range(15):
                        color = (100, random.randint(200, 255), 255)
                        p = ExplosionParticle(player.rect.centerx, player.rect.centery, color)
                        effects_group.add(p); all_sprites.add(p)
                else:
                    lives -= 1
                    player.invincible = 45  # 0.75s de invencibilidade
                    screen_shake = 12
                    damage_flash_timer = 8
                    play_sound(snd_hit)
                    combo_count = 0
                    combo_multiplier = 1
                    ft_comb = FloatingText("COMBO QUEBROU!", player.rect.centerx, player.rect.top - 30, color=(255, 50, 50), size=18)
                    effects_group.add(ft_comb); all_sprites.add(ft_comb)
                    spawn_explosion_particles(player.rect.centerx, player.rect.centery, 15)
                    if lives <= 0:
                        game_over = True
                        play_sound(snd_gameover)

        # Colisões com balas e aviões (só dão dano se não estiver invencível)
        if player.invincible <= 0:
            bullet_hits = pygame.sprite.spritecollide(player, enemy_bullets, True, pygame.sprite.collide_mask)
            plane_hits = pygame.sprite.spritecollide(player, planes, True, pygame.sprite.collide_mask)
            
            if bullet_hits or plane_hits:
                if player.has_shield:
                    player.has_shield = False
                    player.invincible = 45
                    screen_shake = 8
                    play_sound(snd_shield_break)
                    for _ in range(15):
                        color = (100, random.randint(200, 255), 255)
                        p = ExplosionParticle(player.rect.centerx, player.rect.centery, color)
                        effects_group.add(p); all_sprites.add(p)
                else:
                    lives -= 1
                    player.invincible = 45
                    screen_shake = 12
                    damage_flash_timer = 8
                    play_sound(snd_hit)
                    combo_count = 0
                    combo_multiplier = 1
                    ft_comb = FloatingText("COMBO QUEBROU!", player.rect.centerx, player.rect.top - 30, color=(255, 50, 50), size=18)
                    effects_group.add(ft_comb); all_sprites.add(ft_comb)
                    spawn_explosion_particles(player.rect.centerx, player.rect.centery, 15)
                    if lives <= 0:
                        game_over = True
                        play_sound(snd_gameover)
        
        # --- Colisão de Tiros do Player ---
        # 1. Colisão com Aviões (Planes)
        plane_kills = pygame.sprite.groupcollide(planes, player_bullets, True, True, pygame.sprite.collide_mask)
        if plane_kills:
            play_sound(snd_explosion)
            increase_combo(len(plane_kills))
            base_pts = 200
            for pk in plane_kills:
                earned = base_pts * combo_multiplier
                score += earned
                ft_pts = FloatingText(f"+{earned}", pk.rect.centerx, pk.rect.centery, color=YELLOW_TEXT)
                effects_group.add(ft_pts); all_sprites.add(ft_pts)
                spawn_explosion_particles(pk.rect.centerx, pk.rect.centery, 12)
        
        # 2. Colisão com Inimigos (Enemies) normais
        enemy_kills = pygame.sprite.groupcollide(enemies, player_bullets, True, True, pygame.sprite.collide_mask)
        if enemy_kills:
            play_sound(snd_explosion)
            increase_combo(len(enemy_kills))
            base_pts = 150
            for ek in enemy_kills:
                earned = base_pts * combo_multiplier
                score += earned
                ft_pts = FloatingText(f"+{earned}", ek.rect.centerx, ek.rect.centery, color=YELLOW_TEXT)
                effects_group.add(ft_pts); all_sprites.add(ft_pts)
                spawn_explosion_particles(ek.rect.centerx, ek.rect.centery, 10)

        # 3. Colisão com Pedras (Rocks)
        # Se a pedra tiver um atirador, a bala mata o atirador mas NÃO danifica a pedra.
        # A pedra só leva dano se não houver atirador vivo ancorado nela.
        for rock in list(rocks):
            for bullet in list(player_bullets):
                if not bullet.alive():
                    continue  # bala já foi destruída por outra colisão neste frame
                if pygame.sprite.collide_mask(rock, bullet):
                    is_super = hasattr(bullet, 'is_super') and bullet.is_super
                    
                    # Verifica se há um atirador ancorado nesta rocha
                    anchored_enemy = None
                    for e in list(enemies):
                        if e.anchor == rock:
                            anchored_enemy = e
                            break
                    
                    if anchored_enemy is not None:
                        # Mata apenas o atirador — a pedra sobrevive
                        if not is_super:
                            bullet.kill()  # bala normal se consome
                        anchored_enemy.kill()
                        play_sound(snd_explosion)
                        increase_combo(1)
                        e_earned = 200 * combo_multiplier
                        score += e_earned
                        ft_e = FloatingText(f"+{e_earned}", anchored_enemy.rect.centerx, anchored_enemy.rect.centery, color=YELLOW_TEXT)
                        effects_group.add(ft_e); all_sprites.add(ft_e)
                        spawn_explosion_particles(anchored_enemy.rect.centerx, anchored_enemy.rect.centery, 10)
                        # Pedra fica – não break, pode ter mais balas
                    else:
                        # Sem atirador: dano vai direto pra pedra
                        dmg = 3 if is_super else 1
                        if not is_super:
                            bullet.kill()
                        if rock.take_damage(dmg):
                            # Pedra destruída!
                            play_sound(snd_explosion)
                            earned = (150 if is_super else 100) * combo_multiplier
                            score += earned
                            ft_pts = FloatingText(f"+{earned}", rock.rect.centerx, rock.rect.centery, color=(180, 200, 255))
                            effects_group.add(ft_pts); all_sprites.add(ft_pts)
                            expl = RockExplosion(rock.rect.centerx, rock.rect.centery, rock_break_imgs)
                            effects_group.add(expl); all_sprites.add(expl)
                            rock.kill()
                            break  # rocha destruída, sai do loop de balas
                        else:
                            play_sound(snd_rock_crack)
                            spawn_explosion_particles(rock.rect.centerx, rock.rect.centery, 4)



        
        flash_alpha = 128 + 127 * (pygame.time.get_ticks() % 500 < 250)
        
        # --- LÓGICA DO BOSS ---
        current_target = PHASES[current_phase]["target"]
        if distance >= current_target and boss is None and phase_transition_timer <= 0:
            if current_phase < 3:
                # Fases 1 e 2: spawna boss e avança
                boss = Boss(distance)
                boss.max_health = PHASES[current_phase]["boss_health"]
                boss.health = boss.max_health
                all_sprites.add(boss)
                play_sound(snd_boss_siren)
                ft_alert = FloatingText("ALERTA: CHEFÃO!", SCREEN_WIDTH//2, SCREEN_HEIGHT//3, color=RED_ENEMY, size=32)
                effects_group.add(ft_alert); all_sprites.add(ft_alert)
            else:
                # FASE 3 FINAL: Bosses a cada 2000m com vida escalada
                if (distance - current_target) % 2000 == 0:
                    boss = Boss(distance)
                    boss.max_health = PHASES[3]["boss_health"] + ((distance - current_target) // 2000) * 20
                    boss.health = boss.max_health
                    all_sprites.add(boss)
                    play_sound(snd_boss_siren)
                    ft_alert = FloatingText("ALERTA: CHEFÃO!", SCREEN_WIDTH//2, SCREEN_HEIGHT//3, color=RED_ENEMY, size=32)
                    effects_group.add(ft_alert); all_sprites.add(ft_alert)

        if boss:
            boss.update(player.rect.centerx)
            
            # Colisão: Tiro do Player no Boss
            hits = pygame.sprite.spritecollide(boss, player_bullets, True, pygame.sprite.collide_mask)
            if hits:
                boss.health -= len(hits)
                play_sound(snd_hit)
                earned = 50 * combo_multiplier * len(hits)
                score += earned
                ft_pts = FloatingText(f"+{earned}", boss.rect.centerx + random.randint(-20, 20), boss.rect.centery + random.randint(-10, 10), color=YELLOW_TEXT)
                effects_group.add(ft_pts); all_sprites.add(ft_pts)
                spawn_explosion_particles(boss.rect.centerx + random.randint(-30, 30), boss.rect.centery + random.randint(-15, 15), 5)
                
                if boss.health <= 0:
                    earned_boss = 5000 * combo_multiplier
                    score += earned_boss
                    ft_boss = FloatingText(f"+{earned_boss} BOSS DETONADO!", boss.rect.centerx, boss.rect.centery, color=(100, 255, 100), size=24)
                    effects_group.add(ft_boss); all_sprites.add(ft_boss)
                    boss.kill()
                    boss = None
                    screen_shake = 30 # Explosão épica!
                    play_sound(snd_explosion)
                    spawn_explosion_particles(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3, 40)
                    
                    # Avança de fase (fases 1 e 2)
                    if current_phase < 3:
                        start_phase_transition(current_phase + 1)
                    # Na fase 3, boss apenas desaparece — a vitória é por distância
        
        # Verifica se chegou à terra firme (distância final da fase 3)
        if current_phase == 3 and distance >= VICTORY_DISTANCE and boss is None:
            show_victory(score, distance)
            show_menu()
            show_tutorial()
            reset_game()
            game_over = False
            continue

        # Custo para ganhar o Shift escala com a fase:
        # Fase 1 = 1500 pts, Fase 2 = 3000 pts, Fase 3 = 5000 pts
        power_cost = {1: 1500, 2: 3000, 3: 5000}.get(current_phase, 1500)
        
        if score > 0 and score // power_cost > last_power_score:
            power_charges += 1
            last_power_score = score // power_cost
            show_special_alert = True
            screen_shake = 10
            play_sound(snd_special_ready)

        
    # --- Lógica de Tremida de Tela ---
    render_offset = [0, 0]
    if screen_shake > 0:
        render_offset[0] = random.randint(-screen_shake, screen_shake)
        render_offset[1] = random.randint(-screen_shake, screen_shake)
        screen_shake -= 1

    # --- DESENHO ---
    # 1. Fundo (imagem da cachoeira)
    screen.blit(background_img, (render_offset[0], bg_y + render_offset[1]))
    screen.blit(background_img, (render_offset[0], bg_y - SCREEN_HEIGHT + render_offset[1]))

    # 2. Overlay de Fase (cor do céu / horário do dia)
    phase_cfg = PHASES.get(current_phase, PHASES[1])
    sky_color = phase_cfg["sky_color"]
    sky_alpha = sky_color[3] if len(sky_color) == 4 else 0
    if sky_alpha > 0:
        sky_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        sky_overlay.fill(sky_color[:3] + (sky_alpha,))
        screen.blit(sky_overlay, (0, 0))

    # 3. Raio (Fase 3 – Tempestade)
    if phase_cfg["lightning"]:
        if lightning_flash > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surf.fill((220, 230, 255))
            flash_surf.set_alpha(min(200, lightning_flash * 20))
            screen.blit(flash_surf, (0, 0))
            lightning_flash -= 1
        lightning_timer -= 1
        if lightning_timer <= 0:
            lightning_timer = random.randint(90, 300)   # 1.5 a 5 segundos
            lightning_flash = random.randint(4, 10)
            screen_shake = max(screen_shake, 8)
            play_sound(snd_hit)  # som de trovão

    # 4. Chuva
    rain_intensity = phase_cfg["rain_intensity"]
    if rain_intensity > 0:
        # Ajusta quantidade de gotas ao entrar na fase
        while len(rain_drops) < rain_intensity:
            d = RainDrop(current_phase)
            d.y = random.randint(0, SCREEN_HEIGHT)  # distribui pela tela desde o início
            rain_drops.append(d)
        while len(rain_drops) > rain_intensity:
            rain_drops.pop()
        rain_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for drop in rain_drops:
            drop.update()
            drop.draw(rain_surf)
        screen.blit(rain_surf, (0, 0))
    else:
        rain_drops = []
    
    # Desenha correntes senoidais e detritos no leito do rio
    ticks = pygame.time.get_ticks()
    for current in river_currents:
        current.draw(screen, ticks)
        
    for debris in river_debris:
        debris.draw(screen, ticks)
    
    # Desenha as espumas rápidas da cachoeira
    for foam in water_foams:
        foam.draw(screen)
        
    # Desenha rastro do player
    for p in wake_particles:
        p.draw(screen)
        
    # Desenha os redemoinhos (Whirlpools)
    for w in whirlpools_group:
        screen.blit(w.image, (w.rect.x + render_offset[0], w.rect.y + render_offset[1]))
        
    # Desenha as rochas marginais (Canyon)
    for block in canyons_group:
        screen.blit(block.image, (block.rect.x + render_offset[0], block.rect.y + render_offset[1]))
        
    # 2. Todos os Sprites (usando o offset do tremor)
    for sprite in all_sprites:
        if sprite.alive() and not isinstance(sprite, Boss) and not isinstance(sprite, Whirlpool):
            screen.blit(sprite.image, (sprite.rect.x + render_offset[0], sprite.rect.y + render_offset[1]))
            # Desenha aura do escudo ao redor do jogador
            if sprite == player and player.has_shield:
                shield_surf = pygame.Surface((sprite.rect.width + 20, sprite.rect.height + 20), pygame.SRCALPHA)
                pulse_alpha = 100 + int(40 * math.sin(pygame.time.get_ticks() * 0.015))
                pygame.draw.ellipse(shield_surf, (0, 150, 255, pulse_alpha), (0, 0, sprite.rect.width + 20, sprite.rect.height + 20), 3)
                pygame.draw.ellipse(shield_surf, (100, 200, 255, pulse_alpha // 2), (2, 2, sprite.rect.width + 16, sprite.rect.height + 16))
                screen.blit(shield_surf, (sprite.rect.x - 10 + render_offset[0], sprite.rect.y - 10 + render_offset[1]))

    if boss and boss.alive():
        screen.blit(boss.image, (boss.rect.x + render_offset[0], boss.rect.y + render_offset[1]))
        boss.draw_health_bar(screen)
        
    # 3. UI (Texto, Fases e Vidas)
    draw_text_shaded(screen, f"Score: {score}", font_main, YELLOW_TEXT, 20, 20)
    if combo_multiplier > 1:
        combo_colors = {
            2: (150, 220, 255),
            3: (100, 255, 120),
            4: (255, 180, 50),
            5: (255, 60, 60)
        }
        c_color = combo_colors.get(combo_multiplier, YELLOW_TEXT)
        draw_text_shaded(screen, f"Combo: x{combo_multiplier}", font_main, c_color, 20, 50)
        
    # Exibe apenas distância no centro do HUD (sem nome de fase)
    draw_text_shaded(screen, f"{distance}m", font_main, WHITE, SCREEN_WIDTH//2, 20, "midtop")
    
    # Desenha vidas (corações) no canto superior direito
    for i in range(lives):
        screen.blit(heart_img, (SCREEN_WIDTH - 40 - (i*30), 20))

    # --- Desenho da Transição de Fase ---
    if phase_transition_timer > 0:
        # Desenha uma faixa escura semi-transparente
        banner = pygame.Surface((SCREEN_WIDTH, 110), pygame.SRCALPHA)
        banner.fill((0, 0, 0, 190))
        screen.blit(banner, (0, SCREEN_HEIGHT // 2 - 55))
        
        # Pisca o texto de fase concluída
        text_flash = (pygame.time.get_ticks() // 200) % 2 == 0
        text1_color = YELLOW_TEXT if text_flash else WHITE
        draw_text_shaded(screen, phase_transition_text1, font_title, text1_color, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25, "center")
        draw_text_shaded(screen, phase_transition_text2, font_main, (100, 200, 255), SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25, "center")
        
        phase_transition_timer -= 1
        
    # --- Desenho da UI de Poder ---
    if show_special_alert and not is_power_active:
        # Pisca apenas se o alerta estiver ligado e o poder não estiver em uso
        if (pygame.time.get_ticks() // 250) % 2 == 0:
            draw_text_shaded(screen, "ESPECIAL PRONTO [SHIFT]!", font_main, YELLOW_TEXT, SCREEN_WIDTH//2, 120, "midtop")

    if is_power_active:
        draw_text_shaded(screen, "!!! MODO DESTRUIÇÃO !!!", font_main, RED_ENEMY, SCREEN_WIDTH//2, 120, "midtop")
        
        bar_width = (power_active_timer / 120) * 200
        pygame.draw.rect(screen, BLACK, (SCREEN_WIDTH//2 - 100, 150, 200, 10))
        pygame.draw.rect(screen, YELLOW_TEXT, (SCREEN_WIDTH//2 - 100, 150, bar_width, 10))

    # --- Flash de Dano ---
    if damage_flash_timer > 0:
        flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        flash_surf.fill((255, 0, 0))
        alpha = int((damage_flash_timer / 8.0) * 80)
        flash_surf.set_alpha(alpha)
        screen.blit(flash_surf, (0, 0))
        damage_flash_timer -= 1

    pygame.display.flip()
    clock.tick(FPS)