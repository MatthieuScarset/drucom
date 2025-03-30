import unittest
from drucom.main import main

class TestMain(unittest.TestCase):
    def test_main(self):
        # Example test for the main function
        self.assertIsNone(main())

if __name__ == "__main__":
    unittest.main()
