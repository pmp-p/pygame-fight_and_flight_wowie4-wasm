import asyncio
import pygame as pg
import os
import random
from pygame.locals import *
import sys
from math import *


def load_image(file):
    """loads an image, prepares it for play"""
    file = os.path.join("assets", "sprites", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit('Could not load image "%s" %s' % (file, pg.get_error()))
    return surface.convert_alpha()


def load_sound(file):
    """because pygame can be be compiled without mixer."""
    if not pg.mixer:
        return None
    file = os.path.join("assets", "sounds", file)
    try:
        sound = pg.mixer.Sound(file)
        return sound
    except pg.error:
        print("Warning, unable to load, %s" % file)
    return None


WIN_WIDTH, WIN_HEIGHT = 1500, 750

SPACE_BLUE = pg.Color(0, 0, 64)

pg.init()
WIN = pg.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pg.display.set_caption("Spaceship AI Game")

BG_TILE = pg.transform.scale(
    load_image("background_tile.png").convert_alpha(), (750, 750)
)
bg_width, bg_height = BG_TILE.get_width(), BG_TILE.get_height()

HEART_ICON = pg.transform.scale(load_image("heart.png").convert_alpha(), (30, 30))
HEART_ICON_2 = pg.transform.scale(
    load_image("heart_half.png").convert_alpha(), (30, 30)
)

LOGO_P1 = pg.transform.scale(load_image("Logo_p1.png").convert_alpha(), (500, 200))
LOGO_P2 = pg.transform.scale(load_image("Logo_p2.png").convert_alpha(), (500, 200))
LOGO_P3 = pg.transform.scale(load_image("Logo_p3.png").convert_alpha(), (250, 100))

WOWIE_LOGO_1 = pg.transform.scale(
    load_image("WowieJam4.png").convert_alpha(), (400, 100)
)
WOWIE_LOGO_2 = pg.transform.scale(
    load_image("WowieJam4.png").convert_alpha(), (200, 50)
)

# explosion = GIFImage(os.path.join("assets", "sprites", "explosion.gif"))

BGM = pg.mixer.music.load(os.path.join("assets", "sounds", "Lightless Dawn.ogg"))
pg.mixer.music.play(-1)

HURT_SOUND = load_sound("170148__timgormly__8-bit-hurt1.ogg")
ZAP_SOUND = load_sound("512471__michael-grinnell__electric-zap.ogg")
BOOM_SOUND = load_sound("317751__jalastram__sfx-explosion-08.ogg")
GROWL_SOUND = load_sound("416045__giddster__monster-growl-8-shortened.ogg")
KILL_SOUND = load_sound("527525__jerimee__vibrating-thud.ogg")
SHOOT_SOUND = load_sound("492486__alderman2k__laser-shoot8.ogg")
MOVE_SOUND = load_sound("25761__wolfsinger__space-engine.ogg")
CLICK_SOUND = load_sound("Face_hit_1.ogg")
CLACK_SOUND = load_sound("Face_hit_2.ogg")
WIN_SOUND = load_sound("585801__colorscrimsontears__time-travel-future.ogg")

GROWL_SOUND.set_volume(0.5)
BOOM_SOUND.set_volume(0.5)
SHOOT_SOUND.set_volume(0.5)

INSTR_FONT = pg.font.Font(os.path.join("assets", "fonts", "DatcubBold-4BMy6.ttf"), 28)
CRED_FONT = pg.font.Font(os.path.join("assets", "fonts", "DatcubBold-4BMy6.ttf"), 20)

FPS = 60

clock = pg.time.Clock()

LOSE_EVENT = pg.USEREVENT + 1
WIN_EVENT = pg.USEREVENT + 2


class PlayerShip(pg.sprite.Sprite):
    images = [
        pg.transform.scale(
            load_image("spaceship_placeholder.png").convert_alpha(), (80, 80)
        ),
        pg.transform.scale(
            load_image("spaceship_placeholder_inv.png").convert_alpha(), (80, 80)
        ),
    ]

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = PlayerShip.images[0]
        self.pos = (WIN_WIDTH // 2, WIN_HEIGHT // 2)
        self.rect = self.image.get_rect(center=self.pos)
        self.angle = 0
        self.speed = 0
        self.speedPower = 3
        self.anglePower = 3
        self.gun = PlayerGun()
        self.health = 10
        self.invincibilityTimer = 0

    def update(self):
        if self.invincibilityTimer > 0:
            self.invincibilityTimer -= 1
        else:
            self.image = PlayerShip.images[0]
            self.gun.changeImage(0)
        self.rect.center = self.pos

    def getSpeedAndAngle(self):
        return self.speed, self.angle

    def changeAngle(self, target):
        if self.anglePower == 0:
            self.angle = random.random() * 2 * pi
        elif self.anglePower == 1:
            self.angle = atan2(
                self.pos[1] - target[1], self.pos[0] - target[0]
            ) + random.randint(-3, 4)
        elif self.anglePower == 2:
            self.angle = atan2(
                self.pos[1] - target[1], self.pos[0] - target[0]
            ) + random.randint(-1, 2)
        elif self.anglePower == 3:
            self.angle = atan2(self.pos[1] - target[1], self.pos[0] - target[0])

    def changeSpeed(self):
        if self.speed == 0:
            MOVE_SOUND.play(-1)
        self.gun.changeShipSpeedPower(self.speedPower)
        if self.speedPower == 0:
            self.speed = random.randint(1, 12)
        elif self.speedPower == 1:
            self.speed = random.randint(2, 10)
        elif self.speedPower == 2:
            self.speed = random.randint(3, 7)
        elif self.anglePower == 3:
            self.speed = 5
        MOVE_SOUND.set_volume(self.speed * 0.4 / 12)

    def changeSpeedPower(self, newPower):
        if self.speedPower != newPower:
            ZAP_SOUND.play()
        self.speedPower = newPower

    def changeAnglePower(self, newPower):
        if self.anglePower != newPower:
            ZAP_SOUND.play()
        self.anglePower = newPower

    def setGunDir(self, direction):
        self.gun.setDirection(direction)

    def fireGun(self):
        return self.gun.fire(self.anglePower, self.pos)

    def getHurt(self):
        if self.invincibilityTimer == 0:
            HURT_SOUND.play()
            self.image = PlayerShip.images[1]
            self.gun.changeImage(1)
            self.health -= 1
            if self.health == 0:
                pg.event.post(pg.event.Event(LOSE_EVENT))
            else:
                self.invincibilityTimer = 3 * FPS

    def getHealth(self):
        return self.health


class PlayerGun(pg.sprite.Sprite):
    images = [
        pg.transform.scale(load_image("gun_placeholder.png").convert_alpha(), (80, 80)),
        pg.transform.scale(
            load_image("gun_placeholder_hit.png").convert_alpha(), (80, 80)
        ),
    ]
    offsetFromCenter = 60

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = PlayerGun.images[0]
        self.pos = (WIN_WIDTH // 2, WIN_HEIGHT // 2)
        self.original_rect = PlayerShip.images[0].get_rect(center=self.pos)
        self.rect = self.original_rect.copy()
        self.angleFromPlayer = 0
        self.direction = 0
        self.shipSpeedPower = 3
        self.hitState = 0

    def setDirection(self, direction):
        self.direction = direction

    def updatePosition(self):
        new_x = self.original_rect.center[0] - PlayerGun.offsetFromCenter * sin(
            radians(self.angleFromPlayer)
        )
        new_y = self.original_rect.center[1] - PlayerGun.offsetFromCenter * cos(
            radians(self.angleFromPlayer)
        )
        self.pos = (new_x, new_y)

    def update(self):
        self.updatePosition()
        powerLevels = {3: 0.5, 2: 1, 1: 2, 0: 4}
        self.angleFromPlayer += self.direction * powerLevels[self.shipSpeedPower]
        self.image = pg.transform.rotate(
            PlayerGun.images[self.hitState], self.angleFromPlayer
        )
        self.rect = self.image.get_rect(center=self.pos)

    def fire(self, shipAngPower, pos):
        powerLevels = {0: 5, 1: 3, 2: 2, 3: 1}
        SHOOT_SOUND.play()
        return Bullet(powerLevels[shipAngPower], pos, self.angleFromPlayer)

    def changeShipSpeedPower(self, newPower):
        self.shipSpeedPower = newPower

    def changeImage(self, hitState):
        self.hitState = hitState


class Bullet(pg.sprite.Sprite):
    base_image = pg.transform.scale(
        load_image("bullet_placeholder.png").convert_alpha(), (80, 80)
    )
    size = 2
    speed = 20
    MAX_LIFE = FPS * 5

    def __init__(self, damage, pos, angle):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.damage = damage
        self.image = pg.transform.scale(
            Bullet.base_image, (80 + 5 * damage, 80 + 5 * damage)
        )
        self.angle = radians(angle)
        self.pos = pos
        self.rect = self.image.get_rect(center=self.pos)
        self.life = Bullet.MAX_LIFE

    def updatePosition(self, worldAngle, worldSpeed):
        travelling_x = Bullet.speed * sin(self.angle)
        travelling_y = Bullet.speed * cos(self.angle)
        new_x = self.pos[0] - travelling_x + worldSpeed * cos(worldAngle)
        new_y = self.pos[1] - travelling_y + worldSpeed * sin(worldAngle)
        self.pos = (new_x, new_y)

    def update(self, angle, speed):
        self.life -= 1
        if self.life == 0:
            self.kill()
        self.updatePosition(angle, speed)
        self.rect.center = self.pos
        # print(self.pos)


class Goal(pg.sprite.Sprite):
    image = pg.transform.scale(
        load_image("goal_placeholder.png").convert_alpha(), (80, 80)
    )

    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.pos = pos
        self.rect = Goal.image.get_rect(center=self.pos)

    def updatePosition(self, angle, speed):
        new_x = self.pos[0] + speed * cos(angle)
        new_y = self.pos[1] + speed * sin(angle)
        self.pos = (new_x, new_y)

    def update(self, angle, speed):
        self.updatePosition(angle, speed)
        self.rect.center = self.pos


class Enemy(pg.sprite.Sprite):
    image = pg.transform.scale(
        load_image("enemy_placeholder.png").convert_alpha(), (80, 80)
    )
    speed = 4
    detectionRectSize = 500

    def __init__(self, pos):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = Enemy.image
        self.pos = pos
        self.rect = Goal.image.get_rect(center=self.pos)
        self.target = None
        self.detectionRect = Rect(
            self.pos[0] - (Enemy.detectionRectSize // 2),
            self.pos[1] - (Enemy.detectionRectSize // 2),
            Enemy.detectionRectSize,
            Enemy.detectionRectSize,
        )
        self.detectionRect.center = self.pos
        self.health = 5
        self.flip = False

    def updateTarget(self, target):
        if self.target == None and self.detectionRect.collidepoint(target):
            self.target = target
            GROWL_SOUND.play()
        elif self.target != None and not self.detectionRect.collidepoint(target):
            self.target = None

    def updatePosition(self, angle, worldSpeed):
        travelling_x = 0
        travelling_y = 0
        if self.target != None and self.target != self.pos:
            hyp = sqrt(
                abs(self.target[0] - self.pos[0]) ** 2
                + abs(self.target[1] - self.pos[1]) ** 2
            )
            travelling_x = self.speed * (self.target[0] - self.pos[0]) / hyp
            travelling_y = self.speed * (self.target[1] - self.pos[1]) / hyp
        new_x = self.pos[0] + travelling_x + worldSpeed * cos(angle)
        new_y = self.pos[1] + travelling_y + worldSpeed * sin(angle)
        self.pos = (new_x, new_y)

    def update(self, angle, speed, target):
        if self.health <= 0:
            KILL_SOUND.play()
            self.kill()
        self.updatePosition(angle, speed)
        self.rect.center = self.pos
        self.detectionRect.center = self.pos
        self.updateTarget(target)
        if target[0] < self.pos[0] and not self.flip:
            self.flip = True
            self.image = pg.transform.flip(self.image, True, False)
        elif target[0] > self.pos[0] and self.flip:
            self.flip = False
            self.image = pg.transform.flip(self.image, True, False)

    def lowerHealth(self, damage):
        self.health -= damage
        return self.health <= 0


class UI(pg.sprite.Sprite):
    images = [
        pg.transform.scale(load_image("hud_base.png").convert_alpha(), (500, 250)),
        pg.transform.scale(load_image("hud_opt1.png").convert_alpha(), (500, 250)),
        pg.transform.scale(load_image("hud_opt2.png").convert_alpha(), (500, 250)),
    ]

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = UI.images[1]
        self.rect = self.image.get_rect(
            center=(WIN_WIDTH // 2, WIN_HEIGHT - (self.image.get_height() // 2))
        )
        self.overlaySurface = pg.Surface(
            (self.image.get_width(), self.image.get_height()), pg.SRCALPHA
        )

    def selectOption(self, option):
        self.image = UI.images[option]


class Arrow(pg.sprite.Sprite):
    image = pg.transform.scale(load_image("target_arrow.png").convert_alpha(), (50, 50))
    offsetFromCenter = 170

    def __init__(self, destinationObject):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.pos = (WIN_WIDTH // 2, WIN_HEIGHT // 2)
        self.original_rect = Arrow.image.get_rect(center=self.pos)
        self.rect = self.original_rect.copy()
        self.dest = destinationObject

    def updatePosition(self, newAngle):
        new_x = self.original_rect.center[0] + Arrow.offsetFromCenter * cos(newAngle)
        new_y = self.original_rect.center[1] + Arrow.offsetFromCenter * sin(newAngle)
        self.pos = (new_x, new_y)

    def update(self):
        newAngle = atan2(
            self.dest.pos[1] - WIN_HEIGHT // 2, self.dest.pos[0] - WIN_WIDTH // 2
        )
        self.updatePosition(newAngle)
        self.image = pg.transform.rotate(Arrow.image, 270 - degrees(newAngle))
        self.rect = self.image.get_rect(center=self.pos)


objectGroup = pg.sprite.Group()
playerGroup = pg.sprite.Group()
angleRefToPlayerGroup = pg.sprite.Group()
enemyGroup = pg.sprite.Group()
bulletGroup = pg.sprite.Group()
UIGroup = pg.sprite.Group()
allGroup = pg.sprite.RenderUpdates()

PlayerGun.containers = allGroup, angleRefToPlayerGroup, playerGroup
PlayerShip.containers = allGroup, playerGroup
Goal.containers = allGroup, objectGroup
Enemy.containers = allGroup, enemyGroup
Bullet.containers = allGroup, bulletGroup, objectGroup
UI.containers = UIGroup
Arrow.containers = allGroup, angleRefToPlayerGroup


def generateEnemyClusters(exitPos):
    clusterCoords = []
    xLengthToExit = WIN_WIDTH // 2 - exitPos[0]
    yLengthToExit = WIN_HEIGHT // 2 - exitPos[1]

    for i in range(1, 4):
        clusterCoords.append(
            (round(i * xLengthToExit / 4), round(i * yLengthToExit / 4))
        )

    while len(clusterCoords) < 80:
        addCluster = True
        if exitPos[0] > 0:
            x = random.randint(WIN_WIDTH, exitPos[0])
        else:
            x = random.randint(exitPos[0], 0)
        if exitPos[1] > 0:
            y = random.randint(WIN_HEIGHT, exitPos[1])
        else:
            y = random.randint(exitPos[1], 0)
        for coord in clusterCoords:
            if abs(x - coord[0]) < 100 or abs(y - coord[1]) < 100:
                addCluster = False
        if addCluster:
            len(clusterCoords)
            clusterCoords.append((x, y))
    return clusterCoords


def spawnEnemies(clusterCoords):
    enemyCount = 0
    for clusterCoord in clusterCoords:
        clusterCount = random.randint(3, 11)
        for i in range(clusterCount):
            x = random.randint(clusterCoord[0] - 200, clusterCoord[0] + 200)
            y = random.randint(clusterCoord[1] - 200, clusterCoord[1] + 200)
            Enemy((x, y))


def drawBg(worldSpeed, worldAngle, bgReference):
    x_shift = worldSpeed * cos(worldAngle)
    y_shift = worldSpeed * sin(worldAngle)
    bgReference[0] += x_shift * 0.25
    bgReference[1] += y_shift * 0.25
    if abs(bgReference[0]) > BG_TILE.get_width():
        bgReference[0] = 0
    if abs(bgReference[1]) > BG_TILE.get_height():
        bgReference[1] = 0
    for x in range(-3, 4):
        for y in range(-3, 4):
            WIN.blit(
                BG_TILE,
                (
                    bgReference[0] + (x * bg_width) + x_shift,
                    bgReference[1] + (y * bg_height) + y_shift,
                ),
            )


def writeInstructions(instructionsSurface):
    text = [
        "YOU'RE LOST IN SPACE IN YOUR AI-NAVIGATED SHIP DEEP IN ALIEN TERRITORY!",
        "YOU NEED TO ESCAPE TO THE EXIT PORTAL BUT YOUR SHIP HAS LIMITED POWER BETWEEN",
        "        WEAPONS AND NAVIGATION...",
        "",
        "USE ARROW KEYS TO MOVE YOUR GUN AND SPACEBAR TO FIRE.",
        "USE 'W' AND 'S' TO SELECT MODULES AND 'A' AND 'D' TO SHIFT POWER BETWEEN THEM.",
        "EVERY 2 SECONDS, THE AI WILL CALCULATE A ROUTE AND THE POWER WILL REDISTRIBUTE",
        "        ACCORDING TO WHAT YOU HAVE SET. BE WARNED, THE MORE POWER YOU TAKE FROM",
        "        NAVIGATION, THE STUPIDER THE AI WILL GET.",
        "MORE GUN DAMAGE = GUN DOES MORE DAMAGE              MORE NAV DIRECTION = BETTER NAVIGATION",
        "MORE GUN ROTATION = GUN MOVES FASTER    MORE NAV SPEED = STABLER SPEED (NOT ALWAYS FASTER)",
    ]

    lineSpacing = 70
    for i in range(len(text)):
        t = text[i]
        instructionsSurface.blit(
            INSTR_FONT.render(t, 1, (255, 255, 255)), (20, 10 + (lineSpacing * i))
        )
    return


def writeCredits(winSurface):
    winText = "CONGRATULATIONS, YOU MADE IT TO THE PORTAL AND ESCAPED!"

    text = [
        "CODE, ART, CONCEPT",
        "PENGUINMANEREIKEL",
        "",
        "MUSIC",
        "'LIGHTLESS DAWN' BY KEVIN MCLEOD",
        "(INCOMPOTECH.COM)",
        "",
        "SFX",
        "colorsCrimsonTears   timgormly",
        "michael_grinnell   Wolfsinger",
        "giddster   Jerimee",
        "Alderman2k   jalastram",
        "(freesound.org)",
        "",
        "Made for",
    ]

    winS = INSTR_FONT.render(winText, 1, (255, 255, 255))
    winSurface.blit(winS, ((winSurface.get_width() - winS.get_width()) // 2, 10))

    titleS = INSTR_FONT.render("CREDITS", 1, (255, 255, 255))
    winSurface.blit(titleS, ((winSurface.get_width() - titleS.get_width()) // 2, 100))

    lineSpacing = 20
    for i in range(len(text)):
        t = text[i]
        s = CRED_FONT.render(t, 1, (255, 255, 255))
        winSurface.blit(
            s, ((winSurface.get_width() - s.get_width()) // 2, 140 + (lineSpacing * i))
        )

    winSurface.blit(
        WOWIE_LOGO_2,
        (
            (winSurface.get_width() - WOWIE_LOGO_2.get_width()) // 2,
            140 + (lineSpacing * len(text)),
        ),
    )


def writeGameOver(gameOverSurface, dest):
    distance = round(
        sqrt((dest[0] - (WIN_WIDTH // 2)) ** 2 + (dest[1] - (WIN_HEIGHT // 2)))
    )

    text = [
        "GAME OVER",
        "YOU WERE " + str(int(distance // 10)) + " METERS FROM THE PORTAL",
        "PRESS 'R' TO RESTART",
    ]
    lineSpacing = 50
    for i in range(len(text)):
        t = text[i]
        s = INSTR_FONT.render(t, 1, (255, 255, 255))
        gameOverSurface.blit(
            s,
            (
                (gameOverSurface.get_width() - s.get_width()) // 2,
                10 + (lineSpacing * i),
            ),
        )


async def main():
    running = True
    game_screen = pg.Surface((WIN_WIDTH, WIN_HEIGHT))
    instructions = pg.Surface((WIN_WIDTH, WIN_HEIGHT))
    instructions.fill(SPACE_BLUE)
    writeInstructions(instructions)
    winScreen = pg.Surface((1000, 500))
    gameOverSurface = pg.Surface((800, 150))
    gameOverSurface.fill((0, 0, 0))

    playerShip = PlayerShip()
    goalSide = random.randint(1, 4)
    goalCoordRegions = {
        1: (-14000, -13000, -14000, -13000),
        2: (-14000, -13000, 13000, 14000),
        3: (13000, 14000, 13000, 14000),
        4: (13000, 14000, -14000, -13000),
    }  # (x_start,x_end,y_start,y_end)
    goalCoords = (
        random.randint(goalCoordRegions[goalSide][0], goalCoordRegions[goalSide][0]),
        random.randint(goalCoordRegions[goalSide][1], goalCoordRegions[goalSide][1]),
    )
    # goalCoords = (140,130)
    levelGoal = Goal(goalCoords)
    # levelGoal = Goal((14000,14000))
    explosion = pg.transform.scale(
        load_image("explosion_2.png").convert_alpha(), (90, 90)
    )
    arrow = Arrow(levelGoal)
    # Enemy((1500,750))
    COUNTDOWN_LIMIT = 2 * FPS
    countdown = COUNTDOWN_LIMIT
    selected = "angle"
    ui = UI()
    # testBullet = Bullet(2,(800,300),0)
    anglePowerTemp = playerShip.anglePower
    speedPowerTemp = playerShip.speedPower
    bgReference = [0, 0]
    spawnEnemies(generateEnemyClusters(levelGoal.pos))

    killCount = 0
    time = 0

    state = "TITLE"

    while running:
        clock.tick(FPS)
        WIN.fill(SPACE_BLUE)

        for e in pg.event.get():
            if e.type == QUIT:
                running = False
                pg.quit()
                sys.exit()

            if state == "TITLE":
                if e.type == KEYDOWN:
                    if e.key == K_SPACE or e.key == K_RETURN:
                        state = "INSTR"

            elif state == "INSTR":
                if e.type == KEYDOWN:
                    if e.key == K_SPACE or e.key == K_RETURN:
                        state = "GAME"

            elif state == "GAME":
                if e.type == KEYDOWN:
                    if e.key == K_RIGHT:
                        playerShip.setGunDir(-1)
                    if e.key == K_LEFT:
                        playerShip.setGunDir(1)
                    if e.key == K_s:
                        selected = "speed"
                        CLACK_SOUND.play()
                        ui.selectOption(2)
                    if e.key == K_w:
                        selected = "angle"
                        CLACK_SOUND.play()
                        ui.selectOption(1)

                    if e.key == K_a:
                        CLICK_SOUND.play()
                        if selected == "speed" and speedPowerTemp > 0:
                            speedPowerTemp -= 1
                        if selected == "angle" and anglePowerTemp > 0:
                            anglePowerTemp -= 1
                    if e.key == K_d:
                        CLICK_SOUND.play()
                        if selected == "speed" and speedPowerTemp < 3:
                            speedPowerTemp += 1
                        if selected == "angle" and anglePowerTemp < 3:
                            anglePowerTemp += 1

                    if e.key == K_SPACE:
                        playerShip.fireGun()

                if e.type == KEYUP:
                    if e.key == K_RIGHT and playerShip.gun.direction == -1:
                        playerShip.setGunDir(0)
                    if e.key == K_LEFT and playerShip.gun.direction == 1:
                        playerShip.setGunDir(0)

                if e.type == LOSE_EVENT:
                    state = "LOSE"
                    print("lose")
                    writeGameOver(gameOverSurface, levelGoal.pos)
                    playerShip.gun.kill()
                    playerShip.kill()
                    arrow.kill()
                    BOOM_SOUND.play()
                    # explosion.render(WIN,(playerShip.pos[0] - (playerShip.image.get_width()//2),playerShip.pos[1] - (playerShip.image.get_height()//2)))

                if e.type == WIN_EVENT:
                    state = "WIN"
                    writeCredits(winScreen)
                    WIN_SOUND.play()
                    MOVE_SOUND.stop()
                    playerShip.gun.kill()
                    playerShip.kill()

            elif state == "LOSE":
                if e.type == KEYDOWN:
                    if e.key == K_r:
                        for obj in allGroup:
                            obj.kill()
                        return True

            elif state == "WIN":
                if e.type == KEYDOWN:
                    if e.key == K_r:
                        for obj in allGroup:
                            obj.kill()
                        return True

        if state == "GAME":
            countdown -= 1
        if countdown == 0:
            playerShip.changeAnglePower(anglePowerTemp)
            playerShip.changeSpeedPower(speedPowerTemp)
            playerShip.changeAngle(levelGoal.pos)
            playerShip.changeSpeed()
            countdown = COUNTDOWN_LIMIT

        if state == "GAME":
            speed, angle = playerShip.getSpeedAndAngle()
        else:
            speed = 0
            angle = 0
        drawBg(speed, angle, bgReference)

        if state == "LOSE" or state == "WIN":
            speed = 0
        else:
            enemyGroup.update(speed=speed, angle=angle, target=playerShip.pos)

        objectGroup.update(speed=speed, angle=angle)
        angleRefToPlayerGroup.update()
        for elem in allGroup:
            pass
            # print(type(elem))
        for bullet in bulletGroup:
            if bullet.life <= 0:
                bullet.kill()
        ui.overlaySurface.fill(0)
        if anglePowerTemp <= 0:
            pg.draw.rect(ui.overlaySurface, (155, 0, 0), Rect(43, 123, 22, 13))
        if anglePowerTemp <= 1:
            pg.draw.rect(ui.overlaySurface, (155, 0, 0), Rect(86, 123, 22, 13))
        if anglePowerTemp <= 2:
            pg.draw.rect(ui.overlaySurface, (155, 0, 0), Rect(129, 123, 22, 13))
        if anglePowerTemp >= 1:
            pg.draw.rect(ui.overlaySurface, (155, 0, 0), Rect(343, 123, 22, 13))
        if anglePowerTemp >= 2:
            pg.draw.rect(ui.overlaySurface, (155, 0, 0), Rect(386, 123, 22, 13))
        if anglePowerTemp >= 3:
            pg.draw.rect(ui.overlaySurface, (155, 0, 0), Rect(429, 123, 22, 13))

        if speedPowerTemp <= 0:
            pg.draw.rect(ui.overlaySurface, (155, 155, 0), Rect(43, 158, 22, 13))
        if speedPowerTemp <= 1:
            pg.draw.rect(ui.overlaySurface, (155, 155, 0), Rect(86, 158, 22, 13))
        if speedPowerTemp <= 2:
            pg.draw.rect(ui.overlaySurface, (155, 155, 0), Rect(129, 158, 22, 13))
        if speedPowerTemp >= 1:
            pg.draw.rect(ui.overlaySurface, (155, 155, 0), Rect(343, 158, 22, 13))
        if speedPowerTemp >= 2:
            pg.draw.rect(ui.overlaySurface, (155, 155, 0), Rect(386, 158, 22, 13))
        if speedPowerTemp >= 3:
            pg.draw.rect(ui.overlaySurface, (155, 155, 0), Rect(429, 158, 22, 13))

        if playerShip.anglePower <= 0:
            pg.draw.rect(ui.overlaySurface, (255, 0, 0), Rect(43, 123, 22, 13))
        if playerShip.anglePower <= 1:
            pg.draw.rect(ui.overlaySurface, (255, 0, 0), Rect(86, 123, 22, 13))
        if playerShip.anglePower <= 2:
            pg.draw.rect(ui.overlaySurface, (255, 0, 0), Rect(129, 123, 22, 13))
        if playerShip.anglePower >= 1:
            pg.draw.rect(ui.overlaySurface, (255, 0, 0), Rect(343, 123, 22, 13))
        if playerShip.anglePower >= 2:
            pg.draw.rect(ui.overlaySurface, (255, 0, 0), Rect(386, 123, 22, 13))
        if playerShip.anglePower >= 3:
            pg.draw.rect(ui.overlaySurface, (255, 0, 0), Rect(429, 123, 22, 13))

        if playerShip.speedPower <= 0:
            pg.draw.rect(ui.overlaySurface, (255, 255, 0), Rect(43, 158, 22, 13))
        if playerShip.speedPower <= 1:
            pg.draw.rect(ui.overlaySurface, (255, 255, 0), Rect(86, 158, 22, 13))
        if playerShip.speedPower <= 2:
            pg.draw.rect(ui.overlaySurface, (255, 255, 0), Rect(129, 158, 22, 13))
        if playerShip.speedPower >= 1:
            pg.draw.rect(ui.overlaySurface, (255, 255, 0), Rect(343, 158, 22, 13))
        if playerShip.speedPower >= 2:
            pg.draw.rect(ui.overlaySurface, (255, 255, 0), Rect(386, 158, 22, 13))
        if playerShip.speedPower >= 3:
            pg.draw.rect(ui.overlaySurface, (255, 255, 0), Rect(429, 158, 22, 13))

        heart_offset = 50
        for i in range(playerShip.health // 2):
            ui.overlaySurface.blit(HEART_ICON, (133 + heart_offset * i, 188))
        if playerShip.health % 2 and playerShip.health > 0:
            ui.overlaySurface.blit(
                HEART_ICON_2, (133 + (heart_offset * (playerShip.health // 2)), 188)
            )
        pg.draw.rect(
            ui.overlaySurface,
            (0, 0, 255),
            Rect(
                35 + ((COUNTDOWN_LIMIT - countdown) / COUNTDOWN_LIMIT) * 212,
                73,
                425 - ((COUNTDOWN_LIMIT - countdown) / COUNTDOWN_LIMIT) * 425,
                16,
            ),
        )

        if state == "GAME":
            allGroup.draw(WIN)
        for enemy, bullets in pg.sprite.groupcollide(
            enemyGroup, bulletGroup, False, True
        ).items():
            for bullet in bullets:
                killCount += enemy.lowerHealth(bullet.damage)

        if len(pg.sprite.spritecollide(playerShip, enemyGroup, False)):
            playerShip.getHurt()
        playerGroup.update()
        if state == "GAME":
            UIGroup.draw(WIN)

        if pg.sprite.collide_rect(levelGoal, playerShip):
            pg.event.post(pg.event.Event(WIN_EVENT))

        if state == "LOSE":
            WIN.blit(
                explosion,
                (
                    WIN_WIDTH // 2 - (playerShip.image.get_width()) // 2,
                    WIN_HEIGHT // 2 - (playerShip.image.get_height()) // 2,
                ),
            )
            WIN.blit(
                gameOverSurface,
                (
                    (
                        WIN_WIDTH // 2 - (gameOverSurface.get_width()) // 2,
                        WIN_HEIGHT // 2 - ((gameOverSurface.get_height()) // 2) - 300,
                    )
                ),
            )
        if state == "GAME":
            WIN.blit(ui.overlaySurface, (ui.rect.topleft))
        if state == "INSTR":
            WIN.blit(instructions, (0, 0))
        if state == "WIN":
            WIN.blit(
                winScreen,
                (
                    (WIN_WIDTH - winScreen.get_width()) // 2,
                    (WIN_HEIGHT - winScreen.get_height()) // 2,
                ),
            )
        if state == "TITLE":
            WIN.blit(LOGO_P1, ((WIN_WIDTH - LOGO_P1.get_width()) // 2, 40))
            WIN.blit(
                LOGO_P2,
                (
                    (WIN_WIDTH - LOGO_P2.get_width()) // 2,
                    WIN_HEIGHT - LOGO_P2.get_height() - 40,
                ),
            )
            WIN.blit(
                LOGO_P3,
                ((WIN_WIDTH - LOGO_P3.get_width()) // 2, (WIN_HEIGHT // 2) + 50),
            )
            WIN.blit(
                WOWIE_LOGO_1,
                (
                    WIN_WIDTH - WOWIE_LOGO_1.get_width(),
                    WIN_HEIGHT - WOWIE_LOGO_1.get_height(),
                ),
            )
            playerGroup.draw(WIN)
        pg.display.update()
        await asyncio.sleep(0)


asyncio.run(main())
