import pygame
import pickle
import asyncio
from vector import *
from math import *

# import spritesheetManager as SSM


TILESIZE = 32
WIDTH = 640
HEIGHT = 640
RESOLUTION = 3.5
fullScreen = False

pygame.init()
pygame.font.init()
defaultFont = pygame.font.SysFont("Verdana", 24, True)
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags=pygame.HWACCEL)
clock = pygame.time.Clock()

from grid import Grid, displayMiniMap


Grid.gridDict = pickle.load(open("levels/level.sob", "rb"))
grid = Grid.gridDict[0]


def floatToVector(v: tuple):
    return (WIDTH * v[0], HEIGHT * v[1])


playerV = Vector2F(1, 1)
dirV = Vector2F(-1.0, 0.0)
planeV = Vector2F(0, -0.66)
bullets = []

rotSpeed = 0.1
moveSpeed = 0.05


INVRAD = (cos(-rotSpeed), sin(-rotSpeed))
RAD = (cos(rotSpeed), sin(rotSpeed))

skyBox = pygame.transform.smoothscale(pygame.image.load("res/skybox.jpg"), (WIDTH, HEIGHT))
# model = SSM.SpriteManager(pygame.image.load("res/blobSpritesheet.png"), 32, 32, 500)

targetFPS = 60
currentScreen = pygame.Surface((WIDTH / RESOLUTION, HEIGHT / RESOLUTION), flags=pygame.SRCALPHA | pygame.HWACCEL)
seeThroughWalls = False
highRes = False
miniMap = True
running = True
grid.castRays(currentScreen, playerV, dirV, planeV, seeThroughWalls)
prevTime = moveSpeed * pygame.time.get_ticks()


def checkRoom():
    global grid
    global playerV
    if playerV.y < 0 or playerV.x < 0 or playerV.y >= grid.rows or playerV.x >= grid.cols:
        if playerV.x < 0:
            if grid.neighbors["left"] != None:
                grid = Grid.gridDict[grid.neighbors["left"]]
                playerV.x += grid.cols
        elif playerV.y < 0:
            if grid.neighbors["up"] != None:
                grid = Grid.gridDict[grid.neighbors["up"]]
                playerV.y += grid.rows
        elif playerV.x > grid.cols - 1:
            if grid.neighbors["right"] != None:
                grid = Grid.gridDict[grid.neighbors["right"]]
                playerV.x -= grid.cols
        elif playerV.y > grid.rows - 1:
            if grid.neighbors["down"] != None:
                grid = Grid.gridDict[grid.neighbors["down"]]
                playerV.y -= grid.rows


print("Ready to run")


async def run():
    global running, currentScreen, miniMap, targetFPS, seeThroughWalls, highRes, miniMap, prevTime
    while running:
        mousePos = Vector2F(*pygame.mouse.get_pos())
        moved = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.display.toggle_fullscreen()
                if event.key == pygame.K_z:
                    seeThroughWalls = not seeThroughWalls
                if event.key == pygame.K_r:
                    if highRes:
                        currentScreen = pygame.Surface(
                            (WIDTH / RESOLUTION, HEIGHT / RESOLUTION), flags=pygame.SRCALPHA | pygame.HWACCEL
                        )
                        targetFPS = 60
                    else:
                        currentScreen = pygame.Surface((WIDTH, HEIGHT), flags=pygame.SRCALPHA | pygame.HWACCEL)
                        targetFPS = 30

                    grid.castRays(currentScreen, playerV, dirV, planeV, seeThroughWalls)
                    highRes = not highRes
                if event.key == pygame.K_m:
                    miniMap = not miniMap
                if event.key == pygame.K_SPACE:
                    grid.castMelee(currentScreen.get_width(), playerV, dirV, planeV, 2.5)
                    currentScreen.fill((0, 0, 0, 0))
                    grid.castRays(currentScreen, playerV, dirV, planeV, seeThroughWalls)

        key = pygame.key.get_pressed()
        if key[pygame.K_RIGHT]:
            oldX = dirV.x
            dirV.x = dirV.x * RAD[0] - dirV.y * RAD[1]
            dirV.y = oldX * RAD[1] + dirV.y * RAD[0]

            oldPlaneX = planeV.x
            planeV.x = planeV.x * RAD[0] - planeV.y * RAD[1]
            planeV.y = oldPlaneX * RAD[1] + planeV.y * RAD[0]
            moved = True
        elif key[pygame.K_LEFT]:
            oldX = dirV.x
            dirV.x = dirV.x * INVRAD[0] - dirV.y * INVRAD[1]
            dirV.y = oldX * INVRAD[1] + dirV.y * INVRAD[0]

            oldPlaneX = planeV.x
            planeV.x = planeV.x * INVRAD[0] - planeV.y * INVRAD[1]
            planeV.y = oldPlaneX * INVRAD[1] + planeV.y * INVRAD[0]
            moved = True

        if key[pygame.K_UP]:
            playerV.x += dirV.x * moveSpeed
            checkRoom()
            if grid.grid[int(playerV.y)][int(playerV.x)] != 0:
                playerV.x -= dirV.x * moveSpeed
            playerV.y += dirV.y * moveSpeed
            checkRoom()
            if grid.grid[int(playerV.y)][int(playerV.x)] != 0:
                playerV.y -= dirV.y * moveSpeed
            moved = True
        if key[pygame.K_DOWN]:
            playerV.x -= dirV.x * moveSpeed
            checkRoom()
            if grid.grid[int(playerV.y)][int(playerV.x)] != 0:
                playerV.x += dirV.x * moveSpeed
            playerV.y -= dirV.y * moveSpeed
            checkRoom()
            if grid.grid[int(playerV.y)][int(playerV.x)] != 0:
                playerV.y += dirV.y * moveSpeed
            moved = True

        if moved:
            currentScreen.fill((0, 0, 0, 0))
            grid.castRays(currentScreen, playerV, dirV, planeV, seeThroughWalls)

        screen.blit(skyBox, (0, 0))
        screen.fill("grey", (0, HEIGHT / 2, WIDTH, HEIGHT / 2))

        screen.blit(pygame.transform.scale(currentScreen, (WIDTH, HEIGHT)), (0, 0))

        screen.blit(defaultFont.render(str(round(clock.get_fps(), 2)), True, "red"), (0, 0))
        pygame.draw.circle(screen, (0, 255, 0), (WIDTH / 2, HEIGHT / 2), 5)
        if miniMap:
            displayMiniMap(screen, grid.grid, pygame.Rect(0, HEIGHT - 100, 100, 100), playerV)

        pygame.display.flip()

        clock.tick(targetFPS)
        # await asyncio.sleep(0)

    pygame.quit()


asyncio.run(run())
