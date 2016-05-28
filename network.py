from collections import namedtuple


Link = namedtuple('Link', ('origin', 'tag', 'target', 'inverse_tag'))
Link.__new__.__defaults__ = (...,) * len(Link._fields)

def __link_inverse(self):
    """View a link from the other end (should be classmethod)"""
    return Link(self.target, self.inverse_tag, self.origin, self.tag)

Link.inverse = __link_inverse


def unique(sequence):
    """Remove duplicates, preserving order"""
    output = []
    for value in sequence:
        if value not in output:
            output.append(value)
    return output

class Network:
    @staticmethod
    def reciprocal(tag):
        if tag[-3:] == " of":
            return tag[:-3]
        else:
            return tag + " of"

    def __init__(self, links=[], filter=Link()):
        self._all_links = links
        self.filter = filter

    def __len__(self):
        return len(tuple(self._matching_links()))

    def __iter__(self):
        return iter(self._matching_links())

    def __getitem__(self, key):
        """Get subnetwork of links that match args"""
        if isinstance(key, int):
            return tuple(self._matching_links())[key]

        if not isinstance(key, tuple):
            key = (key,)  # Python doesn't tupleifiy a single argument.

        def combine_params(current, new):
            if new in (..., None):
                return current
            elif current not in (..., None, new):
                raise ValueError("Incompatible parameter")
            return new

        new_filter = Link(*map(combine_params, self.filter, key))

        return Network(self._all_links, new_filter)

    def addlink(self, *args):
        """Add link, as Link or separate args"""
        link = args[0] if len(args) == 1 else Link(*args)
        for n, implicit_prop in enumerate(self.filter):
            if link[n] == ...:
                link[n] = implicit_prop
        if ... in link:
            raise ValueError("Link not fully specified!")

        if link in self._all_links:
            raise ValueError("Link exists!")
        self._all_links += [link, link.inverse()]
        self._all_links.sort()

    def unlink(self, *args):
        """Remove all links in self[args]"""
        if len(args) == 1 and isinstance(args[0], int):
            args = args[0]
        to_unlink = self[args]
        if not len(to_unlink):
            raise ValueError("No such link(s)!")
        for link in tuple(to_unlink):  # Copy before removing elements
            try:
                self._all_links.remove(link)
                self._all_links.remove(link.inverse())
                self._all_links.sort()
            except ValueError:
                # Link was removed as inverse in previous loop
                continue

    def relink(self, old, new):
        """Replace old (Link) with new (Link)"""
        self.addlink(new)
        try:
            self.unlink(old)
        except ValueError:
            self.unlink(new)
            raise

    # vvv Repetitive
    @property
    def origins(self):
        return sorted(unique(link.origin for link in self))

    @property
    def tags(self):
        return sorted(unique(link.tag for link in self))

    @property
    def targets(self):
        return sorted(unique(link.target for link in self))

    @property
    def inverse_tags(self):
        return sorted(unique(link.inverse_tag for link in self))

    @classmethod
    def from_file(cls, filename):
        with open(filename) as file:
            new_net = cls()

            missing_inverses = 0
            state = 'NONE'
            new_origin = None
            for line in file:
                line = line.strip()
                if state is 'NONE':
                    if not line:
                        continue
                    if ':' in line or ',' in line:
                        raise ValueError("Comma/colons in entity name!")
                    new_origin = line
                    state = 'NAME'
                    continue
                if state is 'NAME':
                    if line == '=' * len(new_origin):
                        state = 'BODY'
                        continue
                    raise ValueError("Expected underline!")
                if state is 'BODY':
                    if not line:
                        state = 'NONE'
                        continue
                    tag, target, *rest = line.split(':')
                    inverse_tag = rest[0] if rest else cls.reciprocal(tag.strip())
                    try:
                        new_net.addlink(new_origin, tag.strip(),
                                     target.strip(), inverse_tag.strip())
                        missing_inverses += 1
                    except ValueError:
                        missing_inverses -= 1
            if missing_inverses:
                # Who cares?
                pass
            return new_net

    def to_file(self, filename):
        with open(filename, 'w') as file:
            for origin in self.origins:
                file.write(origin + "\n")
                file.write("=" * len(origin) + "\n")
                for link in self[origin]:
                    outline = "%s: %s" %(link.tag, link.target)
                    if link.inverse_tag != Network.reciprocal(link.tag):
                        outline += " :%s" %(link.inverse_tag)
                    file.write(outline + "\n")
                file.write("\n")

    def _matching_links(self):
        def matches(link):
            return all(filter_param in (link_param, ...) for
                       filter_param, link_param in zip(self.filter, link))

        return filter(matches, self._all_links)
