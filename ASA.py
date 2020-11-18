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

    def delete(self, element):
        if element.successor and element.predecessor:
            element.predecessor.successor = element.successor
            element.successor.predecessor = element.predecessor

        elif element.successor:
            element.successor.predecessor = element.predecessor

        else:
            element.predecessor.successor = element.successor


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

    def delete(self, element):
        if element == self.max:
            self.max = element.predecessor
        elif element == self.min:
            self.min = element.successor

        element.delete(element)

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
            for ch_l in node_left.children:
                ch_l.parent = node_left

            node_right.children = node.children[node.t + 1:]
            for ch_r in node_right.children:
                ch_r.parent = node_right

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
                if l.successor == r.predecessor:
                    return l.successor

                l = l.successor
                r = r.predecessor
                return self._median((l.count, r.count), l, r)

    def search(self, key):
        if self.root is None:
            return False, self.root

        return self._search(key, self.root)

    def _search(self, key, node):
        if node.leaf:
            for k in node.keys:
                if k == key:
                    return k, node
            return False, None

        for i, k in enumerate(node.keys):
            if k == key:
                return k, node
            elif key < k:
                return self._search(key, node.children[i])

        return self._search(key, node.children[-1])

    def insert(self, key):
        if self.root is None:
            self.root = ASATreeNode(True)
            self.root.add_new(key, self.asa_container)
            return

        self._insert(key, self.root)

    def _insert(self, key, node):
        if node.leaf:
            node.add_new(key, self.asa_container)
            if node.overflow:
                self._split_and_propagate(node)
        else:
            ch_index = self._get_next_node_index(key, node)
            self._insert(key, node.children[ch_index])

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

    def delete(self, key):
        empty_leaf = False

        if self.root is None:
            return False

        key, node = self.search(key)
        if key is False:
            return False

        elif key.count > 1:
            key.count -= 1
            return key

        elif node.leaf:
            if len(node.keys) > 1:
                node.keys.remove(key)
                self.asa_container.delete(key)
                return key
            else:
                node.keys.remove(key)
                empty_leaf = node
        else:
            empty_leaf = self._replace_with_leaf_candidate(key, node)
            if not empty_leaf:
                return False

        if empty_leaf:
            sibling_shift_resolution = self._try_siblings(empty_leaf)
            if isinstance(sibling_shift_resolution, ASATreeNode):
                return sibling_shift_resolution

        # here I need to implement steps 6,7,8,9 from delete

    # this needs better algorithm 
    def _replace_with_leaf_candidate(self, elem, elem_node):
        predecessor, p_node = self.search(elem.predecessor)
        successor, s_node = self.search(elem.successor)

        if len(p_node.keys) > 1:
            predecessor.successor = elem.successor
            elem.successor.predecessor = predecessor
            elem_node.keys.insert(elem_node.keys.index(elem), predecessor)
            elem_node.keys.remove(elem)
            p_node.keys.remove(predecessor)
            return False

        if len(s_node.keys) > 1:
            successor.predecessor = elem.predecessor
            elem.predecessor.successor = successor
            elem_node.keys.insert(elem_node.keys.index(elem), successor)
            s_node.keys.remove(successor)
            elem_node.keys.remove(elem)
            return False

        p_node_par = p_node.parent
        s_node_par = s_node.parent

        if p_node_par is not elem_node:
            if p_node_par.keys >= s_node_par.keys:
                predecessor.successor = elem.successor
                elem.successor.predecessor = predecessor
                elem_node.insert(elem_node.keys.index(elem), predecessor)
                elem_node.keys.remove(elem)
                p_node.remove(predecessor)
                return p_node
            else:
                successor.predecessor = elem.predecessor
                elem.predecessor.successor = successor
                elem_node.insert(elem_node.keys.index(elem), predecessor)
                s_node.keys.remove(successor)
                elem_node.keys.remove(elem)
                return s_node

        predecessor.successor = elem.successor
        elem.successor.predecessor = predecessor
        elem_node.insert(elem_node.keys.index(elem), predecessor)
        elem_node.keys.remove(elem)
        p_node.remove(predecessor)
        return p_node

    def _try_siblings(self, empty_leaf):
        parent = empty_leaf.parent

        c_ind = None
        candidate = None
        empty_index = None

        for i, ch in enumerate(parent.children):
            if len(ch.keys) > 1:
                c_ind = i
                candidate = ch
            elif empty_leaf == ch:
                empty_index = i

        if abs(c_ind - empty_index) == 1:
            ch_draw_ind = int(bool(c_ind - empty_index < 0))
            parent.keys.insert(c_ind, candidate.keys.pop(ch_draw_ind))
            empty_leaf.keys.append(parent.keys.pop(empty_index))
            return empty_leaf

        return False


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
