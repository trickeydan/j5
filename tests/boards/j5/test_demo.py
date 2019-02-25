"""Test the demo board."""
from typing import List

from j5.backends import Backend, Environment
from j5.boards import Board
from j5.boards.j5 import DemoBoard
from j5.components import LED, LEDInterface

MockEnvironment = Environment("MockEnvironment")


class MockDemoBoardBackend(LEDInterface, Backend):
    """A test backend for the DemoBoard."""

    environment = MockEnvironment
    board = DemoBoard

    def set_led_state(self, board: Board, identifier: int, state: bool) -> None:
        """Set the LED state."""
        pass

    def get_led_state(self, board: Board, identifier: int) -> bool:
        """Get the current state of an LED."""
        return True

    @classmethod
    def discover(cls) -> List[Board]:
        """Discover boards available on this backend."""
        return []


def test_demo_board_instantiation():
    """Test that we can instantiate a demo board."""
    demo_board = DemoBoard("00000", MockEnvironment)

    assert type(demo_board) == DemoBoard


def test_demo_board_name():
    """Test that we can get the name of a demo board."""
    demo_board = DemoBoard("00000", MockEnvironment)

    assert demo_board.name == "Demo Board"


def test_demo_board_serial():
    """Test that we can get the serial of a demo board."""
    demo_board = DemoBoard("00000", MockEnvironment)

    assert demo_board.serial == "00000"


def test_demo_board_leds():
    """Test that we can get the leds on a demo board."""
    demo_board = DemoBoard("00000", MockEnvironment)

    assert len(demo_board.leds) == 3
    assert type(demo_board.leds[0]) == LED


def test_demo_board_led_operation():
    """Test that we can operate the leds on the demo board."""
    demo_board = DemoBoard("00000", MockEnvironment)

    for led in demo_board.leds:
        led.state = True
        assert led.state


def test_demo_board_detection():
    """Test that we can detect all the demo boards."""
    boards = DemoBoard.discover(MockEnvironment.get_backend(DemoBoard))
    assert len(boards) == 3
