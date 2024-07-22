from rest_framework import serializers
from .models import Sale


class SaleListSerializer(serializers.ModelSerializer):
    """
    판매 목록을 위한 Serializer
    """
    class Meta:
        model = Sale
        fields = ['id', 'photo_card_id', 'price']


class SaleDetailSerializer(serializers.ModelSerializer):
    """
    판매 상세 정보를 위한 Serializer
    """
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = ['id', 'photo_card_id', 'price', 'fee', 'total_price']

    @staticmethod
    def get_total_price(sale):
        """
        총 가격 계산
        :param sale: Sale 객체
        :return: 총 가격
        """
        return sale.price + sale.fee


class SaleSoldDetailSerializer(serializers.ModelSerializer):
    """
    판매 완료된 상세 정보를 위한 Serializer
    """
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = '__all__'

    @staticmethod
    def get_total_price(sale):
        """
        총 가격 계산
        :param sale: Sale 객체
        :return: 총 가격
        """
        return sale.price + sale.fee


class SalePurchaseSerializer(serializers.ModelSerializer):
    """
    판매 구매 요청을 위한 Serializer
    """
    class Meta:
        model = Sale
        fields = ['id']

    def validate(self, attrs):
        """
        구매 요청 유효성 검사
        :param attrs: 검증할 데이터
        :return: 검증된 데이터
        """
        sale_id = self.context['request'].parser_context['kwargs'].get('pk')
        if not sale_id:
            raise serializers.ValidationError("판매 ID가 필요합니다.")

        try:
            sale = Sale.objects.get(id=sale_id)
        except Sale.DoesNotExist:
            raise serializers.ValidationError("해당 상품을 찾을 수 없습니다.")

        if sale.state != Sale.StateChoice.AVAILABLE.value:
            raise serializers.ValidationError("해당 상품은 이미 판매 완료되었습니다.")

        user = self.context['request'].user
        if user.cash < sale.total_price():
            raise serializers.ValidationError("잔액이 부족합니다.")

        return attrs
