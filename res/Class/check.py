class check:
    def is_startswith(self, index: str, key: str,
        _return_idx=True, _raise=True) -> bool:

        if index.startswith(key):
            if _return_idx is True:
                return index
            return True

        if _raise is True:
            raise TypeError
        return False
