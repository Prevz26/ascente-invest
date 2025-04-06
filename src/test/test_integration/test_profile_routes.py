from main import create_app
import pytest

app = create_app()

def func(a,b):
    return a+b

def test_func():
    assert func(1,3) == 4
