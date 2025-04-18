from itertools import chain
from experta.fact import Fact
from experta.utils import freeze, unfreeze
from abc import ABC, abstractmethod


class Equivalent(ABC):
    # 抽象基类，这里是等价类的实现。主要是使用并查集的等价类我觉得不能算真的等价类，所以保留一个修改的接口吧
    @abstractmethod
    def root_find(self, x):
        pass

class UnionFind(Equivalent):
    def __init__(self):
        """初始化并查集"""
        self.parent = dict()  # 每个元素的父节点初始化为自身
        self.rank = dict()  # 用于按秩合并的秩数组
    
    def root_find(self, x):
        """查找元素x的根节点，带路径压缩优化"""
        # 元素有可能并未显式加入等价类，所以这里也需要处理元素不存在的情况
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 1
            return x
        if self.parent[x] != x:
            self.parent[x] = self.root_find(self.parent[x])  # 路径压缩
        return self.parent[x]
        
    def union(self, x, y):
        """合并元素x和y所在的集合，按秩合并优化"""
    # =========这是处理x,y不在并查集中的情况=========
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x]=1
        if y not in self.parent:
            self.parent[y] = y
            self.rank[y]=1

    # =========上面处理了x,y不在并查集中的情况，所以就能正常处理了=========

        root_x = self.root_find(x)
        root_y = self.root_find(y)
        
        if root_x == root_y:
            return  # 已经在同一集合
        
        # 按秩合并
        if self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
            self.rank[root_x] += self.rank[root_y]
        else:
            self.parent[root_x] = root_y
            self.rank[root_y] += self.rank[root_x]

class equivalent_item():
    '''
    这个类存在的意义就是为了方便记录等价类和使用等价类。
    通过重载__eq__和__hash__方法，使得相等的等价类的hash值相同，便于rete算法的运行
    '''
    def __init__(self, item, parent):
        self.__item = item
        self.__parent = parent
    
    @property
    def item(self):
        return self.__item
    
    @property
    def parent(self):
        return self.__parent
    def __eq__(self, other):
        if isinstance(other, equivalent_item):
                return self.parent == other.parent
        else:
            return self.parent == other
    def __hash__(self):
        return hash(self.parent)
    
#下面这两句是为了在experta中可以正常使用equivalent_item作为事实的value，因为在Fact的初始化中，会将value转化为freeze(value)再写入
@freeze.register(equivalent_item)
def freeze_equivalent_item(obj):
    return obj
@unfreeze.register(equivalent_item)
def unfreeze_equivalent_item(obj):
    return obj
    
class equal_fact(Fact):
    def __new__(cls, equivalent_env, *args, **kwargs):
        #拦截类的创建，在创建前将所有的参数转化为等价类
        

        assert(isinstance(equivalent_env, Equivalent))
        eq_args=list()
        eq_kwargs=dict()

        #这是将参数转化为等价类的主要操作部分
        for item in args:
            eq_args.append(equivalent_item(item = item, parent = equivalent_env.root_find(item)))

        for key, value in kwargs.items():
            eq_kwargs[key] = equivalent_item(item = value, parent = equivalent_env.root_find(value))
        
        # print(dict(chain(enumerate(eq_args), eq_kwargs.items()))) 哪怕在这里都是正常的，但是下一步就出错了
        
        return super().__new__(cls, *eq_args, **eq_kwargs) #理论上这里进行再创建类的时候，使用的就已经是等价类了。
    
#测试代码：

if __name__ == "__main__":
    uf = UnionFind()
    class User(equal_fact):
        pass
    uf.union('Alice', 'Bob')
    user1 = User(uf, name='Alice')
    print(user1)
    for i in user1.values():
        print((i)) # 这个输出结果很奇怪，为什么前面的初始化根本没有成功？？这里的i还是'Alice'，没能成为等价类？？？？