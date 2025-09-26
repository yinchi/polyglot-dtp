"""A simple test suite with one passing and one failing test.

The failing test is marked as expected to fail (xfail) with strict mode enabled; thus,
if it unexpectedly passes, the test suite will fail.
"""

import pytest

# We use \n\n in print statements to ensure clear separation in pytest output, e.g.,
# when using `pytest -s`.


def test_always_pass():
    """A test that always passes."""
    print("\n\nThis test always passes.")
    assert True


@pytest.mark.xfail(strict=True)
def test_always_fail():
    """A test that is expected to fail."""
    print("\n\nThis test always fails, as expected.")
    assert False
