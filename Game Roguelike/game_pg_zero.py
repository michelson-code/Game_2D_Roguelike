#import pgzero
import pgzrun
import random
#import math
from pygame import Rect


# ============================================================================
# CONFIGURAÇÕES E CONSTANTES
# ============================================================================

WIDTH = 800
HEIGHT = 600
TILE_SIZE = 32
GRID_WIDTH = WIDTH // TILE_SIZE  # 25
GRID_HEIGHT = HEIGHT // TILE_SIZE  # 18


class GameState:
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    WIN = "win"
    HOWTO = "howto"


game_state = GameState.MENU
music_enabled = True
hero = None
enemies = []
game_map = []
bullets = []
coins = []
score = 0

ENEMY_MAX_HP = 3
KILL_SCORE = 50
COIN_SCORE = 5

# ============================================================================
# MAPA
# ============================================================================


class GameMap:
    """Grade com paredes e piso do roguelike."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # 0 = piso, 1 = parede
        self.tiles = [[0 for _ in range(width)] for _ in range(height)]
        self.generate_map()

    def generate_map(self):
        """Gera bordas e paredes internas aleatorias."""
        for x in range(self.width):
            self.tiles[0][x] = 1
            self.tiles[self.height - 1][x] = 1

        for y in range(self.height):
            self.tiles[y][0] = 1
            self.tiles[y][self.width - 1] = 1

        for _ in range(30):
            x = random.randint(2, self.width - 3)
            y = random.randint(2, self.height - 3)
            if not (x == GRID_WIDTH // 2 and y == GRID_HEIGHT // 2):
                self.tiles[y][x] = 1

    def is_walkable(self, x, y):
        """Retorna True se a celula eh piso e esta dentro do mapa."""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.tiles[y][x] == 0


# ============================================================================
# HERÓI
# ============================================================================


class Hero:
    """Heroi controlado pelo jogador."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 5
        self.max_health = 5
        self.animation_frame = 0
        self.animation_counter = 0
        self.actor = Actor("hero", (x * TILE_SIZE + TILE_SIZE // 2,
                                    y * TILE_SIZE + TILE_SIZE // 2))
        self.facing = (0, -1)   # olhando para cima
        self.actor.angle = 90   # sprite base apontando para a direita

    def move(self, dx, dy, game_map):
        """Move o heroi na grade, respeitando paredes e girando sprite."""
        new_x = self.x + dx
        new_y = self.y + dy
        if game_map.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y

            if dx != 0 or dy != 0:
                self.facing = (dx, dy)
                if dx == 1 and dy == 0:
                    self.actor.angle = 0
                elif dx == -1 and dy == 0:
                    self.actor.angle = 180
                elif dx == 0 and dy == -1:
                    self.actor.angle = 90
                elif dx == 0 and dy == 1:
                    self.actor.angle = 270

            if music_enabled:
                sounds.hit.play()
            return True
        return False

    def take_damage(self, amount=1):
        """Reduz vida e troca para GAME_OVER se chegar a zero."""
        global game_state
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            game_state = GameState.GAME_OVER
            stop_background_music()

    def update(self):
        """Atualiza animacao e posicao do sprite do heroi."""
        self.animation_counter += 1
        if self.animation_counter >= 10:
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % 2

        self.actor.x = self.x * TILE_SIZE + TILE_SIZE // 2
        self.actor.y = self.y * TILE_SIZE + TILE_SIZE // 2

    def draw(self):
        self.actor.draw()


# ============================================================================
# INIMIGO
# ============================================================================


class Enemy:
    """Inimigos alienigenas com IA simples de perseguicao."""
    def __init__(self, x, y, sprite_name, patrol_range=5):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.patrol_range = patrol_range
        self.actor = Actor(sprite_name, (x * TILE_SIZE + TILE_SIZE // 2,
                                         y * TILE_SIZE + TILE_SIZE // 2))
        self.animation_frame = 0
        self.animation_counter = 0
        self.hp = ENEMY_MAX_HP

    def distance_to(self, target_x, target_y):
        return abs(self.x - target_x) + abs(self.y - target_y)

    def take_turn(self, hero, game_map):
        """Persegue o heroi, ataca quando encosta e recua para nao grudar."""
        hx, hy = hero.x, hero.y
        ex, ey = self.x, self.y
        dist = abs(ex - hx) + abs(ey - hy)

        if dist > 6:
            for dx, dy in random.sample([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)], 5):
                nx, ny = ex + dx, ey + dy
                if game_map.is_walkable(nx, ny) and (nx, ny) != (hx, hy):
                    self.x, self.y = nx, ny
                    return
            return

        if dist == 1:
            hero.take_damage(1)
            if music_enabled:
                sounds.laser.play()

            for _ in range(2):
                ex, ey = self.x, self.y
                dist = abs(ex - hx) + abs(ey - hy)

                moved = False
                for dx, dy in random.sample([(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)], 5):
                    nx, ny = ex + dx, ey + dy
                    if not game_map.is_walkable(nx, ny):
                        continue
                    new_dist = abs(nx - hx) + abs(ny - hy)
                    if new_dist > dist and (nx, ny) != (hx, hy):
                        self.x, self.y = nx, ny
                        moved = True
                        break

                if not moved:
                    break
            return

        best_pos = (ex, ey)
        best_dist = dist

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = ex + dx, ey + dy
            if not game_map.is_walkable(nx, ny):
                continue
            if (nx, ny) == (hx, hy):
                continue
            new_dist = abs(nx - hx) + abs(ny - hy)
            if new_dist < best_dist:
                best_dist = new_dist
                best_pos = (nx, ny)

        self.x, self.y = best_pos

    def update(self):
        self.animation_counter += 1
        if self.animation_counter >= 12:
            self.animation_counter = 0
            self.animation_frame = (self.animation_frame + 1) % 2

        self.actor.x = self.x * TILE_SIZE + TILE_SIZE // 2
        self.actor.y = self.y * TILE_SIZE + TILE_SIZE // 2

    def draw(self):
        self.actor.draw()


# ============================================================================
# BOTÕES
# ============================================================================


class Button:
    """Botao retangular com texto centralizado."""
    def __init__(self, x, y, width, height, text):
        self.rect = Rect((x, y), (width, height))
        self.text = text
        self.hovered = False

    def contains(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self):
        color = (120, 220, 120) if self.hovered else (60, 170, 60)
        screen.draw.filled_rect(self.rect, color)
        screen.draw.rect(self.rect, (230, 230, 230))
        screen.draw.text(self.text, center=self.rect.center,
                         color=(255, 255, 255), fontsize=24)


start_button   = Button(250, 150, 300, 60, "Iniciar partida")
howto_button   = Button(250, 230, 300, 60, "Como jogar")
music_button   = Button(250, 310, 300, 60, "Musica: ON")
quit_button    = Button(250, 390, 300, 60, "Sair do jogo")

restart_button = Button(250, 350, 300, 60, "Jogar novamente")
exit_button    = Button(250, 430, 300, 60, "Sair do jogo")
back_button    = Button(250, 430, 300, 60, "Voltar ao menu")

# imagem da tela COMO JOGAR
howto_image = Actor("como_jogar")
howto_image.pos = (WIDTH // 2, HEIGHT // 2)

# ============================================================================
# MÚSICA
# ============================================================================


def start_background_music():
    if music_enabled:
        music.play("background")


def stop_background_music():
    music.stop()


# ============================================================================
# FUNÇÕES DE JOGO
# ============================================================================


def init_game():
    """Inicia uma nova partida."""
    global game_state, hero, enemies, game_map, score, bullets, coins

    game_state = GameState.PLAYING
    game_map = GameMap(GRID_WIDTH, GRID_HEIGHT)

    hero_x = GRID_WIDTH // 2
    hero_y = GRID_HEIGHT // 2
    hero = Hero(hero_x, hero_y)

    enemies = []
    sprites = ["alien", "alien_ugly", "alien3"]
    for sprite in sprites:
        for _ in range(3):
            while True:
                x = random.randint(2, GRID_WIDTH - 3)
                y = random.randint(2, GRID_HEIGHT - 3)
                if (x, y) != (hero_x, hero_y) and game_map.is_walkable(x, y):
                    enemies.append(Enemy(x, y, sprite_name=sprite, patrol_range=7))
                    break

    bullets = []

    coins = []
    for _ in range(8):
        while True:
            x = random.randint(2, GRID_WIDTH - 3)
            y = random.randint(2, GRID_HEIGHT - 3)
            if (x, y) != (hero_x, hero_y) and game_map.is_walkable(x, y):
                coin = Actor("coin")
                coin.grid_x = x
                coin.grid_y = y
                coin.x = x * TILE_SIZE + TILE_SIZE // 2
                coin.y = y * TILE_SIZE + TILE_SIZE // 2
                coins.append(coin)
                break

    score = 0
    start_background_music()


def check_win_condition():
    """Troca para tela de vitoria quando nao restam inimigos."""
    global game_state
    if game_state == GameState.PLAYING and len(enemies) == 0:
        game_state = GameState.WIN
        stop_background_music()


def collect_coins():
    """Coleta moedas quando o heroi passa por cima."""
    global score
    for coin in coins[:]:
        if coin.grid_x == hero.x and coin.grid_y == hero.y:
            coins.remove(coin)
            score += COIN_SCORE
            if music_enabled:
                sounds.coin.play()


def check_collisions():
    """Reserva para colisoes adicionais (nao usada atualmente)."""
    return


# ============================================================================
# LOOP DO JOGO
# ============================================================================


def draw():
    screen.fill((20, 20, 30))

    if game_state == GameState.MENU:
        screen.draw.text("ROGUELIKE ESPACIAL", center=(WIDTH // 2, 60),
                         color=(100, 220, 100), fontsize=42)
        screen.draw.text("Desenvolvido por Bruno Dantas",
                         center=(WIDTH // 2, 100),
                         color=(150, 150, 150), fontsize=20)

        start_button.draw()
        howto_button.draw()
        music_button.draw()
        quit_button.draw()

    elif game_state == GameState.HOWTO:
        howto_image.draw()
        back_button.draw()

    elif game_state == GameState.PLAYING:
        for y in range(game_map.height):
            for x in range(game_map.width):
                if game_map.tiles[y][x] == 1:
                    rect = Rect((x * TILE_SIZE, y * TILE_SIZE),
                                (TILE_SIZE, TILE_SIZE))
                    screen.draw.filled_rect(rect, (100, 100, 100))
                    screen.draw.rect(rect, (150, 150, 150))

        for coin in coins:
            coin.draw()

        hero.draw()
        for enemy in enemies:
            enemy.draw()
        for bullet in bullets:
            bullet.draw()

        screen.draw.text(f"Vida: {hero.health}/{hero.max_health}", (10, 10),
                         color=(255, 100, 100), fontsize=16)
        screen.draw.text(f"Pontos: {score}", (10, 35),
                         color=(100, 200, 100), fontsize=16)
        screen.draw.text("Setas: mover | WASD: laser", (WIDTH - 270, 10),
                         color=(150, 150, 150), fontsize=12)

    elif game_state == GameState.GAME_OVER:
        screen.draw.text("GAME OVER", center=(WIDTH // 2, 150),
                         color=(255, 100, 100), fontsize=48)
        screen.draw.text(f"Pontuacao Final: {score}",
                         center=(WIDTH // 2, 230),
                         color=(200, 200, 200), fontsize=24)
        screen.draw.text("Desenvolvido por Bruno Dantas",
                         center=(WIDTH // 2, 270),
                         color=(180, 180, 180), fontsize=20)

        restart_button.draw()
        back_button.draw()
        exit_button.draw()

    elif game_state == GameState.WIN:
        screen.draw.text("VOCE VENCEU!", center=(WIDTH // 2, 150),
                         color=(100, 220, 100), fontsize=48)
        screen.draw.text(f"Pontuacao Final: {score}",
                         center=(WIDTH // 2, 230),
                         color=(200, 200, 200), fontsize=24)
        screen.draw.text("Desenvolvido por Bruno Dantas",
                         center=(WIDTH // 2, 270),
                         color=(180, 180, 180), fontsize=20)

        restart_button.draw()
        back_button.draw()
        exit_button.draw()


def update():
    if game_state == GameState.PLAYING:
        hero.update()
        for enemy in enemies:
            enemy.update()

        for bullet in bullets[:]:
            speed = 10
            bullet.x += bullet.vx * speed
            bullet.y += bullet.vy * speed

            if (bullet.x < 0 or bullet.x > WIDTH or
                bullet.y < 0 or bullet.y > HEIGHT):
                bullets.remove(bullet)
                continue

            hit = False
            for enemy in enemies[:]:
                if bullet.colliderect(enemy.actor):
                    enemy.hp -= 1
                    bullets.remove(bullet)
                    hit = True
                    if enemy.hp <= 0:
                        enemies.remove(enemy)
                        global score
                        score += KILL_SCORE
                    break
            if hit:
                continue

        check_win_condition()


def on_key_down(key):
    """Movimento com setas e tiros com WASD."""
    global score

    if game_state != GameState.PLAYING:
        return

    moved = False
    if key == keys.UP:
        moved = hero.move(0, -1, game_map)
    elif key == keys.DOWN:
        moved = hero.move(0, 1, game_map)
    elif key == keys.LEFT:
        moved = hero.move(-1, 0, game_map)
    elif key == keys.RIGHT:
        moved = hero.move(1, 0, game_map)

    elif key in (keys.W, keys.A, keys.S, keys.D):
        if key == keys.D:
            dir_x, dir_y = 1, 0
            angle = 0
        elif key == keys.A:
            dir_x, dir_y = -1, 0
            angle = 180
        elif key == keys.W:
            dir_x, dir_y = 0, -1
            angle = 90
        elif key == keys.S:
            dir_x, dir_y = 0, 1
            angle = 270

        hero.facing = (dir_x, dir_y)
        hero.actor.angle = angle

        bullet = Actor("laser")
        bullet.x = hero.x * TILE_SIZE + TILE_SIZE // 2
        bullet.y = hero.y * TILE_SIZE + TILE_SIZE // 2
        bullet.angle = angle
        bullet.vx = dir_x
        bullet.vy = dir_y
        bullets.append(bullet)
        if music_enabled:
            sounds.shoot.play()

    if moved:
        score += 1
        collect_coins()
        for enemy in enemies:
            enemy.take_turn(hero, game_map)
        check_collisions()


def on_mouse_down(pos):
    """Tratamento de cliques em botoes de menu."""
    global game_state, music_enabled

    if game_state == GameState.MENU:
        if start_button.contains(pos):
            init_game()
        elif howto_button.contains(pos):
            game_state = GameState.HOWTO
        elif music_button.contains(pos):
            music_enabled = not music_enabled
            music_button.text = "Musica: ON" if music_enabled else "Musica: OFF"
            if music_enabled:
                start_background_music()
            else:
                stop_background_music()
        elif quit_button.contains(pos):
            import sys
            sys.exit()

    elif game_state == GameState.HOWTO:
        if back_button.contains(pos):
            game_state = GameState.MENU

    elif game_state in (GameState.GAME_OVER, GameState.WIN):
        if restart_button.contains(pos):
            init_game()
        elif back_button.contains(pos):
            game_state = GameState.MENU
        elif exit_button.contains(pos):
            import sys
            sys.exit()


start_background_music()

if __name__ == "__main__":
    pgzrun.go()
