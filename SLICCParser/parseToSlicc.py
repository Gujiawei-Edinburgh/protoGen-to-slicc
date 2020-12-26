from Machine import Machine
import Transition
import Action
import Port


# def getTransitionTable(source, line, cahche_transition):
#     return

if __name__ == "__main__":
    source = open("/Users/gujiawei/Desktop/Edinburgh/MscProject/ProtoGen/MSI_Proto.m")
    line = source.readline()
    is_cache_get = False
    is_directory_get = False
    is_event_get = False

    cache_machine = Machine()
    directory_machine = Machine()


    while line:
        line = source.readline()
        if line.__contains__("s_cache: enum") and not is_cache_get:
            cache_machine.getStatesOrEvents(source,line,1)
            is_cache_get = True
        elif line.__contains__("s_directory: enum") and not is_directory_get:
            directory_machine.getStatesOrEvents(source,line,1)
            is_directory_get = True
        elif line.__contains__("MessageType: enum") and not is_event_get:
            cache_machine.getStatesOrEvents(source, line, 2)
            is_event_get = True
        elif is_cache_get and is_directory_get and is_event_get:
            cache_machine.getTransition()
            directory_machine.getTransition()
            is_cache_get = False
        elif line.__contains__("function Func_cache"):
            cache_machine.getTransitionTable(source, line)
        # elif line.__contains__("function Func_directory"):
        #     pass
        #     #directory_machine.getTransitionTable(source, line)
    source.close()
    

