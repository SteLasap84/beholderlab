import json
import tempfile
import unittest
from pathlib import Path

from build_gallery import build_gallery


class GalleryIndexTest(unittest.TestCase):
    def test_albums_and_photos_are_indexed_safely(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            gallery = root / "photo-gallery"
            album = gallery / "Evento Roma-2026"
            album.mkdir(parents=True)
            (gallery / "LabLife").mkdir()
            (album / "2 #foto.JPG").touch()
            (album / "1 foto.webp").touch()
            (album / ".hidden.jpg").touch()
            (album / "notes.txt").touch()
            (album / "nested").mkdir()
            (album / "nested" / "ignored.jpg").touch()

            build_gallery(root)
            albums = json.loads((root / "assets" / "gallery.json").read_text())

            self.assertEqual(albums, [
                {
                    "id": "Evento Roma-2026",
                    "title": "Evento Roma 2026",
                    "photos": [
                        "/photo-gallery/Evento%20Roma-2026/1%20foto.webp",
                        "/photo-gallery/Evento%20Roma-2026/2%20%23foto.JPG",
                    ],
                },
                {"id": "LabLife", "title": "LabLife", "photos": []},
            ])

    def test_missing_gallery_directory_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                build_gallery(Path(directory))


if __name__ == "__main__":
    unittest.main()
