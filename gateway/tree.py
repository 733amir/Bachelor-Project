class Tree:
    def __init__(self, id):
        self.__root = {id: {}}

    def add(self, pid, id):
        if not self.__add(self.__root, pid, id):
            raise IdentificationError('Parent ID Error. No node with ID: {} found.'.format(pid))

    def __add(self, collection, parent, child):
        for node in collection:
            if node == parent:
                if child not in collection[parent]:
                    collection[parent][child] = {}
                return True
            if self.__add(collection[node], parent, child):
                return True
        return False

    def remove(self, id):
        if not self.__remove(self.__root, id):
            raise IdentificationError('Node ID Error. No node with ID: {} found.'.format(id))

    def __remove(self, collection, parent):
        for node in collection:
            if node == parent:
                del collection[parent]
                return True
            if self.__remove(collection[node], parent):
                return True
        return False

    def get(self, id):
        result = self.__get(self.__root, id)
        if result is None:
            raise IdentificationError('Node ID Error. No node with ID: {} found.'.format(id))

    def __get(self, collection, parent):
        for node in collection:
            if node == parent:
                return collection[parent]
            result = self.__get(collection[node], parent)
            if result is not None:
                return result
        return None

    def __str__(self):
        # return self.__print(self.__root)
        return str(self.__root)

    def __print(self, collection, level=0):
        result = []
        for node in collection:
            result.append("{}{}\n{}".format('|-'*level, node, self.__print(collection[node], level+1)))
        return ''.join(result)

    def to_dict(self):
        return self.__root


class IdentificationError(Exception):
    def __init__(self, arg):
        self.arg = arg


if __name__ == '__main__':
    t = Tree(1)
    t.add(1, 2)
    t.add(2, 3)
    t.add(1, 4)
    t.add(3, 5)
    t.add(4, 6)
    t.add(4, 7)
    t.add(2, 8)
    print(t)
