import pygame
import threading
import time


class BaseItem(pygame.sprite.Sprite):
    """
    所有物品的基类，继承自pygame的精灵类。
    所有物品都有生命和伤害，一旦一个物品的生命归零，就清除该物品（无敌物品的生命可以设置为负数）。
    发生碰撞后，需要向对方造成伤害。
    """

    def __init__(self, hp: int, damage: int, iconPath: str, initPosition: tuple, movingSpeed: int, rect=(50, 50)):
        """
        初始化方法，赋值HP、伤害、对传入图片进行缩放以匹配标准方格大小50*50

        :param hp: 物品的血量
        :param damage: 伤害
        :param iconPath: 物品图片路径
        :param initPosition: 初始化的坐标
        """
        super().__init__()
        self.hp = int(hp)
        self.damage = damage
        self.initImage = pygame.transform.scale(pygame.image.load(iconPath), rect)
        self.image = self.initImage
        self.rect = self.image.get_rect()
        self.rect.topleft = initPosition
        self.direction = "UP"
        # moving status
        self.moving = False
        self.speed = movingSpeed
        self.lastStep = self.rect.topleft
        self.gameMapObj = None
        self.invincible = False
        self.invisible = False
        if self.hp < 0:
            self.invincible = True

    def turn(self, direction: str):
        """
        转向方法，用于坦克的转向

        :param direction: 要面向的方向
        """
        self.direction = direction
        if direction == "LEFT":
            self.image = pygame.transform.rotate(self.initImage, 90)
        elif direction == "RIGHT":
            self.image = pygame.transform.rotate(self.initImage, 270)
        elif direction == "UP":
            self.image = self.initImage
        else:
            self.image = pygame.transform.rotate(self.initImage, 180)

    def move(self, direction: str, speed: float, displacement=0):
        """
        移动方法，创建移动线程来播放动画，转向，设置移动锁并且储存移动前的有效位置

        :param direction: 要移动的方向
        :param speed: 速度
        :param displacement: 位移。默认为0.意思是朝某一方向无限移动
        """
        if not self.moving:
            self.moving = True
            self.turn(direction)
            print("{} started moving {}, with {} speed.".format(self, direction, speed))
            # store last position
            if self.rect.left % 50 == 0 and self.rect.top % 50 == 0:
                self.lastStep = self.rect.topleft
            t = threading.Thread(target=moveThread, args=(self, direction, speed, displacement))
            t.setDaemon(True)
            t.start()

    def moveRestore(self):
        """
        回到上一次的有效位置的方法
        """
        self.moving = True
        self.rect.topleft = self.lastStep
        self.moving = False

    def moveBack(self):
        """
        向坦克当前面向方向的反向移动，该方法不会检测目的地是否可移动，尽量不要使用
        """
        if self.direction == "UP":
            self.turn("DOWN")
            self.rect.topleft = (self.rect.left // 50 * 50, self.rect.top // 50 * 50 + 50)
        elif self.direction == "DOWN":
            self.turn("UP")
            self.rect.topleft = (self.rect.left // 50 * 50, self.rect.top // 50 * 50 - 50)
        elif self.direction == "LEFT":
            self.turn("RIGHT")
            self.rect.topleft = (self.rect.left // 50 * 50 - 50, self.rect.top // 50 * 50)
        else:
            self.turn("LEFT")
            self.rect.topleft = (self.rect.left // 50 * 50 + 50, self.rect.top // 50 * 50)

    def isOutOfBounds(self, topleft=None):
        """
        判断地图是否越界

        :return: True - 越界
        False - 不越界
        """
        if topleft is None:
            topleft = self.rect.topleft
        if (topleft[1] > self.gameMapObj.height - 49) or (
                topleft[0] > self.gameMapObj.width - 49) or topleft[0] < 0 or topleft[1] < 0:
            return True
        return False

    def setGameMap(self, gameMap):
        """
        设置GameMap对象的方法

        :param gameMap: GameMap对象
        """
        self.gameMapObj = gameMap

    def applyDamage(self, damage: int):
        """
        应用伤害的方法，由attack方法调用，用来对自身应用伤害。检查伤害是否溢出，溢出置0

        :param damage: 造成的伤害
        :return: 该对象是否是无敌状态。True - 无敌
        """
        if not self.invincible:
            if self.hp - damage <= 0:
                self.hp = 0
                self.kill()
                print("{} was killed!".format(self))
            else:
                self.hp -= damage
                print("{} was affected {} damage, {} hp left!".format(self, damage, self.hp))
        else:

            print("{} is invincible!".format(self))
        return self.invincible

    def attack(self, obj):
        """
        攻击方法，当物体可见且不同种时应用伤害，如果是导弹则由Missal类的attack方法处理

        :param obj: 要攻击的对象
        """
        if not self.invisible and not obj.invisible:
            if self.groups():
                i = 0
                for g in obj.groups():
                    if g not in self.groups():
                        i += 1
                if i >= len(obj.groups()):
                    if isinstance(obj, Missal):
                        # self IS NOT Missal because class Missal override this method
                        obj.attack(self)
                        return
                    print("{} meets {}!".format(self, obj))
                    obj.applyDamage(self.damage)
                    self.applyDamage(obj.damage)


def moveThread(obj: BaseItem, direction: str, speed: float, displacement=0):
    """
    移动线程，该线程有两种方式，一种是固定位移的移动，另一种是不限制位移的移动，第一种移动到指定位置即停止，第二种会一直移动直到越界或被清除。
    第一种情况下，由于位移除以速度不一定是整数，所以在最后一帧的时候直接赋值，防止移动不是整数位移。

    :param obj: 物体对象
    :param direction: 移动方向
    :param speed: 移动速度
    :param displacement: 位移
    """
    # linear animation
    if displacement == 0:
        # infinity mode
        while obj:
            if direction == "UP":
                obj.rect.top -= speed
            elif direction == "DOWN":
                obj.rect.top += speed
            elif direction == "LEFT":
                obj.rect.left -= speed
            else:
                obj.rect.left += speed
            if obj.isOutOfBounds():
                if isinstance(obj, Missal):
                    obj.kill()
                obj.moveRestore()
                return
            else:
                obj.lastStep = obj.rect.topleft
            time.sleep(1 / 60)  # 60 FPS
    else:
        # move to given position
        # calculate the coordinates of destination
        if direction == "UP":
            des = (obj.rect.left, obj.rect.top - displacement)
        elif direction == "DOWN":
            des = (obj.rect.left, obj.rect.top + displacement)
        elif direction == "LEFT":
            des = (obj.rect.left - displacement, obj.rect.top)
        else:
            des = (obj.rect.left + displacement, obj.rect.top)
        if obj.isOutOfBounds(des):
            obj.moveRestore()
            return
        if not (obj.gameMapObj.realMap[des[0] // 50][des[1] // 50] is None or
                not obj.gameMapObj.realMap[des[0] // 50][des[1] // 50].invincible):
            obj.moveRestore()
            return
        while obj and displacement - speed > 0:

            if direction == "UP":
                obj.rect.top -= speed
            elif direction == "DOWN":
                obj.rect.top += speed
            elif direction == "LEFT":
                obj.rect.left -= speed
            else:
                obj.rect.left += speed
            displacement -= speed

            time.sleep(1 / 60)  # 60 frame per 1s
        # last frame, move item to destination directly
        obj.rect.topleft = des
        time.sleep(1 / 60)
    obj.moving = False


class Missal(BaseItem):
    """
    导弹类，继承自基础物品类，对构造方法和attack方法进行了覆盖
    """

    def __init__(self, damage: int, initPosition: tuple, direction: str, movingSpeed: int, gameMap, parentTank):
        """
        初始化子弹的伤害，设置GameMap对象、缩放、设置父坦克对象、旋转、居中对齐并开始移动

        :param damage: 伤害
        :param initPosition: 初始化坐标，一般为坦克的旁边一格
        :param direction: 方向
        :param movingSpeed: 移动速度
        :param gameMap: 地图对象
        :param parentTank: 父坦克对象
        """
        # 所有子弹的HP固定为1
        super().__init__(1, damage, "images/Missal.png", initPosition, movingSpeed,
                         rect=(20, 10))  # 0.8 pixel/fps (also 1 grid / s)
        self.setGameMap(gameMap)
        self.parentTank = parentTank
        # 先转成向上的
        self.initImage = pygame.transform.rotate(self.initImage, 270)
        # 再根据方向转
        self.turn(direction)
        # 居中对齐
        self.alignCenter()
        # 移动
        self.move(self.direction, self.speed)

    def alignCenter(self):
        """
        居中对齐，在一个50*50的格子里对齐一个20*10的图像，需要将topleft加20和15
        """
        x, y = self.rect.topleft
        self.rect.topleft = (x + 20, y + 15)

    def attack(self, obj):
        """
        攻击方法，覆盖自BaseItem的attack方法，判断是否为友方坦克，仅对敌方坦克造成攻击

        :param obj: 要攻击的对象
        """
        if not obj.invisible:
            if self.parentTank.groups():
                i = 0
                for g in obj.groups():
                    if g not in self.parentTank.groups():
                        i += 1
                if i >= len(obj.groups()):
                    # attack enemy
                    print("{} hits {}!".format(self, obj))
                    obj.applyDamage(self.damage)
                    self.applyDamage(obj.damage)
                else:
                    self.applyDamage(obj.damage)


class Wall(BaseItem):
    """
    普通砖墙类，继承自基础物品类，对构造方法进行了覆盖
    """

    def __init__(self, hp, damage, initPosition, movingSpeed):
        # 固定移动速度为0
        super().__init__(hp, damage, "images/Wall.png", initPosition, 0)


class MetalWall(BaseItem):
    """
    金属墙类，继承自基础物品类，对构造方法进行了覆盖
    """

    def __init__(self, hp, damage, initPosition, movingSpeed):
        # 固定移动速度为0
        super().__init__(hp, damage, "images/MetalWall.png", initPosition, 0)


class Base(BaseItem):
    """
    基地类，继承自基础物品类，对构造方法进行了覆盖
    """

    def __init__(self, hp, damage, initPosition, movingSpeed):
        # 固定移动速度为0
        super().__init__(hp, damage, "images/Base.png", initPosition, 0)
