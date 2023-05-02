init python:
    class memorizer:
        def __init__(self, store_name, *to_memorize):
            self.to_memorize = attributes_manager.set(to_memorize)
            self.store_name = store_name

        def adjust(self, attrs):
            if not renpy.predicting():
                inter = attrs.intersection(self.to_memorize)
                memo = getattr(store, self.store_name)
                for attr in memo.copy():
                    if -attr in inter:
                        memo.remove(attr)
                memo.update(inter.filter_added(True))
                setattr(store, self.store_name, memo)
            return attrs

        def default(self, attrs):
            return getattr(store, self.store_name)

default cho_memorized = set()
define cho_memorizer = memorizer("cho_memorized", "brows_angry", "brows_base", "brows_raised", "brows_worried")

define config.adjust_attributes["cho"].append(cho_memorizer.adjust)
define config.default_attribute_callbacks["cho"].append(cho_memorizer.default)

# vanilla version
# init python:
#     class memorizer:
#         def __init__(self, store_name, *to_memorize):
#             self.to_memorize = set(to_memorize)
#             self.store_name = store_name

#         def adjust(self, name):
#             atts = set(name[1:])
#             if not renpy.predicting():
#                 inter = atts.intersection(self.to_memorize)
#                 memo = getattr(store, self.store_name)
#                 print(f"{inter=}")
#                 for attr in memo.copy():
#                     if "-"+attr in inter:
#                         memo.remove(attr)
#                 memo.update(a for a in inter if a[0] != "-")
#                 setattr(store, self.store_name, memo)
#                 print(f"memorized {memo=}")
#             return name

#         def default(self, name):
#             return getattr(store, self.store_name)

#     # default
#     cho_memorized = set()

#     # define / python hide
#     cho_memorizer = memorizer("cho_memorized", "brows_angry", "brows_base", "brows_raised", "brows_worried")

#     config.adjust_attributes["cho"] = cho_memorizer.adjust
#     config.default_attribute_callbacks["cho"] = cho_memorizer.default
