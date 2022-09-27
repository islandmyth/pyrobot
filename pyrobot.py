#!/usr/bin/env python3.9.2

import sys
import re
from enum import Enum, auto


class Direction(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()


class Coordinates:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Coordinates(self.x + other.x, self.y + other.y)

    def in_range(self, boundary):
        """Check if x and y is within boundary range e.g.:
            x >= 0 and x <= 4
            y >= 0 and y <= 4
         """
        return 0 <= self.x <= boundary.x and 0 <= self.y <= boundary.y


class PyRobot:
    def is_ready(fn):
        def fn_ready(self):
            if self.is_ready:
                # Check if position within boundary range. Ignore commands if not in range
                if self.position and not self.position.in_range(self.boundaries):
                    return
                return fn(self)
        return fn_ready

    def __init__(self, **kwargs):
        """Set to true when a valid PLACE command has been executed."""
        self.is_ready = False
        self.position = None
        self.direction = None
        self.config = kwargs["config"] if "config" in kwargs else {"dimension_x": 4, "dimension_y": 4}
        self.io_file = kwargs["io_file"] if "io_file" in kwargs else sys.stdout

        """Available commands for the controller """
        self.controls = ["place", "move", "left", "right", "report"]
        self.position_const = {
            Direction.NORTH: Coordinates(0, 1),  # +1 to y-axis going north
            Direction.SOUTH: Coordinates(0, -1),  # -1 to y-axis going south
            Direction.EAST: Coordinates(1, 0),  # +1 to x-axis going east
            Direction.WEST: Coordinates(-1, 0)  # -1 to x-axis going weast
        }
        self.boundaries = Coordinates(self.config["dimension_x"], self.config["dimension_y"])

    @is_ready
    def in_range(self):
        return True

    def place(self, params=None):
        command, x, y, direction = params
        position = Coordinates(int(x), int(y))
        self.is_ready = position.in_range(self.boundaries)
        if self.is_ready:
            self.position = position
            self.direction = Direction[direction]

    @is_ready
    def move(self):
        position = self.position + self.position_const[self.direction]
        if position.in_range(self.boundaries):
            self.position = position

    @is_ready
    def left(self):
        self.direction = self.rotate(Direction.WEST, Direction.EAST, Direction.NORTH, Direction.SOUTH)

    @is_ready
    def right(self):
        self.direction = self.rotate(Direction.EAST, Direction.WEST, Direction.SOUTH, Direction.NORTH)

    @is_ready
    def report(self):
        print(f'Output: {self.position.x},{self.position.y},{self.direction.name}', file=self.io_file)

    def rotate(self, north, south, east, west):
        return {Direction.NORTH: north,
                Direction.SOUTH: south,
                Direction.EAST: east,
                Direction.WEST: west}[self.direction]


class PyRobotController:

    def __init__(self, robot: PyRobot):
        self.robot = robot

    def parse_input(self, line):
        params = None
        command = line.strip()
        pattern = re.compile(r'(PLACE) (\d+),(\d+),(NORTH|SOUTH|EAST|WEST)')
        match = pattern.match(command)
        if match:
            params = match.groups()
            command = match.group(1)
        return command.lower(), params

    def start(self, command_input=sys.stdin):
        """
            Accept user input from console and file
            console input: python pyRobot.py
            file input: python pyRobot.py < commands.txt
        """
        for line in command_input:
            command, params = self.parse_input(line)
            if command in self.robot.controls and hasattr(self.robot, command) and callable(getattr(self.robot, command)):
                try:
                    if params:
                        getattr(self.robot, command)(params)
                    else:
                        getattr(self.robot, command)()
                except: pass


if __name__ == "__main__":
    control = PyRobotController(PyRobot(config={"dimension_x": 4,
                                                "dimension_y": 4}))
    control.start()

