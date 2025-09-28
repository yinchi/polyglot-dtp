"""A simple test suite with one passing and one failing test.

The failing test is marked as expected to fail (xfail) with strict mode enabled; thus,
if it unexpectedly passes, the test suite will fail.

To run this test suite individually:
    just pytest hello

To run all tests:
    just pytests
"""

import logging

import pytest


def test_always_pass():
    """A test that always passes."""
    logging.info("This test always passes.")
    assert True


@pytest.mark.xfail(strict=True)
def test_always_fail():
    """A test that is expected to fail."""
    logging.info("This test always fails, as expected.")
    assert False
