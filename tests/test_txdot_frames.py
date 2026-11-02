import unittest
from scripts.txdot_frames import extract_cameras, safe_name

class TestTxDOT(unittest.TestCase):
    def test_extract_cards(self):
        html = '<div class="card">Dallas camera<img src="/images/cam.jpg"></div>'
        rows = extract_cameras(html, "https://example.org/road")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["image_url"], "https://example.org/images/cam.jpg")

    def test_safe_name(self):
        self.assertEqual(safe_name("Dallas: I-35"), "Dallas_I-35")

if __name__ == "__main__":
    unittest.main()
