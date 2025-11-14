class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False
        self.score = 0
        self.word = None

    def to_dict(self):
        return {
            "is_word": self.is_word,
            "score": self.score,
            "word": self.word,
            "children": {ch: node.to_dict() for ch, node in self.children.items()}
        }

    @staticmethod
    def from_dict(data):
        node = TrieNode()
        node.is_word = data["is_word"]
        node.score = data["score"]
        node.word = data["word"]
        node.children = {
            ch: TrieNode.from_dict(nd)
            for ch, nd in data["children"].items()
        }
        return node


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, score: int = 1):
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]

        node.is_word = True
        node.word = word
        node.score = score

    def _collect(self, node, results):
        if node.is_word:
            results.append((node.word, node.score))
        for child in node.children.values():
            self._collect(child, results)

    def autocomplete(self, prefix: str):
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]

        results = []
        self._collect(node, results)
        results.sort(key=lambda x: x[1], reverse=True)
        return [word for word, score in results[:20]]

    def to_dict(self):
        return self.root.to_dict()

    @staticmethod
    def from_dict(data):
        trie = Trie()
        trie.root = TrieNode.from_dict(data)
        return trie
