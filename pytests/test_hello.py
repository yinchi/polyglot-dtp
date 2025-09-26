"""A simple test suite with one passing and one failing test.

The failing test is marked as expected to fail (xfail) with strict mode enabled; thus,
if it unexpectedly passes, the test suite will fail.
"""

import pytest


def test_always_pass():
    """A test that always passes."""
    assert True


@pytest.mark.xfail(strict=True)
def test_always_fail():
    """A test that is expected to fail."""
    assert False
