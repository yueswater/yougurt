from src.repos.member_repo import GoogleSheetMemberRepository, MemberRepository
from src.repos.product_repo import GoogleSheetProductRepository, ProductRepository


def get_member_repo() -> MemberRepository:
    return GoogleSheetMemberRepository()


def get_product_repo() -> ProductRepository:
    return GoogleSheetProductRepository()
