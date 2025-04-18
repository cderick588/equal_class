from experta.matchers.rete.check import FeatureCheck, CheckFunction
from experta.fieldconstraint import L, W
from experta.engine import KnowledgeEngine, DefFacts
from experta import Rule, Fact, NOT, AND, OR, MATCH

class UnionFind():
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


class Equal_patch():
    '''
    补丁类，通过重注册泛函get_check_function中的L来实现
    '''
    def __init__(self, equal_env): 
        self.equal_env = equal_env

    def activate(self):
        original = FeatureCheck.get_check_function.registry[L]
        self.origin_fun = original # 这是为了后续deactivate撤销等价类
        
        def wrapper(pce, what=None):
            check_func = original(pce, what)
            
            def new_equal_literal(actual, expected): #主要修改部分：我们只需要将原本的==判断修改成比较等价类的father就可以了
                if eq_env.root_find(expected.value) == eq_env.root_find(actual):
                    if expected.__bind__ is None:
                        return True
                    else:
                        return {expected.__bind__: actual}
                return False
                
            return CheckFunction(
                key_a=check_func.key_a,
                key_b=check_func.key_b,
                expected=check_func.expected,
                check=new_equal_literal
            )
        
        FeatureCheck.get_check_function.register(L)(wrapper) # 重注册使得补丁生效
    def deactivate(self):
        FeatureCheck.get_check_function.register(L)(self.origin_fun) # 恢复


if __name__ == "__main__":
    eq_env = UnionFind()
    eq_env.union("a", "b")
    eq_env.union("aaa", "erick")

    patch = Equal_patch(eq_env)
    patch.activate()

    class Greetings(KnowledgeEngine):
        @DefFacts()
        def _initial_action(self):
            yield Fact(action="a")
            yield Fact(name = "aaa")
            yield Fact(age = 16)

        @Rule(Fact(action='b'), NOT(Fact(name = W())))
        def _(self):
            print('aaa')

        @Rule(AND(Fact(action='b'), Fact(name=MATCH.name)))
        def greet(self, name):
            print("hi!{}".format(name))

        @Rule(AND(OR(Fact(action='b'), Fact(age = 17)), Fact(name="erick")))
        def say(self):
            print("=============")
    
    engine = Greetings() #实例化的时刻，是创建rete网络的时刻，所以只要在实例化的时候补丁是生效的，我们实例化出来的engine就是带有等价类的
    patch.deactivate()

    engine.reset()  # Prepare the engine for the execution.
    engine.run()  # Run it!
