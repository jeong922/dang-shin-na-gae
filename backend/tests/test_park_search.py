import unittest
from unittest.mock import patch

import pandas as pd

from app.services import parks, search


class ParkSearchTests(unittest.TestCase):
    services = (parks.get_parks, search.get_search_parks)

    def setUp(self):
        self.frame = pd.DataFrame(
            [
                (1, "진관근린공원(구파발폭포)", "easy", "은평구", "allowed"),
                (2, "진관근린공원", "hard", "은평구", "allowed"),
                (3, "서울숲 공원", "easy", "성동구", "allowed"),
                (4, "서울숲 생태공원", "easy", "성동구", "allowed"),
                (5, "서울숲 공원 별관", "hard", "성동구", "allowed"),
                (6, "서울숲 공원 분원", "easy", "은평구", "allowed"),
                (7, "서울숲 공원 정원", "easy", "성동구", "prohibited"),
                (8, "Seoul Forest", "easy", "성동구", "allowed"),
                (9, "다른 공원", "easy", "성동구", "allowed"),
            ],
            columns=["id", "name", "difficulty", "district", "petStatus"],
        )
        for module in (parks, search):
            patcher = patch.object(module, "load_parks", return_value=self.frame)
            patcher.start()
            self.addCleanup(patcher.stop)

    def assert_matches(self, service, keyword, expected_ids, **kwargs):
        result = service(keyword=keyword, columns=["id", "name"], **kwargs)
        self.assertEqual([item["id"] for item in result["items"]], expected_ids)
        self.assertEqual(result["total"], len(expected_ids))

    def test_special_characters_are_literal(self):
        for keyword in ("[", "[]", "(", ")", "\\", "*", "+", "?", ".", "|", "^", "$"):
            self.frame.loc[0, "name"] = f"테스트{keyword}공원"
            for service in self.services:
                with self.subTest(service=service.__name__, keyword=keyword):
                    self.assert_matches(service, keyword, [1])

    def test_full_park_name_with_parentheses(self):
        for service in self.services:
            with self.subTest(service=service.__name__):
                self.assert_matches(service, "진관근린공원(구파발폭포)", [1])

    def test_normal_substring_search(self):
        for service in self.services:
            for keyword, expected in (
                ("진관", [1, 2]),
                ("서울숲", [3, 4, 5, 6, 7]),
                ("seoul", [8]),
                ("없는공원", []),
            ):
                with self.subTest(service=service.__name__, keyword=keyword):
                    self.assert_matches(service, keyword, expected)

    def test_search_with_existing_filters(self):
        for service in self.services:
            with self.subTest(service=service.__name__):
                self.assert_matches(
                    service,
                    "서울숲",
                    [3, 4],
                    difficulty=["easy"],
                    district=["성동구"],
                    pet_status=["allowed"],
                )

    def test_filtered_search_pagination(self):
        for page, expected_ids in ((1, [3]), (2, [4]), (3, [])):
            with self.subTest(page=page):
                result = parks.get_parks(
                    keyword="서울숲",
                    difficulty=["easy"],
                    district=["성동구"],
                    pet_status=["allowed"],
                    page=page,
                    page_size=1,
                    columns=["id"],
                )
                self.assertEqual(result["items"], [{"id": park_id} for park_id in expected_ids])
                self.assertEqual(result["total"], 2)
                self.assertEqual(result["page"], page)
                self.assertEqual(result["pageSize"], 1)
                self.assertEqual(result["totalPages"], 2)


if __name__ == "__main__":
    unittest.main()
