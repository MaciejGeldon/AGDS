class BTreeNode:
    @classmethod
    def split_from_node(cls, node):
        median_key = node.keys[node.t]
        node_left = cls(node.t, leaf=node.leaf)
        node_left.keys = node.keys[:node.t]

        node_right = cls(node.t, leaf=node.leaf)
        node_right.keys = node.keys[node.t + 1:]

        if not node.leaf:
            node_left.children = node.children[:node.t + 1]
            node_right.children = node.children[node.t + 1:]

        return median_key, node_left, node_right

    def __init__(self, t, leaf=False, parent=None):
        self.t = t
        self.keys = []
        self.children = []
        self.leaf = leaf
        self.parent = parent

    def add_key(self, key):
        added = False
        for i in range(len(self.keys)):
            if key < self.keys[i]:
                self.keys.insert(i, key)
                added = True
                break
        if not added:
            self.keys.append(key)

    @property
    def overflow(self):
        return len(self.keys) >= self.t * 2 + 1


class BTree:
    def __init__(self, t):
        self.root = None
        self.t = t

    def insert(self, key):
        if self.root is None:
            self.root = BTreeNode(self.t, True)
            self.root.add_key(key)
            return

        self._insert(key, self.root)

    def _add_and_propagate(self, node, median_key, left_child, right_child):
        parent = node.parent
        if parent is None:
            new_root = BTreeNode(self.t)
            new_root.keys.append(median_key)

            left_child.parent = new_root
            right_child.parent = new_root

            new_root.children.append(left_child)
            new_root.children.append(right_child)

            self.root = new_root
            return

        # search for position in parent node
        for index in range(len(parent.children)):
            if node == parent.children[index]:
                parent.children.pop(index)

                left_child.parent = parent
                right_child.parent = parent

                parent.children.insert(index, left_child)
                parent.children.insert(index + 1, right_child)

        parent.add_key(median_key)

        if parent.overflow:
            median_key_p, left_node_p, right_node_p = BTreeNode.split_from_node(parent)
            self._add_and_propagate(parent, median_key_p, left_node_p, right_node_p)

    def _insert(self, key, node):
        if node.leaf:
            node.add_key(key)
            if node.overflow:
                median_key, left_node, right_node = BTreeNode.split_from_node(node)
                self._add_and_propagate(node, median_key, left_node, right_node)
            return
        else:
            found = False
            for ch_index, n_key in enumerate(node.keys):
                if key < n_key:
                    found = True
                    break

            if not found:
                ch_index += 1

            self._insert(key, node.children[ch_index])


if __name__ == '__main__':
    bt = BTree(1)

    bt.insert(2)
    bt.insert(9)

    bt.insert(1)
    bt.insert(4)
    bt.insert(5)

    bt.insert(3)
    bt.insert(6)
    bt.insert(10)

    print('debugger checkpoint')
