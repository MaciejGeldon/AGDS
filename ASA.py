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
        self.len = 0

    def add_first(self, key: (int, float)):
        new_elem = ASABaseElem(key)
        self.min = new_elem
        self.max = new_elem
        self.len += 1
        return new_elem

    def add_neighbour(self, key, element=None):
        new_elem = ASABaseElem(key)
        self.len += 1

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

    def __len__(self):
        return self.len


class ASATreeNode:
    @classmethod
    def split_from_node(cls, node):
        node_left = cls(leaf=node.leaf)
        node_right = cls(leaf=node.leaf)

        promoted_element = node.keys[node.t]

        node_left.keys = node.keys[:node.t]
        node_right.keys = node.keys[node.t + 1:]

        if not node.leaf:
            node_left.children = node.children[:node.t + 1]
            node_right.children = node.children[node.t + 1:]

        return promoted_element, node_left, node_right

    def __init__(self, leaf=False, parent=None):
        self.t = 1
        self.keys = []
        self.children = []
        self.leaf = leaf
        self.parent = parent

    def add_promoted(self, promoted_elem: ASABaseElem):
        for i in range(len(self.keys)):
            if promoted_elem < self.keys[i]:
                self.keys.insert(i, promoted_elem)
                return

        self.keys.append(promoted_elem)

    def _add_first(self, key: (int, float), container: ASABaseContainer):
        new_asa_elem = container.add_first(key)
        self.keys.append(new_asa_elem)

    def _increment_counter(self, key: (int, float)):
        ind = self.keys.index(key)
        self.keys[ind].count += 1

    def _add_new(self, key: (int, float), cont: ASABaseContainer):
        i = 0
        for i in range(len(self.keys)):
            if key < self.keys[i]:
                new_asa_elem = cont.add_neighbour(key, self.keys[i])
                self.keys.insert(i, new_asa_elem)
                return

        new_asa_elem = cont.add_neighbour(key, self.keys[i])
        self.keys.append(new_asa_elem)

    def add_new(self, key: (int, float), asa_container: ASABaseContainer):
        if not self.keys:
            self._add_first(key, asa_container)

        elif key in self.keys:
            self._increment_counter(key)

        else:
            self._add_new(key, asa_container)

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

    @property
    def sum(self):
        return sum(element.key * element.count for element in self.asa_container)

    @property
    def avr(self):
        if len(self.asa_container) == 0:
            return

        return self.sum / len(self.asa_container)

    @property
    def median(self):
        l, r = self.asa_container.min, self.asa_container.max

        if l is r:
            return l.key

        return self._median([l.count, r.count], l, r)

    def _median(self, p, l, r):
        if p[0] > p[1]:
            if l.successor is r:
                return l.key
            else:
                r = r.predecessor
                p[1] += r.count
                return self._median(p, l, r)

        elif p[0] < p[1]:
            if l.successor is r:
                return p.c
            else:
                l = l.successor
                p[0] += l.c
                return self._median(p, l, r)
        else:
            if l.successor is r:
                return (l.key + r.key) / 2
            else:
                l = l.successor
                r = r.predecessor
                return self._median((l.count, r.count), l, r)

    def insert(self, key):
        if self.root is None:
            self.root = ASATreeNode(True)
            self.root.add_new(key, self.asa_container)
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

    def _link_children_to_parent(self, node, left_child, right_child):
        parent = node.parent
        for index in range(len(parent.children)):
            if node == parent.children[index]:
                parent.children.pop(index)

                left_child.parent = parent
                right_child.parent = parent

                parent.children.insert(index, left_child)
                parent.children.insert(index + 1, right_child)

    def _split_and_propagate(self, node):
        promoted_element, left_child, right_child = ASATreeNode.split_from_node(node)
        parent = node.parent

        if parent is None:
            self._create_new_root(promoted_element, left_child, right_child)

        else:
            self._link_children_to_parent(node, left_child, right_child)
            parent.add_promoted(promoted_element)

            if parent.overflow:
                self._split_and_propagate(parent)

    def _insert(self, key, node):
        if node.leaf:
            node.add_new(key, self.asa_container)
            if node.overflow:
                self._split_and_propagate(node)
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
    asa.median
