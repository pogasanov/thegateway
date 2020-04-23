from collections import defaultdict
from typing import List, Dict, Set


def group_by(elements: List, attribute: str, many: bool = True) -> Dict:
    """
    Groups list of elements into dictionary that has one of attributes of elements set as key
    and list of corresponding elements / corresponding element as value.
    Used to easier search for specific elements.
    :parameter many should be set to False if only one element matches each value of attribute,
    then values of output dict will be elements instead of lists of elements
    """
    output_dict = defaultdict(lambda: [] if many else None)
    for element in elements:
        value = element[attribute]
        if many:
            output_dict[value].append(element)
        else:
            output_dict[value] = element
    return output_dict


def retry(retries: int, exceptions: Set[Exception]):
    """Retries function *retries* times if one of exception in *exceptions* occurs"""

    def decorator(function):
        def wrapper(*args, **kwargs):
            times_retried = 0
            while True:
                try:
                    return function(*args, **kwargs)
                except exceptions:
                    times_retried += 1
                    if times_retried >= retries:
                        raise

        return wrapper

    return decorator
