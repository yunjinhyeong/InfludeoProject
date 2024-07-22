from django.urls import path
from .views import SaleList, SaleDetail, SalePurchaseView

urlpatterns = [
    # 판매 목록, 판매 등록
    path('sales/', SaleList.as_view()),
    # 판매 상세
    path('sales/<int:photo_card_id>/', SaleDetail.as_view()),
    # 판매 구매
    path('sales/purchase/<int:pk>/', SalePurchaseView.as_view()),
]
