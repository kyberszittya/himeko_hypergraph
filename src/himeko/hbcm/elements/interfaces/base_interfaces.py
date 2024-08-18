import abc


# Interface for compositable elements
# such as edges and vertices
class IComposable(abc.ABC):

    @abc.abstractmethod
    def add_element(self, element):
        raise NotImplementedError

    @abc.abstractmethod
    def remove_element(self, element):
        raise NotImplementedError

    @abc.abstractmethod
    def update_element(self, element):
        raise NotImplementedError

    @abc.abstractmethod
    def get_element(self, key):
        raise NotImplementedError


    @abc.abstractmethod
    def get_children(self, condition, depth: int = None):
        raise NotImplementedError

    @abc.abstractmethod
    def get_all_children(self, condition):
        raise NotImplementedError

    @abc.abstractmethod
    def get_leaf_elements(self):
        raise NotImplementedError

    @abc.abstractmethod
    def get_parent(self):
        pass

    @abc.abstractmethod
    def get_siblings(self, f):
        pass

