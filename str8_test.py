from str8 import Str8, ByteString
import sys
import unittest

class TestString(unittest.TestCase):
    abc = 'áβç'
    abc8 = Str8(abc)
    abcb = abc.encode()

    def test_construct(self):
        self.assertEqual(Str8(2)._str, '2')
        self.assertEqual(Str8(self.abc)._str, self.abc)
        self.assertEqual(Str8(self.abc.encode())._str, self.abc)
        self.assertIsInstance(self.abc8, Str8)
        self.assertIsInstance(self.abc8, bytes)
        self.assertIsInstance(self.abc8, ByteString)
    def test_conv(self):
        self.assertEqual(int(Str8(2)), 2)
    def test_repr(self):
        self.assertEqual(repr(self.abc8), repr(self.abc))
    def test_str(self):
        self.assertEqual(str(self.abc8), str(self.abc))
    def test_compare(self):
        self.assertEqual(self.abc8, self.abc)
        self.assertEqual(self.abc8, self.abcb)
        # TODO: < comparison for bytes vs. str?
    def test_bytes(self):
        self.assertEqual(bytes(self.abc8), self.abcb)
    def test_b(self):
        self.assertEqual(self.abc8.b, self.abcb)
        self.assertIsInstance(self.abc8.b, bytes)
        self.assertEqual(self.abc8.b[2:4].decode(), self.abc8[1])
    def test_s(self):
        self.assertEqual(self.abc8.s, self.abc)
        self.assertIsInstance(self.abc8.s, str)
    def test_encode(self):
        self.assertEqual(self.abc8.encode(), self.abcb)
        self.assertEqual(Str8('\xe1\xe7').encode('latin-1'), b'\xe1\xe7')
        self.assertEqual(self.abc.encode('latin-1', 'replace'), b'\xe1?\xe7')
        with self.assertRaises(UnicodeEncodeError):
            self.abc8.encode('latin-1')
    def test_decode(self):
        self.assertEqual(self.abc8.decode(), self.abc8)
        with self.assertRaises(TypeError):
            self.abc8.decode('latin-1')
    def test_hex(self):
        self.assertEqual(self.abc8.hex(), 'c3a1ceb2c3a7')
        self.assertEqual(Str8.fromhex('C3 A1 CE B2 C3 A7'), self.abc8)
    def test_getitem(self):
        self.assertEqual(self.abc8[2], self.abc[2])
        self.assertIsInstance(self.abc8[2], Str8)
    def test_iter(self):
        self.assertEqual(list(self.abc8), list(self.abc))
    def test_len(self):
        self.assertEqual(len(self.abc8), 3)
    def test_hash(self):
        self.assertEqual(hash(self.abc8), hash(self.abc))
        self.assertEqual(hash(self.abc8.b), hash(self.abcb))
        self.assertEqual(hash(self.abc8.s), hash(self.abc))
    def test_sizeof(self):
        # The size is a bytes with a __dict__ plus a str, plus GC overhead.
        # So, that will be around 32 bytes more than just the bytes and str.
        self.assertGreaterEqual(sys.getsizeof(self.abc8),
                                sys.getsizeof(self.abc) + sys.getsizeof(self.abcb))
    def test_add(self):
        self.assertEqual(self.abc8 + self.abc8, self.abc + self.abc)
        self.assertEqual(self.abc8 + self.abc, self.abc + self.abc)
        self.assertEqual(self.abc + self.abc8, self.abc + self.abc)
        self.assertEqual(self.abc8 + self.abcb, self.abc + self.abc)
        self.assertEqual(self.abcb + self.abc8, self.abc + self.abc)
    def test_mul(self):
        self.assertEqual(self.abc8 * 3, Str8(self.abc * 3))
        self.assertEqual(3 * self.abc8, Str8(self.abc * 3))
    def test_format(self):
        self.assertEqual(Str8('%s %s %s') % (12, self.abcb, self.abc),
                         '%s %s %s' % (12, self.abc, self.abc))
        self.assertEqual('%s %s %s' % (12, self.abcb, self.abc8),
                         '%s %s %s' % (12, self.abcb, self.abc8))
        self.assertEqual(b'%d %s %s' % (12, self.abcb, self.abc8),
                         b'%d %s %s' % (12, self.abcb, self.abc8))
        self.assertEqual(format(self.abc8, '>10'), format(self.abc, '>10'))
        self.assertEqual(Str8('{} {} {}').format(12, self.abcb, self.abc),
                         '{} {} {}'.format(12, self.abc, self.abc))
        self.assertEqual(Str8('{} {b:10} {s:10}').format(12, b=self.abcb, s=self.abc),
                         '{} {b:10} {s:10}'.format(12, b=self.abc, s=self.abc))
    def test_translate(self):
        with self.assertRaises(TypeError):
            Str8.maketrans(b'1', '2')
        with self.assertRaises(TypeError):
            Str8.maketrans('1', b'2')
        with self.assertRaises(TypeError):
            Str8.maketrans(b'1', b'2', delete=b'3')
        btrans = bytes.maketrans(b'\xc3', b'\xc4')
        self.assertEqual(Str8.maketrans(b'\xc3', b'\xc4'), btrans)
        self.assertEqual(self.abc8.translate(btrans),
                         self.abcb.translate(btrans))
        self.assertIsInstance(self.abc8.translate(btrans), Str8)
        btrans2 = Str8.maketrans(b'\xc3', b'?')
        with self.assertRaises(UnicodeDecodeError):
            self.abc8.translate(btrans2)
        strans1 = str.maketrans(self.abc[0], '?')
        self.assertEqual(Str8.maketrans(self.abc[0], '?'), strans1)
        self.assertEqual(self.abc8.translate(strans1),
                         self.abc.translate(strans1))
        self.assertIsInstance(self.abc8.translate(strans1), Str8)        
        strans1d = str.maketrans(self.abc[0], '?', self.abc[1])
        self.assertEqual(Str8.maketrans(self.abc[0], '?', self.abc[1]),
                         strans1d)
        self.assertEqual(Str8.maketrans(self.abc[0], '?', self.abc8[1]),
                         strans1d)
        self.assertEqual(self.abc8.translate(strans1d),
                         self.abc.translate(strans1d))
        strans2 = str.maketrans({self.abc[0]: '?'})
        self.assertEqual(Str8.maketrans({self.abc[0]:'?'}), strans2)
        self.assertEqual(Str8.maketrans({self.abc8[0]:'?'}), strans2)
        self.assertEqual(self.abc8.translate(strans2),
                         self.abc.translate(strans2))
    def test_case(self):
        self.assertEqual(self.abc8.lower(), self.abc8)
        self.assertEqual(self.abc8.upper(), self.abc.upper())
        self.assertEqual(self.abc8.b.upper(), self.abc8)
        self.assertEqual(Str8('ß').casefold(), 'ss')
        self.assertIsInstance(self.abc8.lower(), Str8)
    def test_just(self):
        self.assertEqual(self.abc8.center(5), ' ' + self.abc8 + ' ')
        self.assertEqual(self.abc8.b.center(5), self.abcb)
        self.assertIsInstance(self.abc8.center(5), Str8)
    def test_is(self):
        self.assertTrue(Str8('١').isdigit())
    def test_find(self):
        self.assertEqual(self.abc8.find(self.abc[1]), 1)
        self.assertEqual(self.abc8.find(self.abc[1].encode()), 2)
        self.assertEqual(self.abc8.count(b'\xc3'), 2)
    def test_strip(self):
        s8 = ' ' + self.abc8 + b' 1'
        self.assertEqual(s8.strip(), s8[1:])
        self.assertEqual(s8.strip(' 1'), self.abc8)
        self.assertEqual(s8.strip(b'1'), s8[:-1])
        self.assertIsInstance(s8.strip('1'), Str8)
        self.assertIsInstance(s8.strip(b'1'), Str8)
    def test_splitjoin(self):
        self.assertEqual(Str8('.').join((self.abc, self.abcb, self.abc8)),
                         '.'.join((self.abc, self.abc, self.abc)))
        self.assertEqual(Str8('.').join((self.abc, self.abcb, self.abc8)),
                         '.'.join((self.abc, self.abc, self.abc)))
        self.assertIsInstance(Str8('.').join(('1', b'2')), Str8)
        self.assertEqual(Str8('abc\ndef\nghi').splitlines(),
                         'abc\ndef\nghi'.splitlines())
        self.assertIsInstance(Str8('abc\ndef\nghi').splitlines()[0], Str8)
        self.assertEqual(self.abc8.partition(self.abc[1]), list(self.abc))
        self.assertIsInstance(self.abc8.rpartition(self.abc[1])[0], Str8)
        self.assertEqual(self.abc8.partition(self.abcb[2:4]), list(self.abc))
        with self.assertRaises(UnicodeDecodeError):
            self.abc8.partition(self.abcb[2:3])
    def test_replace(self):
        self.assertEqual(self.abc8.replace(self.abc8[1], '123'),
                         self.abc.replace(self.abc[1], '123'))
        self.assertIsInstance(self.abc8.replace(self.abc8[1], '123'), Str8)
        self.assertEqual(self.abc8.replace(self.abcb[2:4], '123'),
                         self.abc.replace(self.abc[1], '123'))
        self.assertEqual(self.abc8.replace(self.abcb[2:4], b'123'),
                         self.abc.replace(self.abc[1], '123'))
        self.assertIsInstance(self.abc8.replace(self.abcb[2:4], b'123'), Str8)
        with self.assertRaises(UnicodeDecodeError):
            self.abc8.replace(self.abcb[2:3], '')
        
if __name__ == '__main__':
    unittest.main()
