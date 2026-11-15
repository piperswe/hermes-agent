"""Packaging-only tests; no Hermes config or production state is loaded."""
import unittest
from baseline import pin_image


class PromotionTests(unittest.TestCase):
    def test_pins_both_application_images_without_changing_sidecars(self):
        old = 'nousresearch/hermes-agent@sha256:' + '1' * 64
        text = f'image: {old}\nimage: nginx:1.30.6-alpine\nimage: {old}\n'
        result = pin_image(text, 'sha256:' + '2' * 64)
        self.assertEqual(result.count('ghcr.io/piperswe/hermes-agent@sha256:' + '2' * 64), 2)
        self.assertIn('image: nginx:1.30.6-alpine', result)

    def test_refuses_tags_and_incomplete_application_manifest(self):
        for digest in ('latest', 'sha256:abc', 'sha256:' + 'g' * 64):
            with self.assertRaises(ValueError):
                pin_image('image: placeholder', digest)
        with self.assertRaises(ValueError):
            pin_image('image: nginx:latest', 'sha256:' + '2' * 64)


if __name__ == '__main__':
    unittest.main()
