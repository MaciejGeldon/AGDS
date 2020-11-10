from ASA import ASABaseContainer


def test_create_and_link_should_add_new_created_base_element_at_the_beginning():
    cont = ASABaseContainer()
    cont.add_first(5)

    cont.add_neighbour(1, cont.min)

    assert cont.min.key == 1
    assert cont.max.key == 5

    assert cont.min.predecessor is None
    assert cont.min.successor is cont.max

    assert cont.max.predecessor is cont.min


def test_should_create_new_max_element():
    cont = ASABaseContainer()

    second = cont.add_first(5)
    first = cont.add_neighbour(1, second)

    assert first.predecessor is None
    assert second.successor is None

    assert first.successor is second
    assert second.predecessor is first

    assert cont.max is second
    assert cont.min is first


def test_min_max_behaviour_on_larger_input():
    cont = ASABaseContainer()
    elem_1 = cont.add_first(5)

    e_2 = cont.add_neighbour(6, elem_1)
    e_3 = cont.add_neighbour(1, elem_1)
    e_4 = cont.add_neighbour(10, e_2)
    e_5 = cont.add_neighbour(9, e_2)

    assert cont.min is e_3
    assert cont.max is e_4

    ordered = []
    current = cont.min
    ordered.append(current)

    while current.successor:
        ordered.append(current.successor)
        current = current.successor

    assert ordered == [e_3, elem_1, e_2, e_5, e_4]


def test_reverse_ordering_properties():
    cont = ASABaseContainer()
    elem_1 = cont.add_first(5)

    e_2 = cont.add_neighbour(6, elem_1)
    e_3 = cont.add_neighbour(1, elem_1)
    e_4 = cont.add_neighbour(10, e_2)
    e_5 = cont.add_neighbour(9, e_2)

    revers_order = []
    current = cont.max
    revers_order.append(current)

    while current.predecessor:
        revers_order.append(current.predecessor)
        current = current.predecessor

    assert revers_order == [e_4, e_5, e_2, elem_1, e_3]


def test_asa_base_class_should_be_iterable():
    cont = ASABaseContainer()
    elem_1 = cont.add_first(5)

    e_2 = cont.add_neighbour(6, elem_1)
    e_3 = cont.add_neighbour(1, elem_1)
    e_4 = cont.add_neighbour(10, e_2)
    e_5 = cont.add_neighbour(9, e_2)

    assert [elem for elem in cont] == [e_3, elem_1, e_2, e_5, e_4]


def test_asa_base_class_should_be_iterable_in_reverse():
    cont = ASABaseContainer()
    elem_1 = cont.add_first(5)

    e_2 = cont.add_neighbour(6, elem_1)
    e_3 = cont.add_neighbour(1, elem_1)
    e_4 = cont.add_neighbour(10, e_2)
    e_5 = cont.add_neighbour(9, e_2)

    assert [el for el in reversed(cont)] == [e_4, e_5, e_2, elem_1, e_3]


def test_generator_com_should_work():
    cont = ASABaseContainer()
    elem_1 = cont.add_first(5)

    e_2 = cont.add_neighbour(6, elem_1)
    e_3 = cont.add_neighbour(1, elem_1)
    e_4 = cont.add_neighbour(10, e_2)
    e_5 = cont.add_neighbour(9, e_2)

    gen = (e for e in cont)
    assert next(gen) == e_3
    assert next(gen) == elem_1
    assert next(gen) == e_2
    assert next(gen) == e_5
    assert next(gen) == e_4


def test_base_container_should_return_proper_length():
    cont = ASABaseContainer()
    elem_1 = cont.add_first(5)
    e_2 = cont.add_neighbour(6, elem_1)
    e_3 = cont.add_neighbour(1, elem_1)

    assert len(cont) == 3
