from ASA.ASA_tree_and_d_queue import ASABaseElem


class DummyContainer:
    def __init__(self):
        self.min = None
        self.max = None


def test_should_produce_new_element():
    elem = ASABaseElem(2)

    assert elem.key == 2
    assert elem.count == 1


def test_asa_base_elem_should_be_put_in_directory_by_key():
    elem_1 = ASABaseElem(2)
    elem_2 = ASABaseElem(5)

    v_1, v_2 = 'elem_1 value', 'elem_2 value'
    d = dict()
    d[elem_1] = v_1
    d[elem_2] = v_2

    assert elem_1 in d
    assert elem_2 in d

    assert d[elem_1] == v_1
    assert d[elem_2] == v_2


def test_equality_between_asa_base_elements_is_based_on_key_equality():
    elem = ASABaseElem(5)
    elem_2 = ASABaseElem(2)

    array = [elem, elem_2]

    assert elem in array
    assert 5 in array


def test_sorting_in_asa_base_element_is_based_on_key_equality():
    elem = ASABaseElem(5)
    elem_2 = ASABaseElem(2)
    elem_3 = ASABaseElem(3)

    array = [elem, elem_3, elem_2]
    array.sort()

    assert [elem_2, elem_3, elem] == array


def test_create_and_link_should_add_new_created_base_element_at_the_beginning():
    con = DummyContainer()

    first = ASABaseElem(5)
    second = ASABaseElem(1)

    first.link_before(second, con)

    assert second.predecessor is first
    assert second.successor is None

    assert second.predecessor is first
    assert first.predecessor is None


def test_should_add_link_after():
    con = DummyContainer()

    first = ASABaseElem(5)
    second = ASABaseElem(6)

    second.link_after(first, con)

    assert second.predecessor is first
    assert first.successor is second

    assert second.successor is None
    assert first.predecessor is None


def test_should_add_new_element_in_between_existing_elements_when_linking_after_first_twice():
    con = DummyContainer()

    first = ASABaseElem(1)
    last = ASABaseElem(5)
    middle = ASABaseElem(3)

    last.link_after(first, con)

    middle.link_after(first, con)

    assert middle.predecessor is first
    assert middle.successor is last

    assert first.successor is middle
    assert last.predecessor is middle

    assert first.predecessor is None
    assert last.successor is None


def test_should_add_new_element_in_between_existing_elements_when_linking_before_last_twice():
    con = DummyContainer()

    first = ASABaseElem(1)
    last = ASABaseElem(5)
    middle = ASABaseElem(3)

    first.link_before(last, con)
    middle.link_before(last, con)

    assert middle.predecessor is first
    assert middle.successor is last

    assert first.successor is middle
    assert last.predecessor is middle

    assert first.predecessor is None
    assert last.successor is None
