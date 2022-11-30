import random

import pygame
from GameMap import GameMap
import os
import re


def gameLoop(map: str):
    """
    一局的游戏循环函数，负责进行游戏的碰撞检测、绘图、事件处理等。

    :param map: 游戏地图的路径
    """
    fpsClock = pygame.time.Clock()
    pygame.display.set_caption("坦克大战 - {}".format(os.path.splitext(map)[0]))
    m = GameMap(map)
    screen = pygame.display.set_mode((m.width, m.height), 0, 32)
    for j in m.realMap:
        for i in j:
            if i:
                i.setGameMap(m)
    myTank = m.groups["FriendlyTank"].sprites()[0]
    index = 0
    pygame.time.set_timer(pygame.USEREVENT, 1000)
    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    myTank.move("UP", myTank.speed, 50)  # 10 speed, 50 pixels
                elif event.key == pygame.K_DOWN:
                    myTank.move("DOWN", myTank.speed, 50)
                elif event.key == pygame.K_LEFT:
                    myTank.move("LEFT", myTank.speed, 50)
                elif event.key == pygame.K_RIGHT:
                    myTank.move("RIGHT", myTank.speed, 50)
                elif event.key == pygame.K_SPACE:
                    myTank.fire(m)
            elif event.type == pygame.USEREVENT:
                if index < len(m.groups["InvisibleEnemyTank"]):
                    m.groups["InvisibleEnemyTank"].sprites()[index].invisible = False
                    m.groups["EnemyTank"].add(m.groups["InvisibleEnemyTank"].sprites()[index])
                    index += 1

        for tank in m.groups["EnemyTank"]:
            if not tank.moving:
                tank.fire(m)
                tank.move(tank.searchPath(myTank), tank.speed, 50)

        for key in m.groups.keys():
            # Only check the objects that can move
            if key == "EnemyTank" or key == "FriendlyTank" or key == "Missal":
                for tank in m.groups[key]:
                    for targetGroup in m.groups.keys():
                        for item in m.groups[targetGroup]:
                            # avoid check myself
                            if item is tank:
                                continue
                            if pygame.sprite.collide_mask(item, tank):
                                tank.attack(item)
            if key != "InvisibleEnemyTank":
                m.groups[key].draw(screen)

        if myTank.hp == 0 or len(m.groups["Base"]) == 0:
            print("Game Over!")
            pygame.display.set_caption("Game Over!")
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit(0)
                    elif event.type == pygame.KEYDOWN:
                        return
        elif len(m.groups["InvisibleEnemyTank"]) == 0:
            print("You Win!")
            pygame.display.set_caption("You Win!")
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit(0)
                    elif event.type == pygame.KEYDOWN:
                        return

        pygame.display.update()
        fpsClock.tick(60)  # 60 fps means this loop 60 times per 1s


if __name__ == '__main__':
    pygame.init()
    maps = []
    for root, dirs, files in os.walk("./"):
        for file in files:
            if os.path.splitext(file)[1] == '.map':
                maps.append(file)

    maps = sorted(maps)

    for eachMap in maps:
        gameLoop(eachMap)
        print("\n" * 10)
