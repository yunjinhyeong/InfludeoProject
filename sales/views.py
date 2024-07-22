from django.db.models import OuterRef, Subquery
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Sale
from .serializers import SaleListSerializer, SaleDetailSerializer, SalePurchaseSerializer, SaleSoldDetailSerializer


class SaleList(generics.ListCreateAPIView):
    """
    판매 목록을 조회하고 새로운 판매를 생성합니다.
    판매 목록은 현재 판매중인 상태만 포함됩니다.
    """
    serializer_class = SaleListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        현재 판매중인 상품들 중에서 각 photo_card_id별로 가장 먼저등록된 renewal_date를 가진 판매만 필터링하여 반환합니다.
        :return: 현재 판매중인 상품들 중에서 가장 먼저등록된 renewal_date를 가진 판매 들의 리스트
        """
        # 각 photo_card_id에 대해 최신 renewal_date를 가진 Sale의 id를 찾음
        subquery = Sale.objects.filter(
            photo_card_id=OuterRef('photo_card_id'),
            state=Sale.StateChoice.AVAILABLE.value
        ).order_by(
            'price', 'renewal_date'  # 최신 renewal_date 순으로 정렬
        ).values('id')[:1]  # 각 그룹에서 가장 최신의 id만 선택

        # 부모 쿼리에서 서브쿼리 결과를 필터링
        return Sale.objects.filter(
            id__in=Subquery(subquery)
        )

    def perform_create(self, serializer):
        """
        새로운 판매를 등록합니다.
        현재 로그인한 사용자를 판매자(seller)로 설정하고, 상태(state)는 '판매중'으로 설정합니다.
        :param serializer: 판매 데이터를 포함하는 serializer 객체
        :return: None
        """
        serializer.save(seller=self.request.user, state=Sale.StateChoice.AVAILABLE.value)


class SaleDetail(generics.RetrieveAPIView):
    """
    판매 목록의 상세 정보를 조회합니다.
    특정 sale 항목과 해당 photo_card_id로 판매완료된 최근 거래를 5개 조회합니다.
    """
    serializer_class = SaleDetailSerializer

    def get_object(self):
        """
        특정 sale 항목을 조회합니다.
        :return: Sale 객체
        """
        photo_card_id = self.kwargs.get('photo_card_id')
        sale = Sale.objects.filter(
            photo_card_id=photo_card_id,
            state=Sale.StateChoice.AVAILABLE.value
        ).order_by('price', 'renewal_date').first()

        if not sale:
            raise NotFound("해당 photo_card_id에 대한 판매 항목이 없습니다.")
        return sale

    def retrieve(self, request, *args, **kwargs):
        """
        특정 sale 항목과 해당 photo_card_id에 대한 최근 거래를 5개까지 조회하여 응답합니다.
        :param request: HTTP 요청 객체
        :param args: 추가적인 위치 인자
        :param kwargs: 추가적인 키워드 인자
        :return: HTTP 응답 객체
        """
        instance = self.get_object()
        sold_sales = Sale.objects.filter(
            photo_card_id=instance.photo_card_id,
            state=Sale.StateChoice.SOLD.value
        ).order_by('-sold_date')[:5]

        serializer = self.get_serializer(instance)
        response_data = serializer.data
        response_data['sold_sales'] = SaleSoldDetailSerializer(sold_sales, many=True).data

        return Response(response_data)


class SalePurchaseView(generics.GenericAPIView):
    """
    판매 구매를 처리하는 뷰
    """
    serializer_class = SalePurchaseSerializer
    queryset = Sale.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        판매 구매 요청을 처리합니다.
        :param request: 요청 객체
        :return: 응답 객체
        """
        sale_id = self.kwargs.get('pk')
        sale = Sale.objects.get(id=sale_id)
        serializer = self.get_serializer(data={'id': sale_id}, context={'request': request})

        # 유효성 검증
        serializer.is_valid(raise_exception=True)

        # 유효성 검증 후 구매 처리
        user = request.user

        user.cash -= sale.total_price()
        user.save()

        sale.state = Sale.StateChoice.SOLD.value
        sale.buyer = user
        sale.sold_date = timezone.now()
        sale.save()

        return Response({"detail": "구매가 완료되었습니다."}, status=status.HTTP_200_OK)
