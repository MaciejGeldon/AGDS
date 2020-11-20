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


def test_asa_should_have_proper_parent_element_structure():
    asa = ASA()
    for key in [2, 3, 5, 7, 8, 9, 10, 11]:
        asa.insert(key)

    elem, node = asa.search(11)

    assert node.parent.keys == [9]
    grandparent = node.parent.parent

    assert grandparent == asa.root
    assert asa.root.keys == [7]


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

    cont = asa.sorted_d_queue
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

    cont = asa.sorted_d_queue
    l_to_comp = [elem.key for elem in cont]
    assert median(l_to_comp) == asa.median


@pytest.mark.parametrize(
    "elements", [
        [1, 1, 2], [1, 2], [5],
        [1, 2, 2, 3, 3, 4], [5, 5, 5],
        [1, 1, 1, 2, 2, 3, 4, 5, 6],
        [2, 9, 1, 4, 5, 3, 6]
    ]
)
def test_should_check_median_for_given_elements(elements):
    asa = ASA()

    for e in elements:
        asa.insert(e)

    assert asa.median == median(elements)


def test_asa_search_empty_asa_should_return_node():
    asa = ASA()
    found, _ = asa.search(10)
    assert found is False


@pytest.mark.parametrize(
    "elements", [
        [1, 1, 2], [1, 2], [5],
        [1, 2, 2, 3, 3, 4], [5, 5, 5],
        [1, 1, 1, 2, 2, 3, 4, 5, 6],
        [2, 9, 1, 4, 5, 3, 6]
    ]
)
def test_should_return_false_for_given_asa_trees(elements):
    asa = ASA()

    for e in elements:
        asa.insert(e)
    found, _ = asa.search(10)
    assert found is False


@pytest.mark.parametrize(
    "elements,key", [
        ([1, 1, 2], 1),
        ([1, 2, 2, 3, 3, 4], 4),
        ([1, 1, 1, 2, 2, 3, 4, 5, 6], 5),
        ([2, 9, 1, 4, 5, 3, 6], 9),
        ([2, 9, 1, 4, 5, 3, 6, 10], 6),
        ([1, 2, 4, 5, 9], 4)
    ]
)
def test_should_return_element_for_given_asa_trees_and_search_keys(elements, key):
    asa = ASA()

    for e in elements:
        asa.insert(e)

    found, _ = asa.search(key)
    assert found
    assert found.key == key


def test_delete_for_initial_case():
    asa = ASA()

    assert asa.delete(1) is False


@pytest.mark.parametrize(
    'elements,delete_key,count',
    [
        ([1, 1, 2], 1, 1),
        ([1, 2, 2, 3, 3, 4, 4], 4, 1),
        ([1, 1, 1, 2, 2, 3, 4, 5, 5, 6], 5, 1),
        ([2, 9, 9, 9, 1, 4, 5, 3, 6], 9, 2),
        ([2, 9, 1, 4, 5, 3, 6, 6, 6, 6, 10], 6, 3),
    ]
)
def test_delete_should_work_for_existing_duplicated_key(elements, delete_key, count):
    asa = ASA()
    for key in elements:
        asa.insert(key)

    del_key, _ = asa.search(delete_key)
    assert asa.delete(delete_key)
    assert del_key.count == count


def test_delete_should_return_false_if_key_for_delete_not_found():
    asa = ASA()
    for i in [1, 2, 2, 3, 3, 4, 4]:
        asa.insert(i)

    assert asa.delete(10) is False


def test_delete_should_remove_key_from_node_with_two_keys_without_rebalancing():
    asa = ASA()
    for i in [2, 3, 5, 9]:
        asa.insert(i)

    assert asa.delete(5)

    found, node = asa.search(5)

    assert found is False and node is None

    assert [e.key for e in asa.sorted_d_queue] == [2, 3, 9]

    found, node = asa.search(9)
    assert found

    assert node.parent.keys == [3]
    assert node.leaf is True


def test_delete_should_remove_key_from_node_with_two_keys_without_rebalancing_v2():
    asa = ASA()
    for i in [2, 3, 5, 7, 8, 9, 10, 11]:
        asa.insert(i)

    assert asa.delete(10)

    found, node = asa.search(10)

    assert found is False and node is None

    assert [e.key for e in asa.sorted_d_queue] == [2, 3, 5, 7, 8, 9, 11]

    found, node = asa.search(11)
    assert found

    assert node.parent.keys == [9]
    assert node.leaf is True


@pytest.mark.parametrize(
    'elem,node_elem',
    [(6.5, 6), (7.5, 8)]
)
def test_delete_should_replace_deleted_node_key_with_leaf_key_when_proper_leaf_key_found(elem, node_elem):
    asa = ASA()
    for i in range(13):
        asa.insert(i)

    # this will be predecessor or successor of 7
    asa.insert(elem)

    _, node = asa.search(node_elem)

    assert len(node.keys) == 2

    assert asa.delete(7)
    assert elem in asa.root.keys

    elem, node = asa.search(node_elem)
    assert len(node.keys) == 1


@pytest.mark.parametrize(
    'elem,node_elem',
    [(0.1, 0), (1.5, 2)]
)
def test_delete_should_handle_deleting_non_leaf_in_one_level_tree_case(elem, node_elem):
    asa = ASA()
    for i in range(3):
        asa.insert(i)

    asa.insert(elem)

    _, node = asa.search(node_elem)

    assert len(node.keys) == 2

    assert asa.delete(1)
    assert elem in asa.root.keys

    elem, node = asa.search(node_elem)
    assert len(node.keys) == 1


@pytest.mark.parametrize(
    'add, delete, empty_value, ch_index',
    [
        (0.1, 2, 1, 1),
        (1.1, 0, 1, 0),
        (1.1, 4, 3, 2),
        (3.5, 2, 3, 1)
    ]
)
def test_delete_should_handle_filing_empty_leaf_for_one_level_tree(
        add, delete, empty_value, ch_index
):
    asa = ASA()
    for i in range(5):
        asa.insert(i)

    asa.insert(add)

    assert asa.delete(delete)
    modified_node = asa.root.children[ch_index]
    assert empty_value == modified_node.keys[0].key

    # check if structure is preserved
    parent = modified_node.parent
    root = asa.root

    assert parent == root
    assert len(parent.keys) == 2

    p_keys = parent.keys
    assert p_keys[0] < p_keys[1]

    ch_1, ch_2, ch_3 = parent.children
    assert ch_1.keys[0].key < p_keys[0].key < ch_2.keys[0].key
    assert ch_2.keys[0].key < p_keys[1].key < ch_3.keys[0].key

    assert ch_1.keys[0].key < ch_2.keys[0].key < ch_3.keys[0].key
    assert len(ch_1.keys) == len(ch_2.keys) == len(ch_3.keys) == 1


@pytest.mark.parametrize(
    'add, delete, empty_value, ch_index',
    [
        (0.1, 2, 1, 1),
        (1.1, 0, 1, 0),
    ]
)
def test_delete_should_handle_filing_empty_leaf_for_one_level_tree_and_two_children(
        add, delete, empty_value, ch_index
):
    asa = ASA()
    for i in range(3):
        asa.insert(i)

    asa.insert(add)

    assert asa.delete(delete)
    modified_node = asa.root.children[ch_index]
    assert empty_value == modified_node.keys[0].key

    # check if structure is preserved
    parent = modified_node.parent
    root = asa.root

    assert parent == root
    assert len(parent.keys) == 1

    p_keys = parent.keys
    ch_1, ch_2 = parent.children

    assert ch_1.keys[0].key < p_keys[0].key < ch_2.keys[0].key

    assert ch_1.keys[0].key < ch_2.keys[0].key
    assert len(ch_1.keys) == len(ch_2.keys) == 1


@pytest.mark.parametrize(
    'delete_key, parent_key, ch_index',
    [
        (0, 3, 0),
        (2, 3, 0),
        (4, 1, 1)
    ]
)
def test_should_delete_empty_leaf_when_parent_got_two_elements(
        delete_key, parent_key, ch_index
):
    asa = ASA()
    for i in range(5):
        asa.insert(i)

    assert asa.delete(delete_key)

    # check if structure is preserved
    values = [i for i in range(5) if i != delete_key]
    asa_values = [el.key for el in asa.sorted_d_queue]

    assert values == asa_values

    _, parent = asa.search(parent_key)

    assert parent == asa.root
    assert len(parent.keys) == 1

    p_keys = parent.keys
    ch_1, ch_2 = parent.children

    assert ch_1.keys[0].key < p_keys[0].key < ch_2.keys[0].key

    assert ch_1.keys[0].key < ch_2.keys[0].key

    child_with_two_keys = parent.children[ch_index]
    assert len(child_with_two_keys.keys) == 2
    assert len(parent.children[int(bool(1 - ch_index))].keys) == 1


# I need to finish this when I add rebalance steps 8,9
# @pytest.mark.parametrize(
#     'delete_key, parent_key',
#     [
#         (0, 2),
#         (1, 2),
#     ]
# )
# def test_should_delete_empty_leaf_when_parent_got_two_elements(
#         delete_key, parent_key
# ):
#     asa = ASA()
#     for i in range(3):
#         asa.insert(i)
#
#     assert asa.delete(delete_key)
#
#     # check if structure is preserved
#     values = [i for i in range(3) if i != delete_key]
#     asa_values = [el.key for el in asa.asa_container]
#
#     assert values == asa_values
#
#     _, parent = asa.search(parent_key)
#
#     assert asa.root == parent
#     assert len(parent.keys) == 2
#     assert parent.children == []
