"""Generic blocks extension."""
from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.treeprocessors import Treeprocessor
from markdown import util as mutil
from .. import util
import xml.etree.ElementTree as etree
import re
import yaml
import textwrap

# Fenced block placeholder for SuperFences
FENCED_BLOCK_RE = re.compile(
    r'^([\> ]*){}({}){}$'.format(
        mutil.HTML_PLACEHOLDER[0],
        mutil.HTML_PLACEHOLDER[1:-1] % r'([0-9]+)',
        mutil.HTML_PLACEHOLDER[-1]
    )
)

# Block start/end
RE_START = re.compile(
    r'(?:^|\n)[ ]{0,3}(/{3,})[ ]*([\w-]+)[ ]*(?:\|[ ]*(.*?)[ ]*)?(?:\n|$)'
)

RE_END = re.compile(
    r'(?m)(?:^|\n)[ ]{0,3}(/{3,})[ ]*(?:\n|$)'
)

# Frontmatter patterns
RE_YAML_START = re.compile(r'(?m)^[ ]{0,3}(-{3})[ ]*(?:\n|$)')

RE_YAML_END = re.compile(
    r'(?m)^[ ]{0,3}(-{3})[ ]*(?:\n|$)'
)

RE_INDENT_YAML_LINE = re.compile(r'(?m)^(?:[ ]{4,}(?!\s).*?(?:\n|$))+')


class BlockEntry:
    """Track Block entries."""

    def __init__(self, block, el, parent):
        """Block entry."""

        self.block = block
        self.el = el
        self.parent = parent
        self.hungry = False


def get_frontmatter(string):
    """
    Get frontmatter from string.

    YAML-ish key value pairs.
    """

    frontmatter = None

    try:
        frontmatter = yaml.safe_load(string)
        if not isinstance(frontmatter, dict):
            frontmatter = None
    except Exception:
        pass

    return frontmatter


def reindent(text, pos, level):
    """Reindent the code to where it is supposed to be."""

    indented = []
    for line in text.split('\n'):
        index = pos - level
        indented.append(line[index:])
    return indented


def unescape_markdown(md, blocks, is_raw):
    """Look for SuperFences code placeholders and other HTML stash placeholders and revert them back to plain text."""

    superfences = None
    try:
        from ..superfences import SuperFencesBlockPreprocessor
        processor = md.preprocessors['fenced_code_block']
        if isinstance(processor, SuperFencesBlockPreprocessor):
            superfences = processor.extension
    except Exception:
        pass

    new_blocks = []
    for block in blocks:
        new_lines = []
        for line in block.split('\n'):
            m = FENCED_BLOCK_RE.match(line)
            if m:
                key = m.group(2)

                # Extract SuperFences content
                indent_level = len(m.group(1))
                original = None
                if superfences is not None:
                    original, pos = superfences.stash.get(key, (None, None))
                    if original is not None:
                        code = reindent(original, pos, indent_level)
                        new_lines.extend(code)
                        superfences.stash.remove(key)

                # Extract other HTML stashed content
                if original is None and is_raw:
                    index = int(key.split(':')[1])
                    if index < len(md.htmlStash.rawHtmlBlocks):
                        original = md.htmlStash.rawHtmlBlocks[index]
                        if isinstance(original, etree.Element):
                            original = etree.tostring(original, encoding='unicode', method='html')
                        new_lines.append(original)

                # Couldn't find anything to extract
                if original is None:  # pragma: no cover
                    new_lines.append(line)
            else:
                new_lines.append(line)
        new_blocks.append('\n'.join(new_lines))

    return new_blocks


class BlocksTreeprocessor(Treeprocessor):
    """Blocks tree processor."""

    def __init__(self, md, blocks):
        """Initialize."""

        super().__init__(md)

        self.blocks = blocks

    def run(self, doc):
        """Update tab IDs."""

        while self.blocks.inline_stack:
            entry = self.blocks.inline_stack.pop(0)
            entry.block.on_inline_end(entry.el)


class BlocksProcessor(BlockProcessor):
    """Generic block processor."""

    def __init__(self, parser, md):
        """Initialization."""

        self.md = md

        # The Block classes indexable by name
        self.blocks = {}
        self.config = {}
        self.empty_tags = set(['hr'])
        self.block_level_tags = set(md.block_level_elements.copy())
        self.block_level_tags.add('html')

        # Block-level tags in which the content only gets span level parsing
        self.span_tags = set(
            ['address', 'dd', 'dt', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'legend', 'li', 'p', 'summary', 'td', 'th']
        )
        # Block-level tags which never get their content parsed.
        self.raw_tags = set(['canvas', 'math', 'option', 'pre', 'script', 'style', 'textarea'])
        # Block-level tags in which the content gets parsed as blocks
        self.block_tags = set(self.block_level_tags) - (self.span_tags | self.raw_tags | self.empty_tags)
        self.span_and_blocks_tags = self.block_tags | self.span_tags

        super().__init__(parser)

        # Persistent storage across a document for blocks
        self.trackers = {}
        # Currently queued up blocks
        self.stack = []
        # Blocks that should be processed after inline.
        self.inline_stack = []
        # When set, the assigned block is actively parsing blocks.
        self.working = None
        # Cached the found parent when testing
        # so we can quickly retrieve it when running
        self.cached_parent = None
        self.cached_block = None

        # Used during the alpha/beta stage
        self.start = RE_START
        self.end = RE_END
        self.yaml_line = RE_INDENT_YAML_LINE

    def register(self, b, config):
        """Register a block."""

        if b.NAME in self.blocks:
            raise ValueError('The block name {} is already registered!'.format(b.NAME))
        self.blocks[b.NAME] = b
        self.config[b.NAME] = config

    def test(self, parent, block):
        """Test to see if we should process the block."""

        # Are we hungry for more?
        if self.get_parent(parent) is not None:
            return True

        # Is this the start of a new block?
        m = self.start.search(block)
        if m:

            pre_text = block[:m.start()] if m.start() > 0 else None

            # Create a block object
            name = m.group(2).lower()
            if name in self.blocks:
                generic_block = self.blocks[name](len(m.group(1)), self.trackers[name], self.md, self.config[name])

                # Remove first line
                block = block[m.end():]

                # Get frontmatter and argument(s)
                options, the_rest = self.split_header(block, generic_block.length)
                arguments = m.group(3)

                # Options must be valid
                status = options is not None

                # Update the config for the Block
                if status:
                    status = generic_block.parse_config(arguments, **options)

                # Cache the found Block and any remaining content
                if status:
                    self.cached_block = (generic_block, the_rest)

                    # Any text before the block should get handled
                    if pre_text is not None:
                        self.parser.parseBlocks(parent, [pre_text])

                return status
        return False

    def _reset(self):
        """Reset."""

        self.stack.clear()
        self.inline_stack.clear()
        self.working = None
        self.trackers = {d: {} for d in self.blocks.keys()}

    def split_end(self, blocks, length):
        """Search for end and split the blocks while removing the end."""

        good = []
        bad = []
        end = False

        # Split on our end notation for the current Block
        for e, block in enumerate(blocks):

            # Find the end of the Block
            m = None
            for match in self.end.finditer(block):
                if len(match.group(1)) == length:
                    m = match
                    break

            # Separate everything from before the "end" and after
            if m:
                temp = block[:m.start(0)]
                if temp:
                    good.append(temp[:-1] if temp.endswith('\n') else temp)
                end = True

                # Since we found our end, everything after is unwanted
                temp = block[m.end(0):]
                if temp:
                    bad.append(temp)
                bad.extend(blocks[e + 1:])
                break
            else:
                # Gather blocks until we find our end
                good.append(block)

        # Augment the blocks
        blocks.clear()
        blocks.extend(bad)

        # Send back the new list of blocks to parse and note whether we found our end
        return good, end

    def split_header(self, block, length):
        """Split, YAML-ish header out."""

        # Search for end in first block
        m = None
        blocks = []
        for match in self.end.finditer(block):
            if len(match.group(1)) == length:
                m = match
                break

        # Move block ending to be parsed later
        if m:
            end = block[m.start(0):]
            blocks.insert(0, end)
            block = block[:m.start(0)]

        m = self.yaml_line.match(block)
        if m is not None:
            config = textwrap.dedent(m.group(0))
            blocks.insert(0, block[m.end():])
            if config.strip():
                return get_frontmatter(config), '\n'.join(blocks)

        blocks.insert(0, block)

        return {}, '\n'.join(blocks)

    def get_parent(self, parent):
        """Get parent."""

        # Returned the cached parent from our last attempt
        if self.cached_parent:
            parent = self.cached_parent
            self.cached_parent = None
            return parent

        temp = parent
        while temp:
            for entry in self.stack:
                if entry.hungry and entry.parent is temp:
                    self.cached_parent = temp
                    return temp
            if temp is not None:
                temp = self.lastChild(temp)
        return None

    def parse_blocks(self, blocks, entry):
        """Parse the blocks."""

        # Get the target element and parse

        for b in blocks:
            target = entry.block.on_add(entry.el)

            # The Block does not or no longer accepts more content
            if target is None:  # pragma: no cover
                break

            tag = target.tag
            mode = entry.block.on_markdown()
            if mode not in ('block', 'inline', 'raw'):
                mode = 'auto'
            is_block = mode == 'block' or (mode == 'auto' and tag in self.block_tags)
            is_atomic = mode == 'raw' or (mode == 'auto' and tag in self.raw_tags)

            # We should revert fenced code in spans or atomic tags.
            # Make sure atomic tags have content wrapped as `AtomicString`.
            if is_atomic or not is_block:
                child = list(target)[-1] if len(target) else None
                text = target.text if child is None else child.tail
                b = '\n\n'.join(unescape_markdown(self.md, [b], is_atomic))

                if text:
                    text += '\n\n' + b
                else:
                    text = b

                if child is None:
                    target.text = mutil.AtomicString(text) if is_atomic else text
                else:  # pragma: no cover
                    # TODO: We would need to build a special plugin to test this,
                    # as none of the default ones do this, but we have verified this
                    # locally. Once we've written a test, we can remove this.
                    child.tail = mutil.AtomicString(text) if is_atomic else text

            # Block tags should have content go through the normal block processor
            else:
                self.parser.state.set('blocks')
                working = self.working
                self.working = entry
                self.parser.parseChunk(target, b)
                self.parser.state.reset()
                self.working = working

    def run(self, parent, blocks):
        """Convert to details/summary block."""

        # Get the appropriate parent for this Block
        temp = self.get_parent(parent)
        if temp is not None:
            parent = temp

        # Did we find a new Block?
        if self.cached_block:
            # Get cached Block and reset the cache
            generic_block, block = self.cached_block
            self.cached_block = None

            # Discard first block as we've already processed what we need from it
            blocks.pop(0)
            if block:
                blocks.insert(0, block)

            # Ensure a "tight" parent list item is converted to "loose".
            if parent and parent.tag in ('li', 'dd'):  # pragma: no cover
                text = parent.text
                if parent.text:
                    parent.text = ''
                    p = etree.SubElement(parent, 'p')
                    p.text = text

            # Create the block element
            el = generic_block.create(parent)

            # Push a Block entry on the stack.
            self.stack.append(BlockEntry(generic_block, el, parent))

            # Split out blocks we care about
            ours, end = self.split_end(blocks, generic_block.length)

            # Parse the text blocks under the Block
            index = len(self.stack) - 1
            self.parse_blocks(ours, self.stack[-1])

            # Remove Block from the stack if we are at the end
            # or add it to the hungry list.
            if end:
                # Run the "on end" event
                generic_block.on_end(el)
                self.inline_stack.append(self.stack[index])
                del self.stack[index]
            else:
                self.stack[index].hungry = True

        else:
            for r in range(len(self.stack)):
                entry = self.stack[r]
                if entry.hungry and parent is entry.parent:
                    # Find and remove end from the blocks
                    ours, end = self.split_end(blocks, entry.block.length)

                    # Get the target element and parse
                    entry.hungry = False
                    self.parse_blocks(ours, entry)

                    # Clean up if we completed the Block
                    if end:
                        # Run "on end" event
                        entry.block.on_end(entry.el)
                        self.inline_stack.append(entry)
                        del self.stack[r]
                    else:
                        entry.hungry = True

                    break


class BlocksMgrExtension(Extension):
    """Add generic Blocks extension."""

    def extendMarkdown(self, md):
        """Add Blocks to Markdown instance."""

        md.registerExtension(self)
        util.escape_chars(md, ['/'])
        self.extension = BlocksProcessor(md.parser, md)
        # We want to be right after list indentations are processed
        md.parser.blockprocessors.register(self.extension, "blocks", 89.99)

        tree = BlocksTreeprocessor(md, self.extension)
        md.treeprocessors.register(tree, 'blocks_on_inline_end', 19.99)

    def reset(self):
        """Reset."""

        self.extension._reset()


class BlocksExtension(Extension):
    """Blocks Extension."""

    def register_block_mgr(self, md):
        """Add Blocks to Markdown instance."""

        if 'blocks' not in md.parser.blockprocessors:
            ext = BlocksMgrExtension()
            ext.extendMarkdown(md)
            mgr = ext.extension
        else:
            mgr = md.parser.blockprocessors['blocks']
        return mgr

    def extendMarkdown(self, md):
        """Extend markdown."""

        mgr = self.register_block_mgr(md)
        self.extendMarkdownBlocks(md, mgr)

    def extendMarkdownBlocks(self, md, block_mgr):
        """Extend Markdown blocks."""
