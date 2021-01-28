from ASA.ASA_tree_and_d_queue import ASA


# This will be dynamically created to add column information
class RowNode:
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


class AGDS:
    def __init__(self):
        self.attributes = {}
        self.rows = {}

    def build_from_pandas(self, pd_dataframe):
        columns = pd_dataframe.columns
        for ind, col in enumerate(columns):
            self.attributes[col] = ASA()

            for index, val in enumerate(pd_dataframe[col]):
                inserted = self.attributes[col].insert(val)

                if f'O{index}' not in self.rows:
                    rn = RowNode(f'O{index}')
                    setattr(rn, col, inserted)
                    self.rows[f'O{index}'] = rn
                else:
                    rn = self.rows[f'O{index}']
                    if not hasattr(rn, col):
                        setattr(rn, col, inserted)
                        self.rows[f'O{index}'] = rn

                if not hasattr(inserted, f'O{index}'):
                    setattr(inserted, f'O{index}', self.rows[f'O{index}'])

    def __str__(self):
        return f'attributes = {self.attributes} \n rows: {self.rows}'


if __name__ == '__main__':
    import pandas as pd

    data = pd.read_csv("../datasets/iris.csv")
    test_rows = data[0:10]
    agds = AGDS()
    agds.build_from_pandas(test_rows)
    print('Now what')
    print('glourious_object')

