""" Demo file of use """
from configurehue import Manager, construct_devicetype
from configurehue import ConsoleUser, QhueBridge, JSONStorage

hue_manager = Manager(ConsoleUser(), QhueBridge(), JSONStorage())

print("Access sn {} with {.as_usr}".format(*hue_manager.get().popitem()))