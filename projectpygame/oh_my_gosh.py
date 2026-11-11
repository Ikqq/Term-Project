import os
import sys
import math
import random
import pygame

os.chdir(os.path.dirname(os.path.abspath(__file__)))

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
MAX_DELTA = 1 / 30  # กันเฟรมที่ค้างนาน ๆ ทำให้วัตถุกระโดด

pygame.init()
pygame.font.init()

# vsync ช่วยลดภาพฉีก/กระตุก (ถ้าเครื่องไม่รองรับจะ fallback เป็นแบบปกติ)
try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SCALED, vsync=1)
except (pygame.error, TypeError):
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 36, bold=True)
Program = True
delta_time = 0
state = "menu"

# ตัวแปรควบคุมเกมและความเร็วโลก (World Speed)
BASE_SPEED = 15
current_world_speed = BASE_SPEED

# ระบบจับเวลาและเพิ่มความยาก
GAME_DURATION = 60        # เวลาเล่นต่อเกม (วินาที)
SPEED_UP_INTERVAL = 10    # ทุกกี่วินาทีความเร็วจะเพิ่ม
SPEED_UP_STEP = 1.5       # เพิ่มความเร็วครั้งละเท่าไร (ยิ่งมากยิ่งยาก)
base_speed = BASE_SPEED   # ความเร็วพื้นฐานปัจจุบัน (เพิ่มขึ้นตามเวลา)
game_time = 0.0
speed_level = 0
speed_boost_timer = 0
is_speed_boosted = False

# ตัวแปรระบบเกม
coins_collected = 0
player_hp = None
player = None
background1 = None
obstacles_list = []
coin_list = []

last_spawn_time = 0
last_spawn_time2 = 0
spawn_obstacles_time = 3000
spawn_obstacles_time2 = 1700

menu = None
game_over_menu = None
time_up_menu = None


# --- ASSET CACHE (โหลดรูปครั้งเดียว ไม่โหลดซ้ำตอนเกม spawn ของ) ---

_image_cache = {}
_mask_cache = {}


def load_scaled(path, scale=None, size=None, alpha=True, flip=False):
    key = (path, scale, size, alpha, flip)
    cached = _image_cache.get(key)
    if cached is not None:
        return cached

    img = pygame.image.load(path)
    img = img.convert_alpha() if alpha else img.convert()

    if size is not None:
        img = pygame.transform.scale(img, size)
    elif scale is not None:
        img = pygame.transform.scale(
            img, (int(img.get_width() * scale), int(img.get_height() * scale))
        )

    if flip:
        img = pygame.transform.flip(img, True, False)

    _image_cache[key] = img
    return img


def get_mask(img):
    m = _mask_cache.get(id(img))
    if m is None:
        m = pygame.mask.from_surface(img)
        _mask_cache[id(img)] = m
    return m


_tint_cache = {}


def get_tinted(img):
    """คืนค่า (ภาพที่ย้อมสีม่วง, ภาพเงาโปร่งแสง) สร้างครั้งเดียวแล้ว cache ไว้"""
    cached = _tint_cache.get(id(img))
    if cached is None:
        tinted = img.copy()
        tinted.fill((90, 0, 130, 0), special_flags=pygame.BLEND_RGB_ADD)
        ghost = tinted.copy()
        ghost.set_alpha(100)
        get_mask(tinted)
        cached = (tinted, ghost)
        _tint_cache[id(img)] = cached
    return cached


# --- ZONE OF CLASSES ---

class PixelMenu:
    def __init__(self, title, actions, subtitle=None):
        self.title = title
        self.actions = actions
        self.subtitle = subtitle  # ฟังก์ชันที่คืนข้อความ เช่น lambda: 'Coins: 5'
        self.title_font = pygame.font.SysFont("Courier New", 54, bold=True)
        self.btn_font = pygame.font.SysFont("Courier New", 24, bold=True)
        self.sub_font = pygame.font.SysFont("Courier New", 32, bold=True)

    def update(self, events):
        mouse = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, (_, action) in enumerate(self.actions):
                    rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, 330 + i * 90, 280, 52)
                    if rect.collidepoint(mouse):
                        action()
                        return

    def draw(self, surface):
        surface.fill((10, 13, 21))
        pygame.draw.rect(surface, (28, 28, 34), (90, 70, SCREEN_WIDTH - 180, SCREEN_HEIGHT - 140), 4)
        pygame.draw.rect(surface, (18, 18, 26), (110, 90, SCREEN_WIDTH - 220, SCREEN_HEIGHT - 180), 2)

        title = self.title_font.render(self.title, True, (255, 245, 210))
        surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 160)))

        if self.subtitle:
            sub = self.sub_font.render(self.subtitle(), True, (255, 209, 102))
            surface.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 245)))

        for i, (label, _) in enumerate(self.actions):
            rect = pygame.Rect(SCREEN_WIDTH // 2 - 140, 330 + i * 90, 280, 52)
            hover = rect.collidepoint(pygame.mouse.get_pos())
            pygame.draw.rect(surface, (18, 24, 39), rect)
            pygame.draw.rect(surface, (255, 209, 102) if hover else (104, 225, 203), rect, 3)
            btn = self.btn_font.render(label, True, (245, 245, 245))
            surface.blit(btn, btn.get_rect(center=rect.center))


class Background_class:
    def __init__(self, image_path, screen_width, screen_height, speed=3):
        self.speed = speed
        self.width = screen_width
        self.height = screen_height
        size = (screen_width, screen_height)
        # ฉากหลังไม่มีความโปร่งใส ใช้ convert() จะ blit เร็วกว่า convert_alpha() มาก
        self.image1 = load_scaled(image_path, size=size, alpha=False)
        self.image2 = load_scaled(image_path, size=size, alpha=False, flip=True)
        self.x1 = 0
        self.x2 = self.width

    def update(self):
        move = self.speed * 20 * delta_time
        self.x1 -= move
        self.x2 -= move

        # เลื่อนข้ามไปต่อท้ายอีกภาพแบบเว้นระยะคงที่ ไม่มีรอยต่อกระตุก
        if self.x1 <= -self.width:
            self.x1 += self.width * 2
        if self.x2 <= -self.width:
            self.x2 += self.width * 2

    def draw(self, screen):
        screen.blit(self.image1, (round(self.x1), 0))
        screen.blit(self.image2, (round(self.x2), 0))


class player_class:
    def __init__(self, x, y, image_path, scale_factor=0.5, speed=5):
        self.animation_frames = []
        for i in image_path:
            scaled_image = load_scaled(i, scale=scale_factor)
            self.width, self.height = scaled_image.get_size()
            self.animation_frames.append(scaled_image)

        self.current_frame = 0
        self.animation_timer = 0
        self.frame_speed = 50
        self.image = self.animation_frames[0]
        self.mask = get_mask(self.image)

        self.x = x
        self.y = y
        self.speed = speed
        self.current_lane = 1
        self.lanes_y = []

    def set_lane(self, screen_height):
        top_of_road = screen_height // 2
        road_height = screen_height // 2
        lane_height = road_height // 3

        self.lanes_y = [
            top_of_road + lane_height // 2 - self.height // 2,
            top_of_road + 1 * lane_height + lane_height // 2 - self.height // 2,
            top_of_road + 2 * lane_height + lane_height // 2 - self.height // 2
        ]
        self.y = self.lanes_y[self.current_lane]

    def move_up(self):
        if self.current_lane > 0:
            self.current_lane -= 1
            self.y = self.lanes_y[self.current_lane]

    def move_down(self):
        if self.current_lane < 2:
            self.current_lane += 1
            self.y = self.lanes_y[self.current_lane]

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer >= self.frame_speed:
            self.animation_timer = current_time
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Obstacle_class:
    def __init__(self, obstacle_path, screen_width, screen_height, scale_factor=0.5, speed=3):
        if obstacle_path:
            # ดึงจาก cache แทนการโหลดไฟล์จากดิสก์ทุกครั้งที่ spawn (ต้นเหตุหลักของอาการกระตุก)
            self.obs_image = load_scaled(obstacle_path, scale=scale_factor)
            self.width, self.height = self.obs_image.get_size()
            self.mask = get_mask(self.obs_image)

        self.screen_width = screen_width
        top_of_road = screen_height // 2
        road_height = screen_height // 2
        lane_height = road_height // 3
        self.lanes_y = [
            top_of_road + lane_height // 2 - self.height // 2,
            top_of_road + 1 * lane_height + lane_height // 2 - self.height // 2,
            top_of_road + 2 * lane_height + lane_height // 2 - self.height // 2
        ]

        self.speed = speed
        self.y = random.choice(self.lanes_y)
        self.x = screen_width

    def update(self):
        self.x -= self.speed * 60 * delta_time

    def draw(self, screen):
        screen.blit(self.obs_image, (round(self.x), self.y))


class Speed_Boost(Obstacle_class):
    def __init__(self, obstacle_path, screen_width, screen_height, scale_factor=0.5, speed=3):
        super().__init__(obstacle_path, screen_width, screen_height, scale_factor, speed)

    def effect(self, player, player_HP):
        global current_world_speed, speed_boost_timer, is_speed_boosted
        current_time = pygame.time.get_ticks()
        current_world_speed = base_speed + 10

        background1.speed = current_world_speed
        for obs in obstacles_list:
            obs.speed = current_world_speed
        for c in coin_list:
            c.speed = current_world_speed

        if is_speed_boosted:
            speed_boost_timer += 2000
        else:
            speed_boost_timer = current_time + 2000
            is_speed_boosted = True


class Speed_Down(Obstacle_class):
    def __init__(self, obstacle_path, screen_width, screen_height, scale_factor=0.5, speed=3):
        super().__init__(obstacle_path, screen_width, screen_height, scale_factor, speed)

    def effect(self, player, player_HP):
        global current_world_speed, speed_boost_timer, is_speed_boosted
        current_time = pygame.time.get_ticks()
        current_world_speed = max(2, base_speed - 2)

        background1.speed = current_world_speed
        for obs in obstacles_list:
            obs.speed = current_world_speed
        for c in coin_list:
            c.speed = current_world_speed

        if is_speed_boosted:
            speed_boost_timer += 2000
        else:
            speed_boost_timer = current_time + 2000
            is_speed_boosted = True


class decrease_hp(Obstacle_class):
    def __init__(self, obstacle_path, screen_width, screen_height, scale_factor=0.5, speed=3):
        super().__init__(obstacle_path, screen_width, screen_height, scale_factor, speed)

    def effect(self, player, player_HP):
        player_HP.hp -= 1


class increase_hp(Obstacle_class):
    def __init__(self, obstacle_path, screen_width, screen_height, scale_factor=0.5, speed=3):
        super().__init__(obstacle_path, screen_width, screen_height, scale_factor, speed)

    def effect(self, player, player_HP):
        if player_HP.hp < 3:
            player_HP.hp += 1


class Lane_Switcher(decrease_hp):
    """อุปสรรคที่สลับเลนระหว่างเลื่อนมาทางซ้าย
    ขั้นตอน: idle (วิ่งตรง) -> warn (โชว์เงาที่เลนปลายทาง) -> move (เลื่อนไปเลนใหม่)
    ปรับความยากได้จากค่าคงที่ด้านล่าง"""

    SPEED_FACTOR = 0.6      # ช้ากว่าของอื่น จะได้มีเวลาสลับเลนได้หลายครั้งก่อนถึงผู้เล่น
    WARN_TIME = 0.15        # วินาทีที่โชว์เงาเตือนก่อนสลับ (ยิ่งน้อยยิ่งยาก)
    MOVE_TIME = 0.2         # วินาทีที่ใช้เลื่อนข้ามเลน (ครั้งละ 1 เลน)
    IDLE_MIN = 0.0          # พักระหว่างการสลับแต่ละครั้ง (สุ่มระหว่าง MIN-MAX)
    IDLE_MAX = 0.1
    NO_SWITCH_X = 0         # สลับต่อเนื่องจนหลุดจอ (ตั้งเป็น 650 ถ้าอยากให้หยุดสลับตอนใกล้ผู้เล่น)

    def __init__(self, obstacle_path, screen_width, screen_height, scale_factor=0.5, speed=3):
        super().__init__(obstacle_path, screen_width, screen_height, scale_factor, speed)
        self.obs_image, self.ghost = get_tinted(self.obs_image)
        self.mask = get_mask(self.obs_image)

        self.lane = self.lanes_y.index(self.y)
        self.target_lane = self.lane
        self.direction = random.choice((-1, 1))  # -1 = ขึ้น, 1 = ลง
        self.y = float(self.y)
        self.start_y = self.y
        self.phase = "idle"
        self.timer = random.uniform(0.05, 0.2)

    def update(self):
        self.x -= self.speed * self.SPEED_FACTOR * 60 * delta_time
        self.timer -= delta_time

        if self.phase == "idle":
            if self.timer <= 0 and self.x > self.NO_SWITCH_X:
                # ไล่ทีละเลน 0->1->2->1->0 ... แล้วเด้งกลับเมื่อถึงขอบ
                if not 0 <= self.lane + self.direction <= 2:
                    self.direction = -self.direction
                self.target_lane = self.lane + self.direction
                self.phase = "warn"
                self.timer = self.WARN_TIME

        elif self.phase == "warn":
            if self.timer <= 0:
                self.phase = "move"
                self.timer = self.MOVE_TIME
                self.start_y = self.y

        elif self.phase == "move":
            t = max(0.0, 1 - self.timer / self.MOVE_TIME)
            t = t * t * (3 - 2 * t)  # smoothstep ให้การเลื่อนนุ่มนวล
            end_y = self.lanes_y[self.target_lane]
            self.y = self.start_y + (end_y - self.start_y) * t
            if self.timer <= 0:
                self.y = float(end_y)
                self.lane = self.target_lane
                self.phase = "idle"
                self.timer = random.uniform(self.IDLE_MIN, self.IDLE_MAX)

    def draw(self, screen):
        if self.phase in ("warn", "move"):
            screen.blit(self.ghost, (round(self.x), self.lanes_y[self.target_lane]))
        screen.blit(self.obs_image, (round(self.x), round(self.y)))


class coin_class(Obstacle_class):
    def __init__(self, preloaded_frames, screen_width, screen_height, speed=3):
        # ประกาศค่ากว้าง/สูงและสร้าง Mask ก่อนเรียก super().__init__ เพื่อป้องกัน AttributeError
        self.animation_frames = preloaded_frames
        self.image = self.animation_frames[0]
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.mask = get_mask(self.image)

        super().__init__(None, screen_width, screen_height, 1.0, speed)

        top_of_road = screen_height // 2
        road_height = screen_height // 2
        lane_height = road_height // 3
        self.lanes_y = [
            top_of_road + lane_height // 2 - self.height // 2,
            top_of_road + 1 * lane_height + lane_height // 2 - self.height // 2,
            top_of_road + 2 * lane_height + lane_height // 2 - self.height // 2
        ]
        self.y = random.choice(self.lanes_y)
        self.x = screen_width

        self.current_frame = 0
        self.animation_timer = 0
        self.frame_speed = 200

    def update(self):
        self.x -= self.speed * 60 * delta_time
        current_time = pygame.time.get_ticks()
        if current_time - self.animation_timer >= self.frame_speed:
            self.animation_timer = current_time
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]

    def draw(self, screen):
        screen.blit(self.image, (round(self.x), self.y))


class HP:
    def __init__(self, heart_path1, heart_path2, max_hp):
        self.hp = max_hp
        self.image = load_scaled(heart_path1, scale=0.05)
        self.image2 = load_scaled(heart_path2, scale=0.05)
        self.width, self.height = self.image.get_size()

        self.spacing = 10
        self.start_x = 30
        self.start_y = 30

    def draw(self, screen):
        for i in range(0, 3):
            x_pos = self.start_x + (i * (self.width + self.spacing))
            if i < self.hp:
                screen.blit(self.image, (x_pos, self.start_y))
            else:
                screen.blit(self.image2, (x_pos, self.start_y))


# --- GAME CONTROL FUNCTIONS ---

def set_game_over():
    global state
    state = "gameover"


def quit_game():
    global Program
    Program = False


def start_game():
    global state, player, background1, obstacles_list, coin_list
    global coins_collected, player_hp, current_world_speed, is_speed_boosted
    global last_spawn_time, last_spawn_time2, speed_boost_timer
    global base_speed, game_time, speed_level

    state = "playing"
    coins_collected = 0
    base_speed = BASE_SPEED
    current_world_speed = BASE_SPEED
    game_time = 0.0
    speed_level = 0
    is_speed_boosted = False
    speed_boost_timer = 0
    obstacles_list.clear()
    coin_list.clear()

    last_spawn_time = pygame.time.get_ticks()
    last_spawn_time2 = pygame.time.get_ticks()

    # ฉากหลัง: ใช้ object เดียวที่มี 2 ภาพต่อกันก็ครอบคลุมทั้งจอแล้ว
    # (ของเดิมมี 2 object = blit ฉากหลัง 4 ครั้งต่อเฟรม ซ้อนกันโดยไม่จำเป็น)
    background1 = Background_class(os.path.join('gamepicture', 'view3.jpg'), SCREEN_WIDTH, SCREEN_HEIGHT, current_world_speed)

    # โหลดตัวละคร
    car_frames = [
        os.path.join('gamepicture', 'car1_frame1.png'),
        os.path.join('gamepicture', 'car1_frame2.png'),
        os.path.join('gamepicture', 'car1_frame3.png'),
        os.path.join('gamepicture', 'car1_frame4.png')
    ]
    player = player_class(50, SCREEN_HEIGHT // 2, car_frames, 0.3, 10)
    player.set_lane(SCREEN_HEIGHT)

    player_hp = HP(os.path.join('gamepicture', 'heart.png'), os.path.join('gamepicture', 'grey_heart.png'), 3)


def create_menus():
    global menu, game_over_menu, time_up_menu
    menu = PixelMenu("CAR GAME", [("START", start_game), ("QUIT", quit_game)])
    game_over_menu = PixelMenu("CRASHED", [("RETRY", start_game), ("QUIT", quit_game)],
                               lambda: f"Coins: {coins_collected}")
    time_up_menu = PixelMenu("TIME UP!", [("RETRY", start_game), ("QUIT", quit_game)],
                             lambda: f"Coins: {coins_collected}")


# --- MAIN EXECUTION ---

if __name__ == "__main__":
    create_menus()

    # ข้อมูลประเภทอุปสรรคที่จะสุ่มเกิด
    obstacle_types = [
        (Speed_Boost, os.path.join('gamepicture', 'speedup.png'), 0.05, 1),       # ไอเทมเร่งความเร็ว
        (Speed_Down, os.path.join('gamepicture', 'speeddown.png'), 0.05, 1),     # ไอเทมสโลว์
        (increase_hp, os.path.join('gamepicture', 'medicine.png'), 0.05, 1),      # ยาเพิ่มเลือด
        (decrease_hp, os.path.join('gamepicture', 'obstacle1.png'), 0.05, 1),     # สิ่งกีดขวางลดเลือด
        (Lane_Switcher, os.path.join('gamepicture', 'obstacle1.png'), 0.05, 1),   # สิ่งกีดขวางที่สลับเลน (สีม่วง)
    ]
    # น้ำหนักการสุ่ม: ตัวเลขยิ่งเยอะยิ่งออกบ่อย
    obstacle_weights = [4, 4, 3, 10, 5]  # [Speed_Boost, Speed_Down, increase_hp, decrease_hp, Lane_Switcher]

    # เหรียญ (โหลดล่วงหน้า)
    coin_frames = [
        load_scaled(os.path.join('gamepicture', n), scale=0.6)
        for n in ('Coin1.png', 'Coin2.png', 'Coin3.png')
    ]

    # โหลดรูปทั้งหมดไว้ใน cache ตั้งแต่เปิดเกม จะได้ไม่มีสะดุดตอนเล่นจริง
    load_scaled(os.path.join('gamepicture', 'view3.jpg'), size=(SCREEN_WIDTH, SCREEN_HEIGHT), alpha=False)
    load_scaled(os.path.join('gamepicture', 'view3.jpg'), size=(SCREEN_WIDTH, SCREEN_HEIGHT), alpha=False, flip=True)
    for n in range(1, 5):
        load_scaled(os.path.join('gamepicture', f'car1_frame{n}.png'), scale=0.3)
    load_scaled(os.path.join('gamepicture', 'heart.png'), scale=0.05)
    load_scaled(os.path.join('gamepicture', 'grey_heart.png'), scale=0.05)
    for cls_, p, sc, _ in obstacle_types:
        base_img = load_scaled(p, scale=sc)
        get_mask(base_img)
        if cls_ is Lane_Switcher:
            get_tinted(base_img)

    # เตรียมค่าคงที่ของถนน (ไม่ต้องคำนวณใหม่ทุกเฟรม)
    road_top = SCREEN_HEIGHT // 2
    road_height = SCREEN_HEIGHT // 2
    lane_height = road_height // 3
    road_rect = (0, road_top, SCREEN_WIDTH, road_height)
    line1_y = road_top + lane_height
    line2_y = road_top + lane_height * 2

    # cache ข้อความคะแนนเหรียญ เรนเดอร์ใหม่เฉพาะตอนคะแนนเปลี่ยน
    coin_text = font.render("Coins: 0", True, (255, 215, 0))
    last_rendered_coins = 0

    # cache ข้อความเวลา/เลเวลความเร็ว
    time_text = None
    time_key = None

    while Program:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                Program = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    Program = False
                if state == "playing":
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        player.move_up()
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        player.move_down()

        screen.fill((30, 30, 40))

        if state == "menu":
            menu.update(events)
            menu.draw(screen)

        elif state == "playing":
            current_time = pygame.time.get_ticks()

            # นับเวลาเล่น และเพิ่มความเร็วทุก SPEED_UP_INTERVAL วินาที
            game_time += delta_time
            new_level = int(game_time // SPEED_UP_INTERVAL)
            while speed_level < new_level:
                speed_level += 1
                base_speed += SPEED_UP_STEP
                current_world_speed += SPEED_UP_STEP
                background1.speed = current_world_speed
                for obs in obstacles_list:
                    obs.speed = current_world_speed
                for c in coin_list:
                    c.speed = current_world_speed

            # เช็คหมดเวลา Speed Boost / Speed Down
            if is_speed_boosted and current_time >= speed_boost_timer:
                current_world_speed = base_speed
                background1.speed = current_world_speed
                for obs in obstacles_list:
                    obs.speed = current_world_speed
                for c in coin_list:
                    c.speed = current_world_speed
                is_speed_boosted = False

            # ระบบสปอนอุปสรรค
            if current_time - last_spawn_time >= spawn_obstacles_time:
                cls, p, sc, spd_offset = random.choices(obstacle_types, weights=obstacle_weights, k=1)[0]
                obstacles_list.append(cls(p, SCREEN_WIDTH, SCREEN_HEIGHT, sc, current_world_speed + spd_offset))
                last_spawn_time = current_time

            # ระบบสปอนเหรียญ
            if current_time - last_spawn_time2 >= spawn_obstacles_time2:
                coin_list.append(coin_class(coin_frames, SCREEN_WIDTH, SCREEN_HEIGHT, speed=current_world_speed))
                last_spawn_time2 = current_time

            # อัปเดตฉากหลัง
            background1.update()

            # อัปเดตและเช็คชนเหรียญ
            for c in coin_list[:]:
                c.update()
                offset = (round(c.x) - player.x, c.y - player.y)
                if player.mask.overlap(c.mask, offset):
                    coins_collected += 1
                    coin_list.remove(c)
                elif c.x <= -c.width:
                    coin_list.remove(c)

            # อัปเดตและเช็คชนอุปสรรค
            for obs in obstacles_list[:]:
                obs.update()
                offset = (round(obs.x) - player.x, round(obs.y) - player.y)
                if player.mask.overlap(obs.mask, offset):
                    obs.effect(player, player_hp)
                    obstacles_list.remove(obs)
                    if player_hp.hp <= 0:
                        set_game_over()
                elif obs.x <= -obs.width:
                    obstacles_list.remove(obs)

            player.update()

            # --- ส่วนการวาดภาพลงหน้าจอ ---
            background1.draw(screen)

            # วาดพื้นถนนครึ่งล่าง
            pygame.draw.rect(screen, (50, 50, 50), road_rect)
            pygame.draw.line(screen, "White", (0, line1_y), (SCREEN_WIDTH, line1_y), 3)
            pygame.draw.line(screen, "White", (0, line2_y), (SCREEN_WIDTH, line2_y), 3)

            # วาดอุปสรรคและเหรียญ
            for obs in obstacles_list:
                obs.draw(screen)

            for c in coin_list:
                c.draw(screen)

            # วาด UI (เลือด และ คะแนนเหรียญ)
            player_hp.draw(screen)
            if coins_collected != last_rendered_coins:
                coin_text = font.render(f"Coins: {coins_collected}", True, (255, 215, 0))
                last_rendered_coins = coins_collected
            screen.blit(coin_text, coin_text.get_rect(topright=(SCREEN_WIDTH - 20, 20)))

            secs_left = max(0, math.ceil(GAME_DURATION - game_time))
            if (secs_left, speed_level) != time_key:
                time_key = (secs_left, speed_level)
                color = (255, 90, 90) if secs_left <= 10 else (255, 255, 255)
                time_text = font.render(f"Time: {secs_left}   Speed Lv.{speed_level + 1}", True, color)
            screen.blit(time_text, time_text.get_rect(midtop=(SCREEN_WIDTH // 2, 20)))

            player.draw(screen)

            # หมดเวลา (ถ้าเลือดหมดในเฟรมเดียวกัน ให้ถือว่าชนก่อน)
            if state == "playing" and game_time >= GAME_DURATION:
                state = "timeup"

        elif state == "gameover":
            game_over_menu.update(events)
            game_over_menu.draw(screen)

        elif state == "timeup":
            time_up_menu.update(events)
            time_up_menu.draw(screen)

        pygame.display.flip()
        # จำกัด delta_time ไม่ให้เฟรมที่ค้าง (เช่นตอนโหลด) ทำให้ของวาร์ปข้ามจอ
        delta_time = min(clock.tick(60) / 1000, MAX_DELTA)

pygame.quit()
sys.exit()
