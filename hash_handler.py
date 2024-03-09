class HashHandler:
    def __init__(self):
        self._snap_hashes = []

    # todo: due to circular import, I can't import Snapshot (for typing),
    #       but i know there is a way to import just the type
    def is_it_really_new(self, snap):
        snap_hash = snap.hash
        is_it_new = snap_hash not in self._snap_hashes
        if is_it_new:
            self._snap_hashes.append(snap_hash)
        return is_it_new
