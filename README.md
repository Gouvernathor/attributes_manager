# renpy-AttributesManager

A framework to help handling layeredimage attributes (and image attributes in general, really, it's not at all specific to layeredimages) in Ren'Py. It's intended as a way to simplify the use of `config.adjust_attributes` and `config.default_attribute_callbacks`, by passing types easier to handle to the functions added to those variables, and by adding the possibility of having several adjusters for the same tag execute cumulatively.

The `attributes_manager_ren.py` file contains the code itself. The particulars are explained further down.

`memorizer_ren.py` contains an example of use of this system to make some attributes of a given tag persist through a hide/scene-show cycle.

`script.rpy` *(TBD)* contains an example as to how to use it with the assets of the `images/` folder, as well as a comparison with how the same thing would be done vanilla-style.

## How to use

The first thing this system (`attributes_manager_ren.py`) does is to slightly change how the `config.adjust_attributes` and `config.default_attribute_callbacks` variables work. You can still manually set individual keys to old-style functions, but you shouldn't change or assign the dict as a whole, as it may come after and erase changes done by this system. If you want to use this system in more creative ways, you may even want to set the config's dict to be a different type, as we'll see later.

### Decorators

The main tool of this package is `attributes_manager.adjust_decorator`, and its counterpart `attributes_manager.default_decorator`. As the name implies, they are decorators used in python blocks with the following syntax:

```py
@attributes_manager.adjust_decorator
def eileen_adjust_attributes(attrs):
    # do stuff
    return attrs

@attributes_manager.adjust_decorator()
def zoey_adjust_attributes(attrs):
    # do stuff
    return attrs

@attributes_manager.adjust_decorator("lucy")
def i_can_name_this_one_however_i_want(attrs):
    # do stuff
    return attrs

@attributes_manager.default_decorator
def eileen_default_attributes(attrs):
    # do stuff
    return rv
```

If the @ looks like it came from another world, I suggest you familiarize yourself with how decorators work in Python.

These decorators must be applied to functions not exactly similar to the ones normally added in adjust_attributes, but I'll come back to that in just a minute. Their main use is to register the decorated function as the adjuster or the defaulter (respectively) of the given tag. As shown above, you can either pass the tag as a string or pass no arguments and let the decorator infer the tag from the function name. In the latter case, it must be of the form `{tag}_adjust_attributes` or `{tag}_default_attributes`, respectively, otherwise the whole function name will be taken as the tag.

Note that you can cumulate the decorations in any order, since the decorators return the function as-is. At most one of the decorators should have no arguments, otherwise the function will be registered several times (see below how several adjusters can be added to the same tag).

As I said, the decorated functions are not exactly the same as the vanilla adjusters/defaulters. The vanilla ones are passed a tuple of strings whose first element is the image tag itself (useless). Instead, the decorated ones are passed an `attributes_manager.set` of `attributes_manager.attribute` objects, which will be described further down. The main difference is therefore the type of the sole passed parameter.

The return value of the decorated functions can be any iterable of strings or attributes.

### Cumulative adjusting and defaulting

There is another new thing you can do : cumulate several adjusters, or several defaulters, for the same tag. For example, you could have one adjuster implementing a behavior you want to apply on several characters, with each having a little something specific. You can do that now:

```py
@attributes_manager.adjust_decorator
def lucy(attrs):
    # do specific stuff prior to general behavior applying
    return attrs

@attributes_manager.adjust_decorator("lucy")
@attributes_manager.adjust_decorator("zoey")
@attributes_manager.adjust_decorator("eileen")
def general_behavior(attrs):
    # do stuff applying to all three
    return attrs

@attributes_manager.adjust_decorator
def eileen(attrs):
    # do specific stuff after general behavior applying
    return attrs
```

Lucy will have the first and second functions triggered as adjusters, eileen will have the second and the third, and zoey will have only the second. The order in which the adjusters are called is the order in which they are registered, as reflected in the comments. The order is greatly impacted by the init time the python block executes in, and by the name of the file, per renpy rules. And of course, all of this also applies to defaulters.

The attributes passed to the successive functions work the following way :

- for adjusters, the second function will be passed what the first one returned, and so on. No type conversion whatsoever will be performed between successive calls, both to enable creator freedom and for performance reasons ; so, if one of your adjusters returns a tuple of strings for example, the following ones better be able to handle that.
- for defaulters, the second function will be passed an `attributes_manager.set` containing the attributes that were passed to the first function as well as those returned by the first function. The third function will be passed the original attributes plus those returned by the first and second functions, and so on. This time, the type is guaranteed.

### Attribute

The `attributes_manager.attribute` class is basically a string with supplementary properties, namely `added` and `name`. In a nutshell:
- `att=attribute("hello")`
  * `att.name == "hello"` (this returns a pure string)
  * `att.added == True`
- `att=attribute("-hello")`
  * `att.name == "hello"`
  * `att.added == False`

The constructor also takes the `added` parameter which overrides the addedness of the attribute:
- `att=attribute("hello", added=False)`
  * `att.name == "hello"`
  * `att.added == False`
  * `att == attribute("-hello") == "-hello"`
- `att=attribute("-hello", added=True)`
  * `att.name == "hello"`
  * `att.added == True`
  * `att == attribute("hello") == "hello"`

The object usually behaves like a string (and allows the same operations) regarding indexing, slicing, substring tests, equality...

The type also adds three unary operators:
- `+att` returns the same attribute but with the addedness forced to True.
- `-att` returns the same attribute but with the addedness forced to False.
- `~att` returns the same attribute with the addedness inverted.

### Set

The `attributes_manager.set` class is a set of `attributes_manager.attribute` objects. It simplifies usual operations done on sets of attributes in adjusters or defaulters. Its constructor can take any iterable of strings or attributes, and will convert them accordingly. It provides the following methods:
- `add` and `update`, which in addition to converting their parameters to attributes, take the optional `added` keyword-only parameter to force those (only those passed) to the given addedness.
- the usual operations of the set type
- `find(name=None, added=None)`, which returns an arbitrary attribute in the set satisfying the provided conditions, or None if none is found.
  * `attributes_manager.set({"-hello", "-goodbye"}).find(name="hello")` returns `attribute("-hello")`
  * `attributes_manager.set({"hello", "goodbye"}).find(added=False)` returns `attribute("-goodbye")`
  * `attributes_manager.set({"-hello", "-goodbye"}).find(added=False)` returns either attribute object of the two, since the two match
  * `attributes_manager.set({"hello", "-goodbye"}).find(name="hello", added=False)` returns None
  * `attributes_manager.set({"hello", "goodbye"}).find(name="hell")` returns None - partial matches don't count
- `filter_or(*args)`, which returns a subset containing each attribute containing ANY of the substrings passed as arguments.
  * `attributes_manager.set({"hell", "hello", "love", "bite"}).filter_or("hell", "lo")` returns `attributes_manager.set({"hell", "hello", "love"})`
- `filter_and(*args)`, which returns a subset containing each attribute containing ALL of the substrings passed as arguments.
  * `attributes_manager.set({"hell", "hello", "love", "bite"}).filter_and("hell", "lo")` returns `attributes_manager.set({"hello"})`
- `filter_added(added)`, which returns a subset containing each attribute with the given addedness (True or False).

It also supports the `+`, `-` and `~` unaries, by returning a new set with the unaries applied to each attribute.

The find and filter methods in cunjunction with the attribute type are very useful to circumvent the problems posed by the potential prepended "-", and simplifies cases where you would have to check `(att[1:] if add[0] == "-" else att) == "uniform"`, `att.removeprefix("-") == "ribbon"` or `att in ("annoyed", "-annoyed")` in vanilla adjusters and defaulters.

### Callable lists (advanced)

(TBD)

## Terms of use

Use it freely in any project, just drop my name in the credits, and if you liked it you can add a link to this repo 🥰
