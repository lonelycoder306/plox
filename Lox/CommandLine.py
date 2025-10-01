from Environment import Environment
from List import List
from LoxGroup import LoxGroup
import State
from String import String

def argvSetUp() -> LoxGroup:
    newEnv = Environment()
    newEnv.define("argc", float(len(State.argv)), "FIX")
    savedArgv = [String(arg) for arg in State.argv]
    newEnv.define("argv", List(savedArgv), "FIX")
    return LoxGroup("cl", newEnv)