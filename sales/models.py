from django.db import models
from users.models import CustomUser


class Sale(models.Model):
    class StateChoice(models.TextChoices):
        AVAILABLE = 'available', '판매중'
        SOLD = 'sold', '판매완료'

    photo_card_id = models.IntegerField(
        help_text='사진카드번호'
    )
    price = models.IntegerField(
        help_text='가격'
    )
    fee = models.IntegerField(
        help_text='수수료'
    )
    state = models.CharField(
        help_text='상태',
        max_length=10,
    )
    buyer = models.ForeignKey(
        CustomUser,
        related_name='purchases',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='구매자'
    )
    seller = models.ForeignKey(
        CustomUser,
        related_name='sales',
        on_delete=models.CASCADE,
        help_text='판매자'
    )
    create_date = models.DateTimeField(
        auto_now_add=True,
        help_text='생성일'
    )
    renewal_date = models.DateTimeField(
        auto_now=True,
        help_text='수정일'
    )
    sold_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text='판매일'
    )

    def save(self, *args, **kwargs):
        """
        :param args: 추가적인 위치 인자
        :param kwargs: 추가적인 키워드 인자
        :return: None
        """
        if not self.fee:
            self.fee = self.calculate_fee()
        super().save(*args, **kwargs)

    def calculate_fee(self):
        """
        :return: 요금 계산 (따로 언급없어 임의 지정)
        """
        return int(self.price * 0.2)

    def total_price(self):
        """
        :return: 전체 가격
        """
        return self.price + self.fee
