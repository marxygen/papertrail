from argparse import ArgumentParser, Namespace
import sqlite3
import pandas as pd

from arxiv.api import get_papers_in_category


def get_args() -> Namespace:
    parser = ArgumentParser("Paper Fetcher")
    parser.add_argument('--db', default='./papers.db', help='Path to a SQLite database that the paper info will be written into')
    parser.add_argument('--category', default='cs.LG', help='Arxiv category code')
    parser.add_argument('--batch-size', help='Number of elements to load at once')
    return parser.parse_args()


def load_last_page_number(con: sqlite3.Connection) -> int | None:
    cursor = con.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS stats (stat TEXT, value FLOAT)")

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stats';")
    if cursor.rowcount in [0, -1]:
        con.commit()
        return None

    cursor.execute('SELECT value FROM stats WHERE stat = "last_page" LIMIT 1')
    return cursor.fetchone()


def save_last_page_number(con: sqlite3.Connection, last_page: int) -> None:
    cursor = con.cursor()
    cursor.execute(f'INSERT INTO stats ("stat", "value") VALUES ("last_page", {last_page})')
    con.commit()


def main():
    args = get_args()
    print("=" * 20, 'Paper Fetcher', "=" * 20)
    print(f'Category: {args.category}')
    print(f'Batch size: {args.batch_size or "Default"}')
    print(f'DB: {args.db}')

    con = sqlite3.connect(args.db)
    last_page_number = load_last_page_number(con)
    if last_page_number:
        print(f'Picking up from page {last_page_number:,}')
    else:
        last_page_number = 0
        print(f'No last page number retrieved from the database, starting from 0')

    def save_entries(entries):
        df = pd.DataFrame([e.to_json() for e in entries])
        df.to_sql(con=con, name='papers', if_exists='replace', index=False)
        save_last_page_number(con, start)
        entries = []

    try:
        start = None
        entries = []
        for entry, start in get_papers_in_category(category_id=args.category, start=int(last_page_number), batch_size=args.batch_size):
            print(f'- {entry.title}, {len(entry.reference_ids)} references')
            entries.append(entry)

            if len(entries) % 1_000 == 0:
                save_entries(entries)

        save_entries(entries)

    except KeyboardInterrupt:
        print(f'Ctrl + C detected, exiting')


if __name__ == '__main__':
    main()
