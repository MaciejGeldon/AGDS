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
        node_left = cls(leaf=node.leaf)
        node_right = cls(leaf=node.leaf)

        median_key = node.keys[node.t]

        node_left.keys = node.keys[:node.t]
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

    def _add_first(self, key, container):
        new_asa_elem = container.add_first(key)
        self.keys.append(new_asa_elem)

    def _increment_counter(self, key):
        ind = self.keys.index(key)
        self.keys[ind].count += 1

    def _add_new(self, key, cont):
        i = 0
        for i in range(len(self.keys)):
            if key < self.keys[i]:
                new_asa_elem = cont.add_neighbour(key, self.keys[i])
                self.keys.insert(i, new_asa_elem)
                return

        new_asa_elem = cont.add_neighbour(key, self.keys[i])
        self.keys.append(new_asa_elem)

    def _add_value_key(self, value_key, asa_container):
        if not self.keys:
            self._add_first(value_key, asa_container)

        elif value_key in self.keys:
            self._increment_counter(value_key)

        else:
            self._add_new(value_key, asa_container)

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

    def _create_new_root(self, median_key, left_child, right_child):
        new_root = ASATreeNode()
        new_root.keys.append(median_key)

        left_child.parent = new_root
        right_child.parent = new_root

        new_root.children.append(left_child)
        new_root.children.append(right_child)

        self.root = new_root

    def _get_next_node_index(self, key, node):
        ch_index = 0
        for ch_index, n_key in enumerate(node.keys):
            if key < n_key:
                return ch_index

        ch_index += 1
        return ch_index

    def _add_new_children_to_parent(self, node, left_child, right_child):
        parent = node.parent
        for index in range(len(parent.children)):
            if node == parent.children[index]:
                parent.children.pop(index)

                left_child.parent = parent
                right_child.parent = parent

                parent.children.insert(index, left_child)
                parent.children.insert(index + 1, right_child)

    def _add_and_propagate(self, node):
        median_key, left_child, right_child = ASATreeNode.split_from_node(node)
        parent = node.parent

        if parent is None:
            self._create_new_root(median_key, left_child, right_child)

        else:
            self._add_new_children_to_parent(node, left_child, right_child)
            parent.add_key(median_key, self.asa_container)

            if parent.overflow:
                self._add_and_propagate(parent)

    def _insert(self, key, node):
        if node.leaf:
            node.add_key(key, self.asa_container)
            if node.overflow:
                self._add_and_propagate(node)
        else:
            ch_index = self._get_next_node_index(key, node)
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