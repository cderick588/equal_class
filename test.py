from equial_class import Equivalent, UnionFind, equivalent_item, equal_fact
from experta import *


class Greetings(KnowledgeEngine):
    eqev= UnionFind()
    eqev.union('greet', 'shit')
    @DefFacts()
    def _initial_action(self):
        yield equal_fact(self.eqev, action="greet")

    @Rule(equal_fact(eqev, action='greet'))
    def ask_name(self):
        # self.declare(equal_fact(self.eqev,name=input("What's your name? ")))
        print('aaa')

    # @Rule(equal_fact(eqev, action='greet'),
    #       NOT(Fact(location=W())))
    # def ask_location(self):
    #     self.declare(equal_fact(self.eqev, location=input("Where are you? ")))

    # @Rule(equal_fact(eqev, action='greet'),
    #       Fact(name=MATCH.name),
    #       Fact(location=MATCH.location))
    # def greet(self, name, location):
    #     print("Hi %s! How is the weather in %s?" % (name, location))


# eqev= UnionFind()
# eqev.union('greet', 'shit')
# a = Fact(action="greet")
# b = Fact(action=W())
# print(a==b)

engine = Greetings()
engine.reset()  # Prepare the engine for the execution.
engine.run()  # Run it!
