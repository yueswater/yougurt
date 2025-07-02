from src.utils.sheet_client import get_worksheet


def main():
    worksheet = get_worksheet("Products")
    records = worksheet.get_all_records()
    for row in records:
        print(row)


if __name__ == "__main__":
    main()
