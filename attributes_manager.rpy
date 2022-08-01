init python in attributes_manager:
    class attribute(str):
        """
        Represents an attribute passed to the attributes_manager functions.

        In a nutshell :
        att=attribute("hello")
            att.name=="hello", att.added==True
        att=attribute("-hello")
            att.name=="hello", att.added==False

        If given, the `added` argument of the constructor overrides the added-ness.
        Examples :
        att=attribute("hello", added=False)
            att.name=="hello", att.added==False, att==attribute("-hello"), str(att)=="-hello"
        att=attribute("-hello", added=True)
            att.name=="hello", att.added==True,  att==attribute("hello"),  str(att)=="hello"

        attribute is a subclass of str and supports operations with strings, usually returning strings.
        In particular, `"hello" in attribute("hello")`, `"hello" in attribute("-hello")`,
        `"-hell" in attribute("-hello")` and `attribute("hello", added=False)[0] == "-"` all return True.
        """
        __slots__ = ()

        def __new__(clss, name, added=None):
            if added is not None:
                if (not added) and (name[0] != "-"):
                    name = "-"+name
                elif added:
                    name = name.removeprefix("-")
            return super(attribute, clss).__new__(clss, name)

        @property
        def name(self):
            """
            Returns the attribute as a string, without the prepended minus sign.
            """
            return self.removeprefix("-")

        @property
        def added(self):
            """
            Returns a boolean representing the minus sign in front of attributes to remove them :
            if added is True, the minus sign wasn't there.
            """
            return self[0] != '-'

        def __repr__(self):
            return "attribute({})".format(super().__repr__())

    class set(renpy.store.set):
        __slots__ = ()

        def __init__(self, iterable=()):
            super().__init__(attribute(el) for el in iterable)

        def add(self, value, **kwargs):
            return super().add(attribute(value, **kwargs))

        def find(self, name=None, added=None):
            """
            Returns an element of the set satisfying the conditions given in arguments, or None.

            attributes_manager.set({"-hello", "-goodbye"}).find(name="hello")
                returns attribute("-hello")
            attributes_manager.set({"hello", "-goodbye"}).find(added=False)
                returns attribute("-goodbye")
            attributes_manager.set({"-hello", "-goodbye"}).find(added=False)
                returns either one as an attribute object
            attributes_manager.set({"hello", "-goodbye"}).find(name="hello", added=False)
                returns None
            attributes_manager.set({"hello", "goodbye"}).find(name="hell")
                returns None
            """
            if name is None and added is None:
                raise ValueError("One of name or added must be given.")
            for att in self:
                if ((name is None) or (att.name == name)) and ((added is None) or (att.added == added)):
                    return att
            return None

        def filter_or(self, *args):
            """
            Returns a subset of each attribute containing ANY OF the substrings passed as arguments.

            attributes_manager.set({"hell", "hello", "love", "bite"}).filter_or("hell", "lo")
                returns attributes_manager.set({"hell", "hello", "love"})
            """
            rv = type(self)()
            for att in self:
                for substring in args:
                    if substring in str(att):
                        rv.add(att)
            return rv

        def filter_and(self, *args):
            """
            Returns a subset of each attribute containing EACH OF the substrings passed as arguments.

            attributes_manager.set({"hell", "hello", "love", "bite"}).filter_and("hell", "lo")
                returns attributes_manager.set({"hello"})
            """
            rv = type(self)()
            for att in self:
                for substring in args:
                    if substring not in str(att):
                        break
                else:
                    rv.add(att)
            return rv

        def __repr__(self):
            return type(self).__module__ + "." + super().__repr__()

init python hide:
    """
    Some little magic to make our set's inerited methods return objects of the proper type.
    """
    def _wrapper(func):
        def internal(self, *args):
            args = (type(self)(arg) for arg in args)
            return type(self)(func(self, *args))
        return internal
    for methname in ("__sub__", "__isub__", "__rsub__",
                     "__xor__", "__ixor__", "__rxor__",
                     "__and__", "__iand__", "__rand__",
                     "__or__", "__ior__", "__ror__",
                     "copy", "difference", "intersection", "symmetric_difference", "union"):
        setattr(attributes_manager.set, methname, _wrapper(getattr(renpy.store.set, methname)))

init python in attributes_manager:
    class adjust_decorator(python_object):
        """
        This is a decorator for the declaration of adjust_attributes functions.

        The function being decorated will be passed a single argument :
        an `attributes_manager.set` of `attributes_manager.attribute` objects.
        The first attribute, which is the tag of the shown image, is not a part of the set.
        The function being decorated must return an iterable (set, list, tuple... attributes_manager.set)
        of string objects (or subclasses of string, such as attributes_manager.attribute).

        If a `name` is provided to the decorator, the decorated version of the function
        will be stored in `config.adjust_attributes[name]`.
        If no `name` parameter is passed, if the name of the function is "(something)_adjust_attributes",
        that `something` is taken as the name.
        Otherwise, the decorator doesn't store the function anywhere.
        """

        __slots__ = "name"
        suffix = "_adjust_attributes"
        store = renpy.store.config.adjust_attributes

        def __init__(self, name=None):
            self.name = name

        def __call__(self, func):
            funcname = self.name

            def rf(name):
                aaa_set = set(attribute(att) for att in name[1:])
                rv = func(aaa_set)
                rv = tuple(str(el) for el in rv) # very important, only return native types !
                return (name[0],)+tuple(rv)

            if funcname is None:
                sfx = self.suffix
                if func.__name__.endswith(sfx):
                    funcname = func.__name__.removesuffix(sfx)

            if funcname is not None:
                self.store[funcname] = rf
            return rf

    class default_decorator(adjust_decorator):
        """
        This is a decorator for the declaration of default_attribute_callbacks functions.

        It works the same as adjust_decorator, except that the store is config.default_attribute_callbacks,
        and the recognized template is "(something)_default_attributes"
        """

        __slots__ = ()
        suffix = "_default_attributes"
        store = renpy.store.config.default_attribute_callbacks
