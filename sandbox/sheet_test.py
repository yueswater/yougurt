from src.repos.member_repo import GoogleSheetMemberRepository


def main():
    repo = GoogleSheetMemberRepository()
    repo.get_all()
    print(repo.get_all())


if __name__ == "__main__":
    main()
