import unittest

from utils.cache.decorators import CacheDecorators


class CacheDecoratorsTest(unittest.TestCase):

	def test_get_cache_keys(self):
		args, kwargs = [
			(("USD", "ZAR"),),
			(("ZAR", "USD"),)
		], [{}, {}]

		keys = [
			CacheDecorators._CacheDecorators__get_cache_keys(a, k)
			for a, k in zip(args, kwargs)
		]

		self.assertFalse(keys[0] == keys[1])
