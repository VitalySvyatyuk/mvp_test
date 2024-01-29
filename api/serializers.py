from rest_framework import serializers
from rest_framework.validators import ValidationError

from api.models import Product, User
from api.utils import get_change


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'deposit']

    def update(self, instance, validated_data):
        setattr(instance, 'deposit', instance.deposit + validated_data['deposit'])
        instance.save()
        return instance

    def validate_deposit(self, value):
        if value not in [0, 5, 10, 20, 50, 100]:
            raise ValidationError('Value not allowed')
        return value


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'role', 'deposit']

    def create(self, validated_data):
        instance = User.objects.create_user(**validated_data)
        return instance


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_name', 'amount_available', 'cost']

    def validate_cost(self, value):
        if value <= 0:
            raise ValidationError('Cost must be > 0')
        if value % 5 != 0:
            raise ValidationError('Cost must be divisible by 5 without a remainder')
        return value

    def validate(self, attrs):
        attrs['seller_id'] = self.context['user'].id
        return attrs


class ProductGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'product_name', 'amount_available', 'cost', 'seller']


class BuyProductSerializer(serializers.Serializer):
    amount = serializers.IntegerField()  # buyer's desired amount

    def validate_amount(self, value):
        if value <= 0:
            raise ValidationError('Must be at least 1 amount')
        return value

    def validate(self, items):
        product = self.instance
        buyer = self.context['user']
        if product.amount_available <= 0:
            raise ValidationError('Amount is not available')
        if product.cost <= 0:
            raise ValidationError('Cost must be > 0')
        if buyer.deposit <= 0:
            raise ValidationError('Deposit must be > 0')
        if items['amount'] * product.cost > buyer.deposit:
            raise ValidationError('Deposit is not enough')
        if product.amount_available < items['amount']:
            raise ValidationError('Not enough product')
        return items

    def update(self, instance, validated_data):
        total_spent = validated_data['amount'] * instance.cost
        deposit = self.context['user'].deposit - total_spent
        self.context['user'].deposit = 0
        instance.amount_available -= validated_data['amount']
        self.context['user'].save()
        instance.save()
        return {'total_spent': total_spent,
                'product': instance.product_name,
                'change': get_change(deposit)}
