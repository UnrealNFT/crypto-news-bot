import os
from typing import Optional


class Storage:
    """Handles persistent storage for posted articles."""

    def __init__(self, data_dir: Optional[str] = None):
        if data_dir is None:
            data_dir = os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
        self.data_dir = data_dir
        self.posted_articles_file = os.path.join(data_dir, "posted_articles.txt")
        self.posted_titles_file = os.path.join(data_dir, "posted_titles.txt")

    def load_article_ids(self) -> set:
        try:
            with open(self.posted_articles_file, "r", encoding="utf-8") as f:
                return set(line.strip() for line in f if line.strip())
        except FileNotFoundError:
            return set()

    def load_titles(self) -> list:
        try:
            with open(self.posted_titles_file, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return []

    def save_article(self, article_id: str, title: str):
        try:
            with open(self.posted_articles_file, "a", encoding="utf-8") as f:
                f.write(article_id + "\n")
            with open(self.posted_titles_file, "a", encoding="utf-8") as f:
                f.write(title + "\n")
            self.cleanup()
        except Exception:
            pass

    def cleanup(self, max_items: int = 200):
        try:
            article_ids = list(self.load_article_ids())
            if len(article_ids) > max_items:
                article_ids = article_ids[-max_items:]
                with open(self.posted_articles_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(article_ids) + "\n")

            titles = self.load_titles()
            if len(titles) > max_items:
                titles = titles[-max_items:]
                with open(self.posted_titles_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(titles) + "\n")
        except Exception:
            pass
