class Node:
    def __init__(self, hash_key):
        self._hash_key = hash_key

    def __hash__(self):
        return hash(self._hash_key)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._hash_key == other._hash_key
        if isinstance(other, str):
            return self._hash_key == other
        raise NotImplementedError(f'__eq__ not implemented for {self}, {other}')

    def __repr__(self):
        return f'Node({self._hash_key})'


class ValueNode(Node):
    def __init__(self, parameter, value, count=1):
        super().__init__(f'{parameter}:{value}')
        self.parameter = parameter
        self.value = value
        self.count = count

    def __repr__(self):
        return f'ValueNode({self.parameter}, {self.value}, {self.count})'


class AGDS:
    def __init__(self):
        self._graph_dict = {}

    def add_vertex(self, vertex):
        if vertex not in self._graph_dict:
            self._graph_dict[vertex] = []

    def add_edge(self, v1, v2, symmetric=False) -> None:
        connections = [[v1, v2]]

        if symmetric:
            connections += [(v2, v1)]

        for v1, v2 in connections:
            if self._graph_dict[v1]:
                self._graph_dict[v1].append(v2)
            else:
                self._graph_dict[v1] = [v2]

    def add_row(self, row, attributes):
        for param in attributes:
            val = getattr(row, param)

            value_node = ValueNode(param, val)
            if value_node in self._graph_dict:
                self._graph_dict[value_node].count += 1

            else:
                self._graph_dict[value_node] = value_node
                self._graph_dict[param].append(value_node)

    def build_from_pandas(self, pd_dataframe):
        attributes_node = Node('attributes')
        self.add_vertex(attributes_node)

        attrs = [a for a in pd_dataframe.columns]

        for attr in attrs:
            attr_node = Node(attr)
            self.add_vertex(attr_node)
            self.add_edge(attributes_node, attr_node, symmetric=True)

        for row in pd_dataframe.itertuples():
            self.add_row(row, attrs)


if __name__ == '__main__':
    import pandas as pd

    data = pd.read_csv("iris.csv")
    test_rows = data[0:5]
    agds = AGDS()
    agds.build_from_pandas(test_rows)

    print('debugger checkpoint')
