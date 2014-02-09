from collections import OrderedDict
from functools import partial


class VirtualDir(object):
    def __init__(self, dir_list, name, identifier, message_count):
        self._dir_list = dir_list
        self._name = name
        self._identifier = identifier
        self._message_count = message_count

    def _update(self, value, key=None):
        if key not in ("name", "message_count", "identifier"):
            raise AttributeError(key)
        setattr(self, "_%s" % key, value)
        self._dir_list.update()

    def _get(self, key):
        if key not in ("name", "message_count", "identifier"):
            raise AttributeError(key)
        return getattr(self, "_%s" % key)

    name = property(partial(_get, key="name"), partial(_update, key="name"))
    identifier = property(partial(_get, key="identifier"), partial(_update, key="identifier"))
    message_count = property(partial(_get, key="message_count"), partial(_update, key="message_count"))


class DirList(object):
    vdir_template = 'in:Inbox;0|sent:Sent Items;0'

    def __init__(self, member_extra):
        self._member_extra = member_extra
        self._vdirs = OrderedDict()
        self._max_custom = 2

        if member_extra.vdirs is None or not len(member_extra.vdirs):
            member_extra.vdirs = self.vdir_template

        for dir_entry in member_extra.vdirs.split("|"):
            (identifier, tail) = dir_entry.split(":", 1)
            message_count = None
            if ";" in tail:
                tail_splits = tail.split(";")
                name = ";".join(tail_splits[:-1])
                message_count = int(tail_splits[-1])
            else:
                name = tail

            if identifier.startswith("dir_"):
                number = int(identifier.split("_")[-1])
                self._max_custom = max(number, self._max_custom)

            vdir = VirtualDir(self, name, identifier, message_count)
            self._vdirs[identifier] = vdir

    def __getitem__(self, item):
        return self._vdirs[item]

    def __contains__(self, item):
        return item in self._vdirs

    @property
    def as_list(self):
        return list(self._vdirs.values())

    def add_dir(self, name):
        self._max_custom += 1
        identifier = "dir_%d" % self._max_custom
        vdir = VirtualDir(self, name, identifier, None)
        self._vdirs[identifier] = vdir

    def update(self):
        dir_parts = []
        for vdir in self._vdirs:
            part = "%s:%s" % (vdir.identifier, vdir.name)
            if vdir.message_count is not None:
                part = "%s;%d" % (part, vdir.message_count)
            dir_parts.append(part)
        self._member_extra = "|".join(dir_parts)