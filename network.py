from collections import namedtuple
from enum import Enum


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
        if not all(prop.strip() for prop in link):
            raise ValueError("Names must not be empty or only whitespace.")
        if any(':' in prop for prop in link):
            raise ValueError("Colons are forbidden in tags or entity names.")

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

    def origin_counts(self):
        """Get namedtuple('origin', 'count'), reverse-sorted by count."""
        OC = Enum('OriginCount', ('count', 'name'))
        return sorted((OC(len(self[origin]), origin) for origin in self.origins),
                      reverse=True)

    # vvv Repetitive
    @property
    def origins(self):
        # Sorted already, because first element in link.
        return unique(link.origin for link in self)

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
    def from_file(cls, file):
        """Read a new network from `file`."""
        LineType = Enum('LineType', ('origin', 'underline', 'link'))
        expected = LineType.origin
        new_net = cls()
        current_origin = None

        for line_num, line in enumerate(file, start=1):
            def parse_error(message):
                raise ValueError("Line %d: %s" %(line_num, message))

            if expected == LineType.underline:
                if line.rstrip() != "=" * len(current_origin):
                    raise parse_error("missing underline.")
                expected = LineType.link
                continue

            if not line.strip():
                expected = LineType.origin
                continue

            parts = [part.strip() for part in line.split(":")]
            if expected == LineType.origin:
                if len(parts) > 1:
                    parse_error("colon in entity name.")
                current_origin = parts[0]
                expected = LineType.underline
                continue

            if expected == LineType.link:
                if not current_origin:
                    parse_error("link outside entity block.")
                if not 2 <= len(parts) <= 3:
                    parse_error("invalid link definition.")
                if not all(parts):
                    parse_error("blank tag or target.")
                if len(parts) == 2:  # Implicit inverse-tag
                    parts.append(cls.reciprocal(parts[0]))
                try:
                    new_net.addlink(current_origin, *parts)
                except ValueError: # Added as inverse of earlier link.
                    pass
        return new_net

    def to_file(self, file):
        """Save the network to a file."""
        file.truncate()
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
