import builtins
import types
import importlib
from unittest import mock
import pandas as pd

import fetch_commits as fc


# Helper class to simulate requests responses
class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code
        self.text = str(json_data)

    def json(self):
        return self._json_data


def test_extract_name_from_email():
    assert fc.extract_name_from_email("john.doe@example.com") == "john doe"
    assert fc.extract_name_from_email("alice@example.com") == "alice"


def test_extract_project_from_title():
    assert fc.extract_project_from_title("XXXXX123-fix issue") == "XXXXX123"
    assert fc.extract_project_from_title("no match") == "N/A"


def test_organize_commits_by_author_project_and_month():
    commits = [
        {
            "author": {"email": "john.doe@example.com", "date": "2024-05-01T12:00:00Z"},
            "comment": "XXXXX1-initial commit",
        },
        {
            "author": {"email": "john.doe@example.com", "date": "2024-05-02T12:00:00Z"},
            "comment": "XXXXX1-update",
        },
        {
            "author": {"email": "alice@example.com", "date": "2024-06-03T12:00:00Z"},
            "comment": "XXXXX2-new feature",
        },
    ]
    result = fc.organize_commits_by_author_project_and_month(commits)
    assert result["john doe"]["XXXXX1"]["2024-05"] == 2
    assert result["alice"]["XXXXX2"]["2024-06"] == 1


def test_convert_to_dataframe():
    data = {
        "john": {"XXXXX1": {"2024-05": 3}},
        "alice": {"XXXXX2": {"2024-06": 1}},
    }
    df = fc.convert_to_dataframe(data)
    assert set(df.columns) == {"Author", "Project", "Month", "Commits"}
    # Ensure rows correspond to provided data
    assert df.loc[df["Author"] == "john", "Commits"].iloc[0] == 3


def test_fetch_commits_aggregates_results(monkeypatch):
    repos = [
        {"id": "1", "name": "r1"},
        {"id": "2", "name": "r2"},
    ]

    commits_repo1 = [
        {
            "author": {"email": "john@example.com", "date": "2024-05-01T00:00:00Z"},
            "comment": "XXXXX1-msg",
        }
    ]
    commits_repo2 = [
        {
            "author": {"email": "john@example.com", "date": "2024-05-02T00:00:00Z"},
            "comment": "XXXXX1-msg",
        },
        {
            "author": {"email": "alice@example.com", "date": "2024-06-01T00:00:00Z"},
            "comment": "XXXXX2-msg",
        },
    ]

    def fake_get_commits(repo_id):
        return commits_repo1 if repo_id == "1" else commits_repo2

    monkeypatch.setattr(fc, "get_commits", fake_get_commits)

    result = fc.fetch_commits(repos)
    assert result["john"]["XXXXX1"]["2024-05"] == 2
    assert result["alice"]["XXXXX2"]["2024-06"] == 1


def test_get_repositories_success(monkeypatch):
    def mock_get(url, headers=None):
        return MockResponse({"value": [{"id": 1}]}, 200)

    monkeypatch.setattr(fc.requests, "get", mock_get)

    repos = fc.get_repositories()
    assert repos == [{"id": 1}]


def test_get_commits_pagination(monkeypatch):
    responses = [
        MockResponse({"value": [{"id": "c1", "author": {"email": "a@b", "date": "2024-01-01T00:00:00Z"}, "comment": "XXXXX-"}]}),
        MockResponse({"value": []}),
    ]
    call_iter = iter(responses)

    def mock_get(url, headers=None, params=None, timeout=30):
        return next(call_iter)

    monkeypatch.setattr(fc.requests, "get", mock_get)

    commits = fc.get_commits("repo1")
    assert len(commits) == 1

