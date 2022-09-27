#!/usr/bin/env python3.9.2
import io
import unittest
from pyrobot import PyRobot, Coordinates, Direction, PyRobotController


class TestPyRobot(unittest.TestCase):

    def test_left(self):
        robot = PyRobot()
        robot.place((None, 0, 0, 'EAST'))
        for direction in [Direction.NORTH, Direction.WEST, Direction.SOUTH, Direction.EAST]:
            robot.left()
            self.assertEqual(robot.direction, direction)

    def test_right(self):
        robot = PyRobot()
        robot.place((None, 0, 0, 'EAST'))
        for direction in [Direction.SOUTH, Direction.WEST, Direction.NORTH, Direction.EAST]:
            robot.right()
            self.assertEqual(robot.direction, direction)

    def test_place(self):
        robot = PyRobot()
        invalid_params = [(None, 5, 5, 'EAST'), (None, 5, 6, 'EAST')]
        # check robot for if not ready and out of range
        self.assertFalse(robot.in_range())
        # check for out of range
        for params in invalid_params:
            robot.place(params)
            self.assertFalse(robot.in_range())
        # check for valid placement
        robot.place((None, 1, 1, 'NORTH'))
        self.assertTrue(robot.in_range(), True)
        # check again
        for params in invalid_params:
            robot.place(params)
            self.assertFalse(robot.in_range())


class TestPyRobotController(unittest.TestCase):

    def test_start(self):
        commands = """
            PLACE 0,0,NORTH
            MOVE
            REPORT

            PLACE 0,0,NORTH
            LEFT
            REPORT

            PLACE 1,2,EAST
            MOVE
            MOVE
            LEFT
            MOVE
            REPORT
        """
        expected_report = '''Output: 0,1,NORTH
Output: 0,0,WEST
Output: 3,3,NORTH
'''
        std_out = io.StringIO()
        controller = PyRobotController(PyRobot(io_file=std_out))
        controller.start(io.StringIO(commands))
        self.assertMultiLineEqual(std_out.getvalue(), expected_report)


if __name__ == '__main__':
    unittest.main()
