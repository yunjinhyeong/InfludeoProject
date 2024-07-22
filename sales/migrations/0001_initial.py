# Generated by Django 4.2.14 on 2024-07-19 02:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo_card_id', models.IntegerField(help_text='사진카드번호')),
                ('price', models.IntegerField(help_text='가격')),
                ('fee', models.IntegerField(help_text='수수료')),
                ('state', models.CharField(help_text='상태', max_length=10)),
                ('create_date', models.DateTimeField(auto_now_add=True, help_text='생성일')),
                ('renewal_date', models.DateTimeField(auto_now=True, help_text='수정일')),
                ('sold_date', models.DateTimeField(blank=True, help_text='판매일', null=True)),
            ],
        ),
    ]
