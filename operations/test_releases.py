import unittest
from releases import choose_release


class ReleaseTests(unittest.TestCase):
    def test_final_semver_only_and_no_downgrade(self):
        tags = ['v0.23.0','v0.23.1','v0.24.0','v0.25.0-rc.1','v2026.11.15','v0.024.1','v0.26.0']
        releases = [{'tag_name':t, 'prerelease':t=='v0.26.0'} for t in tags]
        self.assertEqual(choose_release(releases), 'v0.24.0')
        self.assertIsNone(choose_release(releases, (0,24,0)))

    def test_excludes_drafts_and_orders_numerically(self):
        releases = [{'tag_name':'v0.9.0'}, {'tag_name':'v0.100.0'}, {'tag_name':'v1.0.0','draft':True}]
        self.assertEqual(choose_release(releases), 'v0.100.0')


if __name__ == '__main__':
    unittest.main()
