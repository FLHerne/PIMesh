from collections import defaultdict, namedtuple


def reciprocal(tag):
    if tag[-3:] == " of":
        return tag[:-3]
    else:
        return tag + " of"

def header(text):
    return text + "\n" + "=" * len(text)


class Entity:
    def __init__(self, network, name):
        self._name = name
        self._network = network
        self._tags = defaultdict(list)

    @property
    def name(self):
        return self._name

    @property
    def links(self):
        links = []
        #TODO Messy...
        for tag in self:
            for target in tag[1]:
                links.append((tag[0], target))
        return tuple(links)

    def __str__(self):
        output = header(self._name) + "\n"
        for tag, targets in self._tags.items():
            for target in targets:
                output += tag + ": " + target.name + "\n"
        return output

    def __len__(self):
        return len(self._tags)

    def __getitem__(self, key):
        return tuple(self._tags[key])

    def __iter__(self):
        return iter(self._tags.items())

    def link(self, tag, target, mirror=False):
        target = self._resolve_target(target)
        if target in self._tags[tag]:
            return False
        self._tags[tag].append(target)
        if mirror:
            return True
        return target.link(reciprocal(tag), self, mirror=True)

    def unlink(self, tag, target, mirror=False):
        target = self._resolve_target(target)
        if target not in self._tags[tag]:
            return False
        self._tags[tag].remove(target)
        if not self._tags[tag]:
            del self._tags[tag]
            if not self._tags:
                del self._network[self._name]
        if mirror:
            return True
        return target.unlink(reciprocal(tag), self, mirror=True)

    def relink(self, tag, old_target, new_target):
        if not self.link(tag, new_target):
            return False
        if not self.unlink(tag, old_target):
            # Failed, remove new link.
            self.unlink(tag, new_target)
            return False
        return True

    def _resolve_target(self, target):
        if isinstance(target, Entity):
            return target
        else:
            return self._network[target]


class EntityNetwork(dict):
    @classmethod
    def from_file(cls, filename):
        """Load a network from a file (kinda fragile, also aargh)"""
        network = cls()
        with open(filename) as file:
            state = 'NONE'
            new_entity = None
            for line in file:
                line = line.strip()
                if state is 'NONE':
                    if not line:
                        continue
                    if ':' in line or ',' in line:
                        raise ValueError("No commas or colons!")
                    new_entity = network[line]
                    state = 'NAME'
                    continue
                if state is 'NAME':
                    if line == '=' * len(new_entity.name):
                        state = 'BODY'
                        continue
                    raise ValueError("No underline!")
                if state is 'BODY':
                    if not line:
                        state = 'NONE'
                        continue
                    tag, target, *rest = line.split(':')
                    if rest:
                        print("Warning: stuff ignored!")
                    new_entity.link(tag.strip(), target.strip())
            return network

    def to_file(self, filename):
        with open(filename, 'w') as file:
            for entity in self.values():
                file.write(str(entity) + "\n")

    def __missing__(self, key):
        self[key] = Entity(self, key)
        return self[key]
