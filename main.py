import random

WIDTH = 800
HEIGHT = 600
TITLE = "Mini Roguelike"

# game states
MENU = "menu"
GAME = "game"
state = MENU

music_on = True

# spawn timer
spawn_timer = 0
spawn_delay = 180  # ~3 sekundy

# game objects
bullets = []
enemies = []
score = 0

# ---------- CLASSES ----------

class Player:
    def __init__(self):
        self.actor = Actor("player_idle_0", center=(400, 300))
        self.speed = 3
        self.direction = (0, -1)
        self.idle_frames = ["player_idle_0", "player_idle_1"]
        self.walk_frames = ["player_walk_0", "player_walk_1"]
        self.frame = 0
        self.timer = 0
        self.moving = False

    def move(self):
        self.moving = False
        if keyboard.a:
            self.actor.x -= self.speed
            self.direction = (-1, 0)
            self.moving = True
        if keyboard.d:
            self.actor.x += self.speed
            self.direction = (1, 0)
            self.moving = True
        if keyboard.w:
            self.actor.y -= self.speed
            self.direction = (0, -1)
            self.moving = True
        if keyboard.s:
            self.actor.y += self.speed
            self.direction = (0, 1)
            self.moving = True

        # stay in screen
        self.actor.x = max(50, min(WIDTH - 50, self.actor.x))
        self.actor.y = max(50, min(HEIGHT - 50, self.actor.y))

    def animate(self):
        self.timer += 1
        if self.timer % 20 == 0:
            self.frame = (self.frame + 1) % 2
            self.actor.image = (
                self.walk_frames[self.frame] if self.moving else self.idle_frames[self.frame]
            )

class Enemy:
    def __init__(self):
        self.actor = Actor(
            "enemy_idle_0",
            center=(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50))
        )
        self.speed = 1
        self.state = "idle"  # "idle" albo "moving"
        self.state_timer = 0
        self.idle_duration = random.randint(30, 90)  # ile klatek stoi
        self.move_duration = random.randint(60, 150)  # ile klatek chodzi
        self.direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        self.frame = 0
        self.timer = 0

    def update_state(self):
        self.state_timer += 1
        if self.state == "idle" and self.state_timer >= self.idle_duration:
            self.state = "moving"
            self.state_timer = 0
            self.move_duration = random.randint(60, 150)
            self.direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
        elif self.state == "moving" and self.state_timer >= self.move_duration:
            self.state = "idle"
            self.state_timer = 0
            self.idle_duration = random.randint(30, 90)

    def move(self):
        self.update_state()
        if self.state == "moving":
            dx, dy = self.direction
            self.actor.x += dx * self.speed
            self.actor.y += dy * self.speed

            if random.randint(0, 100) == 0:
                self.direction = random.choice([(1,0), (-1,0), (0,1), (0,-1)])

        self.actor.x = max(50, min(WIDTH - 50, self.actor.x))
        self.actor.y = max(50, min(HEIGHT - 50, self.actor.y))

    def animate(self):
        self.timer += 1
        if self.timer % 30 == 0:
            self.frame = (self.frame + 1) % 2
            if self.state == "moving":
                self.actor.image = f"enemy_walk_{self.frame}"
            else:
                self.actor.image = f"enemy_idle_{self.frame}"

class Bullet:
    def __init__(self, pos, direction):
        self.actor = Actor("bullet", center=pos)
        self.dx, self.dy = direction
        self.speed = 6

    def update(self):
        self.actor.x += self.dx * self.speed
        self.actor.y += self.dy * self.speed

    def offscreen(self):
        return self.actor.x < 0 or self.actor.x > WIDTH or self.actor.y < 0 or self.actor.y > HEIGHT

# ---------- GAME OBJECTS ----------

player = Player()
enemies = [Enemy() for _ in range(4)]

# ---------- MENU BUTTONS ----------

start_btn = Rect((300, 200), (200, 50))
music_btn = Rect((300, 270), (200, 50))
exit_btn = Rect((300, 340), (200, 50))

# ---------- FUNCTIONS ----------

def start_game():
    global state, enemies, bullets, score
    state = GAME
    enemies = [Enemy() for _ in range(4)]
    bullets = []
    score = 0
    if music_on:
        music.play("music.wav")

def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        music.play("music.wav")
    else:
        music.stop()

def draw_menu():
    screen.clear()
    screen.blit("background_menu", (0, 0))
    screen.draw.text("ROGUELIKE", center=(400, 120), fontsize=60)

    screen.draw.filled_rect(start_btn, "gray")
    screen.draw.filled_rect(music_btn, "gray")
    screen.draw.filled_rect(exit_btn, "gray")

    screen.draw.text("Start Game", center=start_btn.center)
    screen.draw.text(
        "Music: ON" if music_on else "Music: OFF",
        center=music_btn.center
    )
    screen.draw.text("Exit", center=exit_btn.center)

def reset_game():
    global state, enemies, bullets, score
    state = MENU
    enemies = [Enemy() for _ in range(4)]
    bullets = []
    score = 0
    music.stop()

# ---------- PGZERO ----------

def draw():
    if state == MENU:
        draw_menu()
    else:
        screen.clear()
        screen.blit("background", (0, 0))
        player.actor.draw()
        for enemy in enemies:
            enemy.actor.draw()
        for bullet in bullets:
            bullet.actor.draw()
        screen.draw.text(f"Score: {score}", (10, 10), fontsize=30)

def update():
    global spawn_timer, score
    if state == GAME:
        player.move()
        player.animate()

        # bullets
        for bullet in bullets[:]:
            bullet.update()
            # kolizja z wrogami
            for enemy in enemies[:]:
                if bullet.actor.colliderect(enemy.actor):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    sounds.hit.play()
                    score += 1
                    break
            # offscreen
            if bullet.offscreen() and bullet in bullets:
                bullets.remove(bullet)

        # enemies
        for e in enemies:
            e.move()
            e.animate()
            if player.actor.colliderect(e.actor):
                sounds.hit.play()
                reset_game()

        # spawn nowych przeciwników
        spawn_timer += 1
        if spawn_timer >= spawn_delay:
            enemies.append(Enemy())
            spawn_timer = 0

# strzelanie
def on_key_down(key):
    if state == GAME:
        if key == keys.SPACE:
            bullets.append(Bullet(player.actor.center, player.direction))

# menu klik
def on_mouse_down(pos):
    if state == MENU:
        if start_btn.collidepoint(pos):
            start_game()
        elif music_btn.collidepoint(pos):
            toggle_music()
        elif exit_btn.collidepoint(pos):
            exit()
