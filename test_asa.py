import pytest
from ASA import ASA, ASABaseElem
from statistics import median


def test_should_add_one_key_to_asa_and_properly_initialize_dependent_data_structures():
    asa = ASA()
    asa.insert(2)

    assert asa.min == asa.max
    assert asa.min == 2
    assert isinstance(asa.min, ASABaseElem)

    assert asa.root.keys == [2]
    assert asa.root.children == []
    assert asa.root.leaf


def test_one_level_asa_tree():
    asa = ASA()
    asa.insert(2)
    asa.insert(5)

    assert asa.min == 2
    assert asa.max == 5

    assert asa.root.leaf
    assert asa.root.keys == [2, 5]


def test_overflow_should_split_tree_building_two_level_tree():
    asa = ASA()

    asa.insert(5)
    asa.insert(10)
    asa.insert(2)

    assert asa.min == 2
    assert asa.max == 10

    assert not asa.root.leaf
    assert asa.root.keys == [5]

    assert len(asa.root.children) == 2
    assert asa.root.children[0].keys == [2]
    assert asa.root.children[1].keys == [10]

    assert asa.root.children[0].leaf
    assert asa.root.children[1].leaf


def test_should_compose_3_level_tree_and_have_proper_structure():
    asa = ASA()

    asa.insert(2)
    asa.insert(9)

    asa.insert(1)
    asa.insert(4)
    asa.insert(5)

    asa.insert(3)
    asa.insert(6)
    asa.insert(10)

    assert asa.min == 1
    assert asa.max == 10

    assert asa.root.keys == [5]

    r = asa.root

    assert len(r.children) == 2

    assert r.children[0].keys == [2]
    assert r.children[1].keys == [9]

    assert not r.children[0].leaf
    assert not r.children[1].leaf

    l_tree = r.children[0]
    r_tree = r.children[1]

    assert l_tree.children[0].keys == [1]
    assert l_tree.children[1].keys == [3, 4]
    assert l_tree.children[0].leaf
    assert l_tree.children[1].leaf

    assert r_tree.children[0].keys == [6]
    assert r_tree.children[1].keys == [10]
    assert r_tree.children[0].leaf
    assert r_tree.children[1].leaf


def test_asa_should_calculate_proper_avr_and_sum():
    asa = ASA()

    asa.insert(2)
    asa.insert(9)

    asa.insert(1)
    asa.insert(4)
    asa.insert(5)

    asa.insert(3)
    asa.insert(6)
    asa.insert(10)

    assert asa.sum == 40
    assert asa.avr == 5


def test_asa_should_have_properly_ordered_elements():
    asa = ASA()

    asa.insert(2)
    asa.insert(9)

    asa.insert(1)
    asa.insert(4)
    asa.insert(5)

    asa.insert(3)
    asa.insert(6)
    asa.insert(10)

    cont = asa.asa_container
    sorted_cont = [el for el in cont]
    sorted_cont.sort()
    assert sorted_cont == [el for el in cont]


def test_should_calculate_median_1():
    asa = ASA()

    asa.insert(2)
    asa.insert(9)

    asa.insert(1)
    asa.insert(4)
    asa.insert(5)

    asa.insert(3)
    asa.insert(6)
    asa.insert(10)

    cont = asa.asa_container
    l_to_comp = [elem.key for elem in cont]
    assert median(l_to_comp) == asa.median


@pytest.mark.parametrize(
    "elements", [
        [1, 1, 2], [1, 2], [5],
        [1, 2, 2, 3, 3, 4], [5, 5, 5],
        [1, 1, 1, 2, 2, 3, 4, 5, 6]
    ]
)
def test_should_check_median_for_given_elements(elements):
    asa = ASA()

    for e in elements:
        asa.insert(e)

    assert asa.median == median(elements)
