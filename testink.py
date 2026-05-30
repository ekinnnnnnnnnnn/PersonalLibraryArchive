import unittest

class testinkall(unittest.TestCase):
    def testRating(self):
        canRate = lambda status: status == 'read'
        isValidRating = lambda r: isinstance(r, int) and 1 <= r <= 10
        
        self.assertTrue(canRate('read'))
        self.assertFalse(canRate('reading'))
        self.assertTrue(isValidRating(5))
        self.assertFalse(isValidRating(11))

    def testPaging(self):
        def paging(t, r):
            try:
                total, read = int(t), int(r)
                return "error" if read > total else (total, read)
            except ValueError:
                return "valueError"
        self.assertEqual(paging("300", "150"), (300, 150))
        self.assertEqual(paging("100", "200"), "error")
        self.assertEqual(paging("abc", "10"), "valueError")

if __name__ == '__main__':
    unittest.main()
