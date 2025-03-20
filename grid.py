import pygame
from math import *
import pickle
import pygame.sysfont
from vector import *


# Everything here is for DDA and level building (levelEditor.py)

# Block numbers mapped to blocks
COLORS = {
    1: [(220, 0, 0), (110, 0, 0)],
    2: [(0, 220, 0), (0, 110, 0)],
    3: [(0, 0, 220), (0, 0, 110)],
    4: [(220, 220, 0), (110, 110, 0)],
    5: [(0, 220, 220), (0, 110, 110)],
    6: [(220, 0, 220), (110, 0, 110)],
}

# generic white block texture
BLOCKTEXTURE = pygame.image.load("res/block/genericblock2.png")


# Tints an image a certain color. Better than havng multiple block files.
def tintImage(image: pygame.Surface, color: pygame.Color):
    tintedImage = image.copy()  # Copies the image surface
    tintedImage.convert_alpha()  #
    tintedImage.fill(color, special_flags=pygame.BLEND_RGBA_MULT)

    return tintedImage


def displayMiniMap(screen: pygame.Surface, grid, area: pygame.Rect, posV: Vector2F):
    surface = pygame.Surface((area.w, area.h), flags=pygame.SRCALPHA)
    WIDTHSIZE = area.width / len(grid[0])
    HEIGHTSIZE = area.height / len(grid[0])
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            block = grid[row][col]
            if block == 0:
                pygame.draw.rect(surface, (255, 255, 255, 100), (col * WIDTHSIZE, row * HEIGHTSIZE, WIDTHSIZE, HEIGHTSIZE))
            else:
                pygame.draw.rect(surface, (*COLORS[block][0], 150), (col * WIDTHSIZE, row * HEIGHTSIZE, WIDTHSIZE, HEIGHTSIZE))

    pygame.draw.circle(surface, (200, 0, 0), vectorMultiply(posV, Vector2F(WIDTHSIZE, HEIGHTSIZE)).toTuple(), WIDTHSIZE / 3)
    screen.blit(surface, (area.x, area.y))


class Grid:
    CURRENTID = 0
    gridDict = {}

    def __init__(self, rows, cols, tilesize):
        self.id = self.CURRENTID

        self.neighbors = {"up": None, "down": None, "left": None, "right": None}

        self.rows = rows
        self.cols = cols
        self.tilesize = tilesize
        self.grid = [[0] * self.cols]
        for r in range(self.rows):
            self.grid.append([0] * self.cols)

        self.gridDict[self.id] = self
        self.portals = {
            "upPortal": Vector2I(self.cols // 2, 0),
            "downPortal": Vector2I(self.cols // 2, self.rows - 1),
            "leftPortal": Vector2I(0, self.rows // 2),
            "rightPortal": Vector2I(self.cols - 1, self.rows // 2),
        }

    def plotPoint(self, row: int, col: int, tile: int):
        if (col, row) == self.portals["upPortal"].toTuple() and self.neighbors["up"] != None:
            return False
        if (col, row) == self.portals["downPortal"].toTuple() and self.neighbors["down"] != None:
            return False
        if (col, row) == self.portals["leftPortal"].toTuple() and self.neighbors["left"] != None:
            return False
        if (col, row) == self.portals["rightPortal"].toTuple() and self.neighbors["right"] != None:
            return False
        elif self.grid[row][col] != tile:
            self.grid[row][col] = tile
            return True

    def loadLevel(self, path: str):
        self.grid = pickle.load(open("levels/level.sob", "rb"))
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])

    def castRays(self, screen: pygame.Surface, posV: Vector2F, dirV: Vector2F, planeV: Vector2F, alpha: bool):
        # Technique derived from Lodevs DDA raycasting demonstration: https://lodev.org/cgtutor/raycasting.html
        width = screen.get_width()
        height = screen.get_height()

        blitTargets = []
        for x in range(width):
            cameraX = ((2 * x) / float(width)) - 1
            rayDir = Vector2F(dirV.x + planeV.x * cameraX, dirV.y + planeV.y * cameraX)
            mapPos = Vector2I(posV.x, posV.y)

            sideDist = Vector2F()
            deltaDist = Vector2F()

            if rayDir.x != 0:
                deltaDist.x = sqrt(1 + ((rayDir.y + 1e-20) ** 2) / ((rayDir.x + 1e-20) ** 2))
                # deltaDist.x = abs(1 + (rayDir.x))
            else:
                deltaDist.x = float("inf")
            if rayDir.y != 0:
                deltaDist.y = sqrt(1 + ((rayDir.x + 1e-20) ** 2) / ((rayDir.y + 1e-20) ** 2))
                # deltaDist.x = abs(1 + (rayDir.y))
            else:
                deltaDist.y = float("inf")

            perpWallDist = 0

            stepV = Vector2I()

            hit = False
            side = 0
            if rayDir.x < 0:
                stepV.x = -1
                sideDist.x = (posV.x - mapPos.x) * deltaDist.x
            else:
                stepV.x = 1
                sideDist.x = (mapPos.x + 1.0 - posV.x) * deltaDist.x
            if rayDir.y < 0:
                stepV.y = -1
                sideDist.y = (posV.y - mapPos.y) * deltaDist.y
            else:
                stepV.y = 1
                sideDist.y = (mapPos.y + 1.0 - posV.y) * deltaDist.y

            curGrid = self
            gridDistance = Vector2I().fromVector2I(mapPos)
            while not hit:
                if sideDist.x < sideDist.y:
                    sideDist.x += deltaDist.x
                    gridDistance.x += stepV.x
                    mapPos.x += stepV.x
                    side = 0
                else:
                    sideDist.y += deltaDist.y
                    gridDistance.y += stepV.y
                    mapPos.y += stepV.y
                    side = 1

                if mapPos.x < 0:
                    if curGrid.neighbors["left"] != None:
                        curGrid = Grid.gridDict[curGrid.neighbors["left"]]
                        mapPos.x = self.cols - 1
                    else:
                        break
                elif mapPos.x >= self.cols:
                    if curGrid.neighbors["right"] != None:
                        curGrid = Grid.gridDict[curGrid.neighbors["right"]]
                        mapPos.x = 0
                    else:
                        break
                elif mapPos.y < 0:
                    if curGrid.neighbors["up"] != None:
                        curGrid = Grid.gridDict[curGrid.neighbors["up"]]
                        mapPos.y = self.rows - 1
                    else:
                        break
                elif mapPos.y >= self.rows:
                    if curGrid.neighbors["down"] != None:
                        curGrid = Grid.gridDict[curGrid.neighbors["down"]]
                        mapPos.y = 0
                    else:
                        break
                if curGrid.grid[int(floor(mapPos.y))][int(floor(mapPos.x))] != 0:  # Switch x and y if needed
                    hit = True
                    block = curGrid.grid[int(floor(mapPos.y))][int(floor(mapPos.x))]

            if side == 0:
                perpWallDist = abs((gridDistance.x - posV.x + (1.0 - stepV.x) / 2.0) / rayDir.x)
                wallX = posV.y + perpWallDist * rayDir.y
            else:
                perpWallDist = abs((gridDistance.y - posV.y + (1.0 - stepV.y) / 2.0) / rayDir.y)
                wallX = posV.x + perpWallDist * rayDir.x

            lineHeight = abs(int(height / (perpWallDist + 1e-10)))

            drawStart = max(0, (-lineHeight / 2) + (height / 2))
            drawEnd = min(height - 1, (lineHeight / 2) + (height / 2))

            if not hit:
                pygame.draw.line(screen, (0, 0, 0, 100), (x, drawStart), (x, drawEnd), 1)
            else:
                texWidth = BLOCKTEXTURE.get_width()
                texHeight = BLOCKTEXTURE.get_height()
                wallX -= floor(wallX)
                texX = int(wallX * float(texWidth))
                if side == 0 and rayDir.x > 0:
                    texX = texWidth - texX - 1
                if side == 1 and rayDir.x < 0:
                    texX = texWidth - texX - 1
                texYStart = int((drawStart - height / 2 + lineHeight / 2) * (texHeight / lineHeight))
                texYStart = max(0, min(texYStart, texHeight - 1))
                texYEnd = int((drawEnd - height / 2 + lineHeight / 2) * (texHeight / lineHeight))
                texYEnd = max(0, min(texYEnd, texHeight - 1))
                textureStrip = pygame.transform.scale(
                    BLOCKTEXTURE.subsurface((texX, texYStart, 1, texYEnd - texYStart)), (1, drawEnd - drawStart)
                )

                if alpha == True:
                    textureStrip.set_alpha(100)
                if side == 0:
                    blitTargets.append((tintImage(textureStrip, COLORS[block][0]), (x, drawStart)))
                else:
                    blitTargets.append((tintImage(textureStrip, COLORS[block][1]), (x, drawStart)))
        screen.blits(blitTargets)

    def castMelee(self, screenWidth: int, posV: Vector2F, dirV: Vector2F, planeV: Vector2F, blockRange: float):
        # Literally same as raytracing but we cast one ray
        x = screenWidth / 2
        cameraX = ((2 * x) / float(screenWidth)) - 1
        rayDir = Vector2F(dirV.x + planeV.x * cameraX, dirV.y + planeV.y * cameraX)
        mapPos = Vector2I(posV.x, posV.y)

        sideDist = Vector2F()
        deltaDist = Vector2F()

        if rayDir.x != 0:
            deltaDist.x = sqrt(1 + ((rayDir.y + 1e-20) ** 2) / ((rayDir.x + 1e-20) ** 2))
            # deltaDist.x = abs(1 + (rayDir.x))
        else:
            deltaDist.x = float("inf")
        if rayDir.y != 0:
            deltaDist.y = sqrt(1 + ((rayDir.x + 1e-20) ** 2) / ((rayDir.y + 1e-20) ** 2))
            # deltaDist.x = abs(1 + (rayDir.y))
        else:
            deltaDist.y = float("inf")

        perpWallDist = 0

        stepV = Vector2I()

        hit = False
        side = 0
        if rayDir.x < 0:
            stepV.x = -1
            sideDist.x = (posV.x - mapPos.x) * deltaDist.x
        else:
            stepV.x = 1
            sideDist.x = (mapPos.x + 1.0 - posV.x) * deltaDist.x
        if rayDir.y < 0:
            stepV.y = -1
            sideDist.y = (posV.y - mapPos.y) * deltaDist.y
        else:
            stepV.y = 1
            sideDist.y = (mapPos.y + 1.0 - posV.y) * deltaDist.y

        curGrid = self
        gridDistance = Vector2I().fromVector2I(mapPos)
        curDist = 0
        while not hit and curDist < blockRange:
            if sideDist.x < sideDist.y:
                sideDist.x += deltaDist.x
                curDist = sideDist.x
                gridDistance.x += stepV.x
                mapPos.x += stepV.x
                side = 0
            else:
                sideDist.y += deltaDist.y
                curDist = sideDist.y
                gridDistance.y += stepV.y
                mapPos.y += stepV.y
                side = 1

            if mapPos.x < 0:
                if curGrid.neighbors["left"] != None:
                    curGrid = Grid.gridDict[curGrid.neighbors["left"]]
                    mapPos.x = self.cols - 1
                else:
                    break
            elif mapPos.x >= self.cols:
                if curGrid.neighbors["right"] != None:
                    curGrid = Grid.gridDict[curGrid.neighbors["right"]]
                    mapPos.x = 0
                else:
                    break
            elif mapPos.y < 0:
                if curGrid.neighbors["up"] != None:
                    curGrid = Grid.gridDict[curGrid.neighbors["up"]]
                    mapPos.y = self.rows - 1
                else:
                    break
            elif mapPos.y >= self.rows:
                if curGrid.neighbors["down"] != None:
                    curGrid = Grid.gridDict[curGrid.neighbors["down"]]
                    mapPos.y = 0
                else:
                    break
            if curGrid.grid[int(floor(mapPos.y))][int(floor(mapPos.x))] != 0:  # Switch x and y if needed
                hit = True
                curGrid.grid[int(floor(mapPos.y))][int(floor(mapPos.x))] = 0

    def draw(self, screen):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col] != 0:
                    pygame.draw.rect(
                        screen,
                        COLORS[self.grid[row][col]][0],
                        (col * self.tilesize, row * self.tilesize, self.tilesize, self.tilesize),
                    )
                pygame.draw.line(screen, "grey", (col * self.tilesize, 0), (col * self.tilesize, self.rows * self.tilesize))
            pygame.draw.line(screen, "grey", (0, row * self.tilesize), (self.cols * self.tilesize, row * self.tilesize))



