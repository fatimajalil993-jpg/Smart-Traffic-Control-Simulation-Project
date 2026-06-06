import pygame
import random
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart City Control Center")
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GRAY = (100, 100, 100)
RED = (255, 50, 50)
YELLOW = (255, 255, 50)
GREEN = (50, 255, 50)
CITY_GROUND = (40, 40, 45)
DASHBOARD = (20, 20, 30)
BUILDING_COLOR = (70, 70, 80)
HEADLIGHT = (255, 255, 200)
CENTER = 400
ROAD_SIZE = 140
clock = pygame.time.Clock()

try:
    siren_sound = pygame.mixer.Sound("mixkit-ambulance-siren-us-1642.wav")
except:
    siren_sound = None

buildings = []
while len(buildings) < 12:
    w = random.randint(60, 90)
    h = random.randint(60, 90)
    x = random.choice([random.randint(20, 280), random.randint(540, 750)])
    y = random.choice([random.randint(20, 280), random.randint(540, 750)])
    new_rect = pygame.Rect(x, y, w, h)
    ok = True
    for b in buildings:
        if new_rect.inflate(20, 20).colliderect(b):
            ok = False
    if ok:
        buildings.append(new_rect)

def draw_city():
    screen.fill(CITY_GROUND)
    for b in buildings:
        pygame.draw.rect(screen, BUILDING_COLOR, b)
        pygame.draw.rect(screen, BLACK, b, 2)
        for wx in range(b.x + 10, b.x + b.width - 10, 20):
            for wy in range(b.y + 10, b.y + b.height - 10, 20):
                pygame.draw.rect(screen, (255, 255, 150), (wx, wy, 5, 5))

    pygame.draw.rect(screen, BLACK, (CENTER - 70, 0, ROAD_SIZE, 800))
    pygame.draw.rect(screen, BLACK, (0, CENTER - 70, 800, ROAD_SIZE))

    for i in range(0, 800, 40):
        pygame.draw.rect(screen, WHITE, (CENTER - 2, i, 4, 20))
        pygame.draw.rect(screen, WHITE, (i, CENTER - 2, 20, 4))

def draw_lights(active_lane, phase):
    pos = {
        "RIGHT": (480, 260),
        "LEFT": (280, 480),
        "UP": (280, 260),
        "DOWN": (480, 480)
    }
    for side in pos:
        x, y = pos[side]
        pygame.draw.rect(screen, (20, 20, 20), (x, y, 40, 80))

        r = (50, 0, 0)
        yel = (50, 50, 0)
        g = (0, 50, 0)

        if side == active_lane:
            if phase == "GREEN":
                g = GREEN
            elif phase == "YELLOW":
                yel = YELLOW
            else:
                r = RED
        else:
            r = RED

        pygame.draw.circle(screen, r, (x + 20, y + 20), 8)
        pygame.draw.circle(screen, yel, (x + 20, y + 40), 8)
        pygame.draw.circle(screen, g, (x + 20, y + 60), 8)

def monitorboard(active_lane, phase, count, emergency):
    pygame.draw.rect(screen, DASHBOARD, (800, 0, 200, 800))
    font = pygame.font.SysFont("Arial", 22, bold=True)

    screen.blit(font.render("URBAN MONITOR", True, WHITE), (820, 40))
    screen.blit(font.render(f"Lane: {active_lane}", True, GREEN), (820, 120))
    screen.blit(font.render(f"Phase: {phase}", True, WHITE), (820, 180))
    screen.blit(font.render(f"Traffic: {count} CARS", True, WHITE), (820, 240))

    if emergency:
        if (pygame.time.get_ticks() // 400) % 2 == 0:
            pygame.draw.rect(screen, RED, (810, 360, 180, 50))
            screen.blit(font.render("EMERGENCY", True, WHITE), (835, 372))

cars = []
signal = ["RIGHT", "DOWN", "LEFT", "UP"]
index = 0
phase = "GREEN"
timer = 0
siren = False
score = 0
running = True
while running:
    draw_city()
    active = signal[index]
    emergency = False
    for c in cars:
        if c["em"]:
            emergency = True
            active = c["dir"]
            phase = "GREEN"
    if emergency:
        if siren_sound and not siren:
            siren_sound.play(-1)
            siren = True
    else:
        if siren:
            if siren_sound:
                siren_sound.stop()
            siren = False
            timer += 1
        if phase == "GREEN" and timer > 180:
            phase = "YELLOW"
            timer = 0
        elif phase == "YELLOW" and timer > 60:
            phase = "GREEN"
            timer = 0
            index = (index + 1) % 4
    draw_lights(active, phase)
    if random.random() < 0.03 and len(cars) < 12:
        d = random.choice(signal)
        em = random.random() < 0.1
        car = {
            "dir": d,
            "em": em,
            "speed": 6 if em else 3
        }
        car["color"] = WHITE if em else (random.randint(50, 150), 100, 255)
        if d == "RIGHT":
            car["x"], car["y"] = -50, CENTER + 15
        elif d == "LEFT":
            car["x"], car["y"] = 850, CENTER - 45
        elif d == "DOWN":
            car["x"], car["y"] = CENTER - 45, -50
        elif d == "UP":
            car["x"], car["y"] = CENTER + 15, 850
        cars.append(car)
    for car in cars[:]:
        move = True
        if not car["em"]:
            if car["dir"] != active or phase != "GREEN":
                if (car["dir"] == "RIGHT" and 280 < car["x"] < 290) or \
                   (car["dir"] == "LEFT" and 500 < car["x"] < 510) or \
                   (car["dir"] == "DOWN" and 280 < car["y"] < 290) or \
                   (car["dir"] == "UP" and 500 < car["y"] < 510):
                    move = False
        for o in cars:
            if o == car:
                continue
            if o["dir"] == car["dir"]:
                if car["dir"] == "RIGHT" and 0 < (o["x"] - car["x"]) < 70:
                    move = False
                if car["dir"] == "LEFT" and 0 < (car["x"] - o["x"]) < 70:
                    move = False
                if car["dir"] == "DOWN" and 0 < (o["y"] - car["y"]) < 70:
                    move = False
                if car["dir"] == "UP" and 0 < (car["y"] - o["y"]) < 70:
                    move = False
        if move:
            if car["dir"] == "RIGHT":
                car["x"] += car["speed"]
            elif car["dir"] == "LEFT":
                car["x"] -= car["speed"]
            elif car["dir"] == "DOWN":
                car["y"] += car["speed"]
            elif car["dir"] == "UP":
                car["y"] -= car["speed"]
        w, h = (40, 25) if car["dir"] in ["LEFT", "RIGHT"] else (25, 40)
        pygame.draw.rect(
            screen,
            car["color"],
            (car["x"], car["y"], w, h),
            border_radius=4
        )
        if car["dir"] == "RIGHT":
            pygame.draw.circle(screen, HEADLIGHT, (car["x"] + w, car["y"] + 5), 3)
            pygame.draw.circle(screen, HEADLIGHT, (car["x"] + w, car["y"] + h - 5), 3)
        elif car["dir"] == "LEFT":
            pygame.draw.circle(screen, HEADLIGHT, (car["x"], car["y"] + 5), 3)
            pygame.draw.circle(screen, HEADLIGHT, (car["x"], car["y"] + h - 5), 3)
        elif car["dir"] == "DOWN":
            pygame.draw.circle(screen, HEADLIGHT, (car["x"] + 5, car["y"] + h), 3)
            pygame.draw.circle(screen, HEADLIGHT, (car["x"] + w - 5, car["y"] + h), 3)
        elif car["dir"] == "UP":
            pygame.draw.circle(screen, HEADLIGHT, (car["x"] + 5, car["y"]), 3)
            pygame.draw.circle(screen, HEADLIGHT, (car["x"] + w - 5, car["y"]), 3)
        if car["em"]:
            if (pygame.time.get_ticks() // 250) % 2 == 0:
                pygame.draw.rect(screen, (0, 0, 255), (car["x"] + 5, car["y"] + 5, 10, 10))
            else:
                if car["dir"] in ["LEFT", "RIGHT"]:
                    pygame.draw.rect(screen, (255, 0, 0), (car["x"] + 18, car["y"] + 5, 10, 10))
                else:
                    pygame.draw.rect(screen, (255, 0, 0), (car["x"] + 5, car["y"] + 18, 10, 10))
        if car["x"] < -100 or car["x"] > 1000 or car["y"] < -100 or car["y"] > 1000:
            cars.remove(car)
    monitorboard(active, phase, len(cars), emergency)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                index = (index + 1) % 4
                phase = "GREEN"
                timer = 0
    pygame.display.flip()
    clock.tick(60)
pygame.quit()