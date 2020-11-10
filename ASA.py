class ASABaseElem:
    def __init__(self, key, count=1):
        self.key = key
        self.count = count
        self.successor = None
        self.predecessor = None

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.key == other.key
        if isinstance(other, (int, float)):
            return self.key == other

        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.key < other.key
        if isinstance(other, (int, float)):
            return self.key < other
        raise TypeError(f'< not supported between instances of {self.__class__.__name__} and {type(other).__name__}')

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.key > other.key
        if isinstance(other, (int, float)):
            return self.key > other
        raise TypeError(f'< not supported between instances of {self.__class__.__name__} and {type(other).__name__}')

    def __repr__(self):
        return f'ASAElement(key={self.key}, count={self.count})'

    def link_after(self, elem, container):
        if elem.successor:
            self.successor = elem.successor
            self.successor.predecessor = self
        else:
            container.max = self

        self.predecessor = elem
        elem.successor = self

    def link_before(self, elem, container):
        if elem.predecessor:
            self.predecessor = elem.predecessor
            self.predecessor.successor = self
        else:
            container.min = self

        self.successor = elem
        elem.predecessor = self


class ASABaseContainer:
    def __init__(self):
        self.min = None
        self.max = None

    def add_first(self, key):
        new_elem = ASABaseElem(key)
        self.min = new_elem
        self.max = new_elem
        return new_elem

    def add_neighbour(self, key, element=None):
        new_elem = ASABaseElem(key)

        if element.key > new_elem.key:
            new_elem.link_before(element, self)
        else:
            new_elem.link_after(element, self)

        return new_elem

    def __iter__(self):
        current = self.min

        while current:
            yield current
            current = current.successor

    def __reversed__(self):
        current = self.max

        while current:
            yield current
            current = current.predecessor


class ASATreeNode:
    @classmethod
    def split_from_node(cls, node):
        median_key = node.keys[node.t]

        node_left = cls(leaf=node.leaf)
        node_left.keys = node.keys[:node.t]

        node_right = cls(leaf=node.leaf)
        node_right.keys = node.keys[node.t + 1:]

        if not node.leaf:
            node_left.children = node.children[:node.t + 1]
            node_right.children = node.children[node.t + 1:]

        return median_key, node_left, node_right

    def __init__(self, leaf=False, parent=None):
        self.t = 1
        self.keys = []
        self.children = []
        self.leaf = leaf
        self.parent = parent

    def add_key(self, item, asa_container):
        if isinstance(item, ASABaseElem):
            self._add_value_key(item.key, asa_container)

        elif isinstance(item, (int, float)):
            self._add_value_key(item, asa_container)

    def _add_value_key(self, value_key, asa_container):
        added = False

        if value_key in self.keys:
            ind = self.keys.index(value_key)
            self.keys[ind].count += 1
            return

        if not self.keys:
            new_asa_elem = asa_container.add_first(value_key)
            self.keys.append(new_asa_elem)
            return

        i = 0
        for i in range(len(self.keys)):
            if value_key < self.keys[i]:
                new_asa_elem = asa_container.add_neighbour(value_key, self.keys[i])

                self.keys.insert(i, new_asa_elem)
                added = True
                break

        if not added:
            new_asa_elem = asa_container.add_neighbour(value_key, self.keys[i])
            self.keys.append(new_asa_elem)

    @property
    def overflow(self):
        return len(self.keys) >= self.t * 2 + 1


class ASA:
    def __init__(self):
        self.root = None
        self.asa_container = ASABaseContainer()
        self.t = 1

    @property
    def min(self):
        return self.asa_container.min

    @property
    def max(self):
        return self.asa_container.max

    def insert(self, key):
        if self.root is None:
            self.root = ASATreeNode(True)
            self.root.add_key(key, self.asa_container)
            return

        self._insert(key, self.root)

    def _add_and_propagate(self, node, median_key, left_child, right_child):
        parent = node.parent
        if parent is None:
            new_root = ASATreeNode()
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

        parent.add_key(median_key, self.asa_container)

        if parent.overflow:
            median_key_p, left_node_p, right_node_p = ASATreeNode.split_from_node(parent)
            self._add_and_propagate(parent, median_key_p, left_node_p, right_node_p)

    def _insert(self, key, node):
        if node.leaf:
            node.add_key(key, self.asa_container)
            if node.overflow:
                median_key, left_node, right_node = ASATreeNode.split_from_node(node)
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
    asa = ASA()

    asa.insert(2)
    asa.insert(9)

    asa.insert(1)
    asa.insert(4)
    asa.insert(5)

    asa.insert(3)
    asa.insert(6)
    asa.insert(10)

    print('finihed')