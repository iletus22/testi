import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest

from main import main
from gui import GUI
from storage import Storage
from settings import Settings


def test_instantiation():
    gui = GUI()
    storage = Storage()
    settings = Settings()
    assert gui is not None
    assert storage is not None
    assert settings is not None


def test_main_runs():
    # main() should run without raising an exception
    main()
