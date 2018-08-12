# str8
A `str8` is a bytes-like type that can only hold UTF-8 values, and can be used (almost) interchangeably as a `str`.

You wouldn't actually want to use this for anything serious. The point is to have something to test other implementations against, and to find edge cases I hadn't thought of.

The ultimate goal is to have a `strview` that's similar to `memoryview` but with `str` APIs instead of `bytes`. Imagine being able to, say, `mmap` a UTF-8 text file and do Unicode operations on it (the way you would in, say, Rust or Swift) without decoding the whole file. Unfortunately, with Python's APIs, this means that, e.g., `find` returns a character index, not a byte index, and you expect to be able to index or slice the string with it. It might also be fun to experiment with replacing `PyUnicode` with something that uses UTF-8 internally.

So, I needed to find out all the things like `str.__rmod__` and the differences between `str.__mod__` and `bytes.__mod__` and so on before I'd know what to test.

---

If you're curious about how you'd even do that UTF-8 with character-index APIs, here are some ideas:

 * Just build a 3.7-style `PyUnicode` on demand (and cache it).
 * Return indices that are a subclass of `int` that has the byte index crammed in.
 * Build something like a lazy skiplist for indexing long strings by character index instead of byte index. (Constructing `str` from 8-bit or even 32-bit strings already needs to scan the whole string in 3.3+ to decide how to store it, so we could build some or all of the index as we do that. A `find` would obviously fill in enough of the missing index to get to the position returned.)
 * Doesn't PyPy do something like this? Steal their ideas.
 
