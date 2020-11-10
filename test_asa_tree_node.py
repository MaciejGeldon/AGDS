from ASA import ASABaseElem, ASATreeNode, ASABaseContainer


def test_asa_node_should_add_first_key_and_initialize_container():
    con = ASABaseContainer()
    tree_node = ASATreeNode()
    key = 2

    tree_node.add_key(key, con)

    assert len(tree_node.keys) == 1
    assert isinstance(tree_node.keys[0], ASABaseElem)
    assert con.min == key
    assert con.max == key


def test_add_key_should_accept_int_and_asa_base_elements_as_arguments():
    con = ASABaseContainer()
    tree_node = ASATreeNode()
    asa_base_elem = ASABaseElem(5)

    tree_node.add_key(2, con)
    tree_node.add_key(asa_base_elem, con)

    assert len(tree_node.keys) == 2
    assert con.min == 2
    assert con.max == 5
    assert tree_node.children == []


def test_tree_node_should_add_duplicates():
    con = ASABaseContainer()
    tree_node = ASATreeNode()

    tree_node.add_key(2, con)
    tree_node.add_key(2, con)

    assert len(tree_node.keys) == 1
    assert tree_node.keys[0].count == 2
    assert con.min == 2
    assert con.max == 2


def test_tree_node_should_add_elements_in_proper_order():
    con = ASABaseContainer()
    tree_node = ASATreeNode()

    tree_node.add_key(5, con)
    tree_node.add_key(2, con)
    tree_node.add_key(3, con)

    assert len(tree_node.keys) == 3
    assert tree_node.keys[0] == 2
    assert tree_node.keys[1] == 3
    assert tree_node.keys[2] == 5


def test_to_ong_node_should_overflow():
    con = ASABaseContainer()
    tree_node = ASATreeNode()

    tree_node.add_key(5, con)
    tree_node.add_key(2, con)
    tree_node.add_key(3, con)

    assert tree_node.overflow


def test_split_from_node_should_return_median_key_and_correctly_divided_keys_in_case_of_leaf_node():
    con = ASABaseContainer()
    tree_node = ASATreeNode()

    tree_node.add_key(5, con)
    tree_node.add_key(2, con)
    tree_node.add_key(3, con)

    median_key, node_left, node_right = ASATreeNode.split_from_node(tree_node)

    assert median_key == 3
    assert isinstance(median_key, ASABaseElem)

    assert len(node_left.keys) == 1
    assert node_left.keys[0] == tree_node.keys[0]

    assert len(node_right.keys) == 1
    assert node_right.keys[0] == tree_node.keys[2]


def test_should_split_keys_and_children_properly_when_node_is_not_leaf():
    con = ASABaseContainer()
    tree_node = ASATreeNode()

    ch_1 = ASATreeNode()
    ch_1.add_key(1, con)

    ch_2 = ASATreeNode()
    ch_2.add_key(3, con)

    ch_3 = ASATreeNode()
    ch_3.add_key(5, con)

    tree_node.add_key(6, con)
    tree_node.add_key(2, con)
    tree_node.add_key(4, con)

    tree_node.children = [ch_1, ch_2, ch_3]

    median_key, node_left, node_right = ASATreeNode.split_from_node(tree_node)

    assert median_key == 4
    assert isinstance(median_key, ASABaseElem)

    assert len(node_left.keys) == 1
    assert node_left.keys[0] == tree_node.keys[0]

    assert len(node_right.keys) == 1
    assert node_right.keys[0] == tree_node.keys[2]

    assert node_left.children == [ch_1, ch_2]
    assert node_right.children == [ch_3]