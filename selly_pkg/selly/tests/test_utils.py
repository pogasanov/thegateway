from selly.utils import group_by, retry


def test_group_by_many():
    elements = [{"a": 1, "ID": 1}, {"a": 2, "ID": 2}, {"a": 1, "ID": 3}]
    grouped = group_by(elements, "a")
    assert list(grouped.keys()) == [1, 2]
    assert grouped[1] == [elements[0], elements[2]]
    assert grouped[2] == [elements[1]]


def test_group_by_single():
    elements = [{"a": 1, "ID": 1}, {"a": 2, "ID": 2}, {"a": 3, "ID": 3}]
    grouped = group_by(elements, "a", False)
    assert list(grouped.keys()) == [1, 2, 3]
    assert grouped[1] == elements[0]
    assert grouped[2] == elements[1]
    assert grouped[3] == elements[2]


def test_retry():
    retried_times = [0]

    @retry(5, ZeroDivisionError)
    def foo():
        retried_times[0] += 1
        if retried_times[0] != 5:
            raise ZeroDivisionError

    foo()
    assert retried_times[0] == 5
