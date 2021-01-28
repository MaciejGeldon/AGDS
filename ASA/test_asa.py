import pytest
from ASA.ASA_tree_and_d_queue import ASA, ASABaseElem
from statistics import median


def check_structure(root_1, root_2):
    assert root_1.keys == root_2.keys
    assert len(root_1.children) == len(root_2.children)

    for ch_1, ch_2 in zip(root_1.children, root_2.children):
        check_structure(ch_1, ch_2)


@pytest.fixture()
def two_level_tree():
    asa = ASA()

    asa.insert(2)
    asa.insert(9)

    asa.insert(1)
    asa.insert(4)
    asa.insert(5)

    asa.insert(3)
    asa.insert(6)
    asa.insert(10)
    return asa


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
    for i in [2, 5]:
        asa.insert(i)

    assert asa.min == 2
    assert asa.max == 5

    assert asa.root.leaf
    assert asa.root.keys == [2, 5]


def test_overflow_should_split_tree_building_two_level_tree():
    asa = ASA()

    for i in [5, 10, 2]:
        asa.insert(i)

    assert asa.min == 2
    assert asa.max == 10

    assert not asa.root.leaf
    assert asa.root.keys == [5]

    assert len(asa.root.children) == 2
    assert asa.root.children[0].keys == [2]
    assert asa.root.children[1].keys == [10]

    assert asa.root.children[0].leaf
    assert asa.root.children[1].leaf


def test_should_compose_3_level_tree_and_have_proper_structure(two_level_tree):
    asa = two_level_tree

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


def test_insert_should_add_counter_for_keys_in_not_leaf_nodes():
    test_data = [5.1, 4.9, 4.7, 4.6, 5.0, 5.4, 4.6, 5.0, 4.4, 4.9, 5.4]
    asa = ASA()
    for f_val in test_data:
        asa.insert(f_val)

    results = [
        (4.400, 1), (4.600, 2), (4.700, 1), (4.900, 2), (5.000, 2), (5.100, 1), (5.400, 2)
    ]

    for ind, val in enumerate(asa.sorted_d_queue):
        assert results[ind][0] == val.key and results[ind][1] == val.count


def test_asa_should_calculate_proper_avr_and_sum(two_level_tree):
    asa = two_level_tree

    assert asa.sum == 40
    assert asa.avr == 5


def test_asa_should_have_properly_ordered_elements(two_level_tree):
    asa = two_level_tree

    cont = asa.sorted_d_queue
    sorted_cont = [el for el in cont]
    sorted_cont.sort()
    assert sorted_cont == [el for el in cont]


def test_should_calculate_median_1(two_level_tree):
    asa = two_level_tree

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


@pytest.mark.parametrize(
    'delete_key, parent_key',
    [
        (0, 2),
        (1, 2),
    ]
)
def test_should_colapse_structure_when_parent_has_one_hey_and_sibling_also_has_only_one_key(
        delete_key, parent_key
):
    asa = ASA()
    for i in range(3):
        asa.insert(i)

    assert asa.delete(delete_key)

    # check if structure is preserved
    values = [i for i in range(3) if i != delete_key]
    asa_values = [el.key for el in asa.sorted_d_queue]

    assert values == asa_values

    _, parent = asa.search(parent_key)

    assert asa.root == parent
    assert len(parent.keys) == 2
    assert parent.children == []


@pytest.mark.parametrize(
    "to_add, to_delete, insertion_order",
    [
        # right node empty
        ([2.1, 2.2], 4, [1, 2.1, 3, 0, 2, 2.2, 5, 6]),
        ([2.1, 2.2], 5, [1, 2.1, 3, 0, 2, 2.2, 4, 6]),

        # left node empty
        ([7, 8], 1, [3, 5, 7, 2, 4, 6, 8, 0]),
        ([7, 8], 0, [3, 5, 7, 2, 4, 6, 8, 1]),
    ]
)
def test_should_rebalance_when_one_of_sibling_nodes_for_two_level_tree_with_single_key_root_node(
        to_add, to_delete, insertion_order
):
    asa = ASA()
    for i in range(7):
        asa.insert(i)

    for el in to_add:
        asa.insert(el)

    assert asa.delete(to_delete)

    def check_structure(root_1, root_2):
        assert root_1.keys == root_2.keys
        assert len(root_1.children) == len(root_2.children)

        for ch_1, ch_2 in zip(root_1.children, root_2.children):
            check_structure(ch_1, ch_2)

    # integrity check build tree without deleted element
    elements = list(range(7)) + to_add
    elements.remove(to_delete)
    elements.sort()

    asa_after_delete = ASA()
    for el in insertion_order:
        asa_after_delete.insert(el)

    check_structure(asa.root, asa_after_delete.root)


@pytest.mark.parametrize(
    "to_add, to_delete, insertion_order",
    [
        # right node 2 elems, middle delete
        ([2.1, 2.2], 5, [1, 2.1, 3, 7, 9, 8, 10, 0, 2, 2.2, 4, 6]),
        ([2.1, 2.2], 4, [1, 2.1, 3, 7, 9, 8, 10, 0, 2, 2.2, 5, 6]),

        # left node 2 elems, middle delete
        ([11, 12], 5, [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 4]),
        ([11, 12], 4, [0, 1, 2, 3, 6, 7, 8, 9, 10, 11, 12, 5]),
    ]
)
def test_should_rebalance_when_one_of_sibling_in_three_children_parent_got_two_keys(
    to_add, to_delete, insertion_order
):
    asa = ASA()
    for i in range(11):
        asa.insert(i)

    for el in to_add:
        asa.insert(el)

    assert asa.delete(to_delete)

    # integrity check build tree without deleted element
    elements = list(range(7)) + to_add
    elements.remove(to_delete)
    elements.sort()

    asa_after_delete = ASA()
    for el in insertion_order:
        asa_after_delete.insert(el)

    check_structure(asa.root, asa_after_delete.root)


@pytest.mark.parametrize(
    "to_delete, root_keys, insertion_order",
    [
        (4, [1, 3], [0, 1, 2, 3, 5, 6]),
        (5, [1, 3], [0, 1, 2, 3, 4, 6]),
        (6, [1, 3], [0, 1, 2, 3, 4, 5]),

        (0, [3, 5], [1, 3, 4, 5, 6, 2]),
        (1, [3, 5], [0, 3, 4, 5, 6, 2]),
        (2, [3, 5], [0, 3, 4, 5, 6, 1]),

    ]
)
def test_should_replace_root_when_tree_will_shrink(to_delete, root_keys, insertion_order):
    asa = ASA()
    for i in range(7):
        asa.insert(i)

    assert asa.delete(to_delete)
    assert asa.root.keys == root_keys

    asa_after_delete = ASA()
    for el in insertion_order:
        asa_after_delete.insert(el)

    check_structure(asa.root, asa_after_delete.root)


@pytest.mark.parametrize(
    "to_delete, root_keys, insertion_order",
    [
        (12, [3, 7], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14]),
        (14, [3, 7], [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]),

        (10, [3, 7], [0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14, 9]),
        (8, [3, 7], [0, 1, 2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 10]),

        (0, [7, 11], [2, 3, 4, 7, 9, 8, 10, 11, 12, 13, 14, 5, 6, 1]),
        (1, [7, 11], [0, 3, 4, 7, 9, 8, 10, 11, 12, 13, 14, 5, 6, 2]),

    ]
)
def test_asa_delete_should_handle_recursive_rebalancing(to_delete, root_keys, insertion_order):
    asa = ASA()
    for i in range(15):
        asa.insert(i)

    assert asa.delete(to_delete)
    assert asa.root.keys == root_keys

    asa_after_delete = ASA()
    for el in insertion_order:
        asa_after_delete.insert(el)

    check_structure(asa.root, asa_after_delete.root)


@pytest.mark.parametrize(
    "del_all_but",
    [
        0, 2, 5
    ]
)
def test_delete_sanity_when_deleting_everything_from_builded_key_except_from_one_element(del_all_but):
    asa = ASA()
    for i in range(7):
        asa.insert(i)

    delete = [i for i in range(7) if i != del_all_but]

    for dd in delete:
        asa.delete(dd)

    assert len(asa.root.keys) == 1
    assert asa.root.keys == [del_all_but]
    assert asa.root.children == []


@pytest.mark.parametrize(
    'insert, root, min_, max_',
    [
        (['a'], 'a', 'a', 'a'),
        (['a', 'b', 'c'], 'b', 'a', 'c'),
        (['param_1', 'param_2', 'param_3'], 'param_2', 'param_1', 'param_3')
    ]
)
def test_asa_with_strings(insert, root, min_, max_):
    asa = ASA()
    for el in insert:
        asa.insert(el)

    assert asa.root.keys[0].key == root
    assert asa.min.key == min_
    assert asa.max.key == max_
