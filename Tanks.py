import random
import time
import pygame
import threading
from Items import BaseItem, Missal


class Tank(BaseItem):
    """
    坦克类，描述了一个坦克的基本信息，继承自基本物品类，除了基础的参数之外，加入了开火方法。
    """

    def __init__(self, hp, damage, iconPath, initPosition: tuple, movingSpeed):
        """
        构造方法，参数同BaseItem类，加入开火锁
        """
        super().__init__(hp, damage, iconPath, initPosition, movingSpeed)
        self.firing = False

    def fire(self, gameMap):
        """
        开火类，发射一发导弹并将其加入组中，由线程来处理发射操作

        :param gameMap: GameMap对象
        """
        if not self.firing:
            self.firing = True
            print("{} started firing!".format(self))
            t = threading.Thread(target=fireThread, args=(self, gameMap))
            t.setDaemon(True)
            t.start()


def fireThread(obj: Tank, gameMap):
    """
    开火线程函数，把导弹放到坦克面朝方向前一格，并开始移动

    :param obj: 坦克对象
    :param gameMap: 地图对象
    """
    x, y = obj.rect.topleft
    if obj.direction == "UP":
        y -= 50
    elif obj.direction == "DOWN":
        y += 50
    elif obj.direction == "LEFT":
        x -= 50
    else:
        x += 50
    gameMap.groups["Missal"] = gameMap.groups.get("Missal", pygame.sprite.Group())
    gameMap.groups["Missal"].add(Missal(obj.damage, (x, y), obj.direction, obj.speed + 1, gameMap, obj))
    time.sleep(obj.speed * 60 / 1000)
    obj.firing = False


class FriendlyTank(Tank):
    """
    友方坦克类，继承自Tank类，只是定义了所用图片路径
    """

    def __init__(self, hp, damage, initPosition, movingSpeed):
        """
        初始化方法，
        """
        super().__init__(hp, damage, "images/FriendlyTank.png", initPosition, movingSpeed)


class EnemyTank(Tank):
    """
    敌方坦克类
    """

    def __init__(self, hp, damage, iconPath, initPosition, movingSpeed):
        """
        构造方法，除了初始化图片之外，初始化了两个类变量，一个是stuckNum，表示坦克在一个地方卡了几次，3次就随机移动一个地方，另一个是invisible，
        代表敌方坦克是否在地图上，这里是invisible所以True是看不见，其与参数同BaseItem
        """
        super().__init__(hp, damage, iconPath, initPosition, movingSpeed)
        self.initImage = pygame.transform.rotate(self.initImage, 270)
        self.image = self.initImage
        self.stuckNum = 0
        self.invisible = True

    def searchPath(self, targetTank: FriendlyTank):
        """
        查找路径方法，如果坦克在一个地方卡了3次就随机移动一个地方，否则比较当前距离基地和玩家坦克之间的距离，选近的过去

        :param targetTank: 玩家坦克对象
        :return: 下一步应该移动的方向
        """
        # should change into A*
        # Manhattan distance
        if self.lastStep == self.rect.topleft:
            self.stuckNum += 1
        if self.stuckNum >= 3:
            self.stuckNum = 0
            return random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        coordinateToTargetTank = (targetTank.rect.left - self.rect.left, targetTank.rect.top - self.rect.top)
        coordinateToBase = (self.gameMapObj.groups["Base"].sprites()[0].rect.left - self.rect.left,
                            self.gameMapObj.groups["Base"].sprites()[0].rect.top - self.rect.top)
        disToBase = abs(coordinateToBase[0]) + abs(coordinateToBase[1])
        disToTargetTank = abs(coordinateToTargetTank[0]) + abs(coordinateToTargetTank[1])
        if disToBase <= disToTargetTank:
            coor = coordinateToBase
        else:
            coor = coordinateToTargetTank

        if coor[1] < 0:
            return "UP"
        elif coor[1] > 0:
            return "DOWN"
        elif coor[0] < 0:
            return "LEFT"
        else:
            return "RIGHT"
