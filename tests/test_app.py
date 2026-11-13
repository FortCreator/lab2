import os
import tempfile
import unittest

from app import create_app

class WebBoardTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

        db_path = os.path.join(
            self.temp_dir.name,
            "test_webboard.db"
        )

        self.app = create_app({
            "TESTING": True,
            "DATABASE": db_path,
            "SECRET_KEY": "test-secret"
        })

        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_home_page(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Доска объявлений".encode(),
            response.data
        )

    def test_search(self):
        response = self.client.get(
            "/?search=ноутбук"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Продам ноутбук".encode(),
            response.data
        )

    def test_listing_page(self):
        response = self.client.get("/listing/1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Продам ноутбук".encode(),
            response.data
        )

    def test_create_listing(self):
        response = self.client.post(
            "/create",
            data={
                "title": "Тестовое объявление",
                "description": "Описание тестового объявления"
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Тестовое объявление".encode(),
            response.data
        )

    def test_add_comment(self):
        response = self.client.post(
            "/listing/1",
            data={
                "content": "Тестовый комментарий"
            },
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Тестовый комментарий".encode(),
            response.data
        )

    def test_missing_listing(self):
        response = self.client.get("/listing/9999")

        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()