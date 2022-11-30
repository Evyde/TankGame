from Tanks import FriendlyTank, EnemyTank
from Items import Missal, Wall, MetalWall, Base
import pygame


class GameMap:
    """
    地图类，定义了游戏地图，初始化精灵等
    """

    def __init__(self, configPath: str):
        """
        从文件中读取游戏地图，把静态的地图储存在realMap变量中，把所有的精灵组以字典形式储存在groups里面，statics为物品数量，以及地图的长和宽

        :param configPath: 配置文件路径
        """
        super().__init__()
        self.realMap = []
        self.groups = {}
        self.statics = {}
        self.width = 0
        self.height = 0

        with open(configPath) as cf:
            yMap = []
            # 读取第一行的字典，获取名字和简称的对应关系
            relationship = eval(cf.readline())
            for key in relationship.keys():
                self.groups[key] = pygame.sprite.Group()
                self.statics[key] = 0
            self.groups["InvisibleEnemyTank"] = pygame.sprite.Group()

            y = 0
            for line in cf.readlines().__iter__():
                x = 0
                elements = line.split(',')
                tmp = []
                for e in elements:
                    e = e.strip()
                    item = None
                    for key in relationship.keys():
                        if isinstance(relationship[key], list):
                            # 敌人坦克
                            for tanks in relationship[key]:
                                if tanks["name"] == e:
                                    item = eval(
                                        "{}(hp={},damage={},iconPath='{}', initPosition=({}, {}), movingSpeed={})"
                                            .format(key, tanks["hp"], tanks["damage"], tanks["image"], x * 50,
                                                    y * 50, int(tanks["speed"])))
                                    self.groups["InvisibleEnemyTank"].add(item)
                                    self.statics[key] += 1
                        # 普通物品及自己的坦克
                        elif relationship[key]["name"] == e:
                            item = eval("{}(hp={},damage={}, initPosition=({}, {}), movingSpeed={})"
                                        .format(key, relationship[key]["hp"], relationship[key]["damage"], x * 50,
                                                y * 50, int(relationship[key]["speed"])))
                            self.groups[key].add(item)
                            self.statics[key] += 1
                    if key == "EnemyTank" and key == "FriendlyTank":
                        item = None
                    tmp.append(item)
                    x += 1
                y += 1
                yMap.append(tmp)

            # Convert yMap in xMap and store it in self.realMap
            # Notice: this needs complete map
            for x in range(len(yMap[0])):
                tmp = []
                for y in range(len(yMap)):
                    tmp.append(yMap[y][x])
                self.realMap.append(tmp)

            self.width = len(self.realMap) * 50
            self.height = len(self.realMap[0]) * 50
            print("Map <{}> init success, has {} walls, {} metal walls and {} enemy tanks."
                  .format(configPath, self.statics["Wall"], self.statics["MetalWall"], self.statics["EnemyTank"]))
