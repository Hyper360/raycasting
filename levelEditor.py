import pygame
import pickle
import argparse


def main():
    pygame.init()

    parser = argparse.ArgumentParser()

    parser.add_argument("dimensions", type=int, help="Number of rows/columns", default=20)
    args = parser.parse_args()

    from grid import Grid

    ROWS = args.dimensions
    COLS = args.dimensions
    WIDTH = 640
    HEIGHT = 640
    TILESIZE = WIDTH / ROWS
    grid = Grid(ROWS, COLS, TILESIZE)
    gridIndex = "A"

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    tile = 1
    running = True
    while running:
        mousePos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    pickle.dump(Grid.gridDict, open("levels/level.sob", "wb"))
                if event.key == pygame.K_l:
                    Grid.gridDict = pickle.load(open("levels/level.sob", "rb"))
                    grid = Grid.gridDict[0]
                if event.key == pygame.K_c:
                    grid = Grid(ROWS, COLS, TILESIZE)
                if event.key == pygame.K_RIGHT:
                    if grid.neighbors["right"] == None:
                        Grid.CURRENTID += 1
                        tempGrid = Grid(ROWS, COLS, TILESIZE)
                        tempGrid.neighbors["left"] = grid.id
                        grid.neighbors["right"] = tempGrid.id
                        grid.grid[grid.rows // 2][grid.cols - 1] = 0

                    grid = Grid.gridDict[grid.neighbors["right"]]

                if event.key == pygame.K_LEFT:
                    if grid.neighbors["left"] == None:
                        Grid.CURRENTID += 1
                        tempGrid = Grid(ROWS, COLS, TILESIZE)
                        tempGrid.neighbors["right"] = grid.id
                        grid.neighbors["left"] = tempGrid.id
                        grid.grid[grid.rows // 2][0] = 0

                    grid = Grid.gridDict[grid.neighbors["left"]]

                if event.key == pygame.K_UP:
                    if grid.neighbors["up"] == None:
                        Grid.CURRENTID += 1
                        tempGrid = Grid(ROWS, COLS, TILESIZE)
                        tempGrid.neighbors["down"] = grid.id
                        grid.neighbors["up"] = tempGrid.id
                        grid.grid[0][grid.cols // 2] = 0

                    grid = Grid.gridDict[grid.neighbors["up"]]

                if event.key == pygame.K_DOWN:
                    if grid.neighbors["down"] == None:
                        Grid.CURRENTID += 1
                        tempGrid = Grid(ROWS, COLS, TILESIZE)
                        tempGrid.neighbors["up"] = grid.id
                        grid.neighbors["down"] = tempGrid.id
                        grid.grid[grid.rows - 1][grid.cols // 2] = 0

                    grid = Grid.gridDict[grid.neighbors["down"]]

                if event.key == pygame.K_1:
                    tile = 1
                if event.key == pygame.K_2:
                    tile = 2
                if event.key == pygame.K_3:
                    tile = 3
                if event.key == pygame.K_4:
                    tile = 4
                if event.key == pygame.K_5:
                    tile = 5
                if event.key == pygame.K_6:
                    tile = 6

        mousePressed = pygame.mouse.get_pressed()
        if mousePressed[0]:
            mouseCol = int(mousePos[0] / TILESIZE)
            mouseRow = int(mousePos[1] / TILESIZE)
            grid.plotPoint(mouseRow, mouseCol, tile)
        if mousePressed[2]:
            mouseCol = int(mousePos[0] / TILESIZE)
            mouseRow = int(mousePos[1] / TILESIZE)
            grid.plotPoint(mouseRow, mouseCol, 0)
        screen.fill("black")

        grid.draw(screen)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
