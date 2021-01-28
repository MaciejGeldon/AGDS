from decimal import Decimal

ACCEPTED_TYPES_FOR_COMPARISON = (int, float, str)


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
        if isinstance(other, ACCEPTED_TYPES_FOR_COMPARISON):
            return self.key == other

        return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.key < other.key
        if isinstance(other, ACCEPTED_TYPES_FOR_COMPARISON):
            return self.key < other
        raise TypeError(f'< not supported between instances of {self.__class__.__name__} and {type(other).__name__}')

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.key > other.key
        if isinstance(other, ACCEPTED_TYPES_FOR_COMPARISON):
            return self.key > other
        raise TypeError(f'< not supported between instances of {self.__class__.__name__} and {type(other).__name__}')

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return self.key >= other.key
        if isinstance(other, ACCEPTED_TYPES_FOR_COMPARISON):
            return self.key >= other
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
        if element.successor:
            element.successor.predecessor = element.predecessor
        if element.predecessor:
            element.predecessor.successor = element.successor


class SortedDQueue:
    def __init__(self):
        self.min = None
        self.max = None
        self.len = 0

    def add_first(self, key: (int, Decimal)):
        new_elem = ASABaseElem(key)
        self.min = new_elem
        self.max = new_elem
        self.len += 1
        return new_elem

    def add_neighbour(self, key, element):
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

    def __repr__(self):
        return str([repr(el) for el in self])


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

    def add_new(self, key: (int, float), asa_container: SortedDQueue):

        if not self.keys:
            new_elem = asa_container.add_first(key)
            self.keys.append(new_elem)
            return new_elem

        elif key in self.keys:
            ind = self.keys.index(key)
            self.keys[ind].count += 1
            return self.keys[ind]

        else:
            i = 0
            for i in range(len(self.keys)):
                if key < self.keys[i]:
                    added = asa_container.add_neighbour(key, self.keys[i])
                    self.keys.insert(i, added)
                    return added

            added = asa_container.add_neighbour(key, self.keys[i])
            self.keys.append(added)
            return added

    @property
    def overflow(self):
        return len(self.keys) >= self.t * 2 + 1


class ASA:
    def __init__(self):
        self.root = None
        self.sorted_d_queue = SortedDQueue()
        self.t = 1

    @property
    def min(self):
        return self.sorted_d_queue.min

    @property
    def max(self):
        return self.sorted_d_queue.max

    @property
    def sum(self):
        return sum(element.key * element.count for element in self.sorted_d_queue)

    @property
    def avr(self):
        if len(self.sorted_d_queue) == 0:
            return

        return self.sum / len(self.sorted_d_queue)

    @property
    def median(self):
        left, right = self.sorted_d_queue.min, self.sorted_d_queue.max

        if left is None and right is None:
            return None

        if left is right:
            return left.key

        return self._median(left.count - right.count, left, right)

    def _median(self, p, left, right):
        if p > 0:
            if left.successor is right:
                return left.key
            else:
                right = right.predecessor
                p -= right.count
                return self._median(p, left, right)

        elif p < 0:
            if left.successor is right:
                return right.key
            else:
                left = left.successor
                p += left.count
                return self._median(p, left, right)
        else:
            if left.successor is right:
                return (left.key + right.key) / 2
            else:
                if left.successor == right.predecessor:
                    return left.successor

                left = left.successor
                right = right.predecessor
                return self._median(left.count - right.count, left, right)

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
            return self.root.add_new(key, self.sorted_d_queue)

        return self._insert(key, self.root)

    def _insert(self, key, node):
        if node.leaf:
            added = node.add_new(key, self.sorted_d_queue)
            if node.overflow:
                self._split_and_propagate(node)
            return added
        elif key in node.keys:
            ind = node.keys.index(key)
            node.keys[ind].count += 1
            return node.keys[ind]
        else:
            ch_index = self._get_next_node_index(key, node)
            return self._insert(key, node.children[ch_index])

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
            return True

        elif node.leaf:
            if len(node.keys) > 1:
                node.keys.remove(key)
                self.sorted_d_queue.delete(key)
                return key
            else:
                node.keys.remove(key)
                empty_leaf = node
                self.sorted_d_queue.delete(key)
        else:
            empty_leaf = self._replace_with_leaf_candidate(key, node)
            # Case replace operation found leaf with more than one element and remove is finished
            if not empty_leaf:
                return True

        if empty_leaf:
            if self._try_siblings(empty_leaf):
                return True

            if self._parent_resolution(empty_leaf):
                return True

        collapsed_leaf = self._collapse(empty_leaf)
        if collapsed_leaf.parent is None:
            # we reach root nothing to do here
            return True

        self._rebalance(collapsed_leaf)
        return True

    def _replace_with_leaf_candidate(self, elem, elem_node):
        # assumption successor and predecessor of non leaf node is a leaf node
        predecessor, p_node = self.search(elem.predecessor)
        successor, s_node = self.search(elem.successor)

        def replace_from_predecessor():
            predecessor.successor = elem.successor
            elem.successor.predecessor = predecessor
            elem_node.keys[elem_node.keys.index(elem)] = predecessor
            p_node.keys.remove(predecessor)

        def replace_from_successor():
            successor.predecessor = elem.predecessor
            elem.predecessor.successor = successor
            elem_node.keys[elem_node.keys.index(elem)] = successor
            s_node.keys.remove(successor)

        if len(p_node.keys) > 1:
            replace_from_predecessor()
            return False

        if len(s_node.keys) > 1:
            replace_from_successor()
            return False

        p_node_par = p_node.parent
        s_node_par = s_node.parent

        if p_node_par is not elem_node:
            if p_node_par.keys >= s_node_par.keys:
                replace_from_predecessor()
                return p_node
            else:
                replace_from_successor()
                return s_node

        replace_from_predecessor()
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

        if candidate and abs(c_ind - empty_index) == 1:
            ch_draw_ind = int(bool(c_ind - empty_index < 0))
            parent.keys.insert(c_ind, candidate.keys.pop(ch_draw_ind))
            empty_leaf.keys.append(parent.keys.pop(empty_index))
            return True

        return False

    def _parent_resolution(self, e_leaf):
        parent = e_leaf.parent
        if len(parent.keys) == 2:
            e_ind = None
            for i in range(3):
                if parent.children[i] == e_leaf:
                    e_ind = i

            if e_ind == 1:
                parent.children[0].keys.append(parent.keys.pop(0))
            elif e_ind == 0:
                parent.children[1].keys.insert(0, parent.keys.pop(0))
            else:
                parent.children[1].keys.append(parent.keys.pop(1))

            parent.children.remove(e_leaf)
            return True
        return False

    def _collapse(self, e_leaf):
        parent = e_leaf.parent

        e_ind = None
        for i, ch in enumerate(parent.children):
            if parent.children[i] == e_leaf:
                e_ind = i

        sibling_index = 1 - e_ind
        if all([
                len(parent.keys) == 1,
                len(parent.children[sibling_index].keys) == 1
        ]):
            parent.keys.insert(sibling_index, parent.children[sibling_index].keys[0])
            parent.children = []
            parent.leaf = True
        return parent

    def _rebalance_from_sibling(self, c_subtree):
        parent = c_subtree.parent

        c_ind = None
        candidate = None
        empty_index = None

        for i, ch in enumerate(parent.children):
            if len(ch.keys) > 1 and c_subtree != ch:
                c_ind = i
                candidate = ch
            elif c_subtree == ch:
                empty_index = i

        if candidate and abs(c_ind - empty_index) == 1:
            ch_draw_ind = int(bool(c_ind - empty_index < 0))
            parent.keys.insert(c_ind, candidate.keys.pop(ch_draw_ind))

            new_leaf = ASATreeNode(parent=parent)
            new_leaf.keys.append(parent.keys.pop(empty_index))
            parent.children[empty_index] = new_leaf

            c_subtree.parent = new_leaf

            # left from empty
            if c_ind - empty_index < 0:
                new_leaf.children.append(candidate.children.pop(-1))
                new_leaf.children.append(c_subtree)

            # right from empty
            else:
                new_leaf.children.append(c_subtree)
                new_leaf.children.append(candidate.children.pop(0))

            return True

        # no candidate found
        return False

    def _join_with_sibling(self, c_subtree):
        parent = c_subtree.parent

        empty_candidate = {0: (1, 0), 1: (0, 0), 2: (1, 1)}
        reduced_index = None

        for i, ch in enumerate(parent.children):
            if c_subtree == ch:
                reduced_index = i

        c_sibling_ind, parent_key_ind = empty_candidate[reduced_index]
        ch_insert_ind = int(bool(reduced_index - c_sibling_ind > 0))
        closest_sibling = parent.children[c_sibling_ind]

        closest_sibling.keys.insert(ch_insert_ind, parent.keys.pop(parent_key_ind))
        if ch_insert_ind > 0:
            closest_sibling.children.append(c_subtree)
        else:
            closest_sibling.children.insert(0, c_subtree)

        if len(parent.keys) > 0:
            return True

        grandparent = parent.parent
        if grandparent is None:
            self.root = closest_sibling
            closest_sibling.parent = None
            c_subtree.parent = closest_sibling
            return False

        p_ind = None
        for i, par in enumerate(grandparent.children):
            if par is parent:
                p_ind = i

        grandparent.children[p_ind] = closest_sibling
        closest_sibling.parent = grandparent
        del parent

        return closest_sibling

    def _rebalance(self, collapsed_subtree):
        if self._rebalance_from_sibling(collapsed_subtree):
            return True

        # simple case when one rebalancing leeds to root change
        unbalanced_node = self._join_with_sibling(collapsed_subtree)
        if not unbalanced_node:
            return True

        self._rebalance(unbalanced_node)


if __name__ == '__main__':
    asa = ASA()

    in_1 = asa.insert(2)
    in_2 = asa.insert(9)

    in_3 = asa.insert(1)
    in_4 = asa.insert(4)
    in_5 = asa.insert(5)

    in_6 = asa.insert(3)
    in_7 = asa.insert(6)
    in_8 = asa.insert(10)

    print('finihed')
