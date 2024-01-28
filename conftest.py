import pytest

from api.models import Product, User


@pytest.fixture
def seller1():
    return User.objects.create_user(username='seller1', password='seller1', role='seller')


@pytest.fixture
def seller2():
    return User.objects.create_user(username='seller2', password='seller2', role='seller')


@pytest.fixture
def buyer1():
    return User.objects.create_user(username='buyer1', password='buyer1', role='buyer', deposit=20)


@pytest.fixture
def buyer2():
    return User.objects.create_user(username='buyer2', password='buyer2', role='buyer', deposit=100)


@pytest.fixture
def product1(seller1):
    return Product.objects.create(product_name='Product 1',
                                  amount_available=4,
                                  cost=5,
                                  seller=seller1)


@pytest.fixture
def product2(seller2):
    return Product.objects.create(product_name='Product 2',
                                  amount_available=20,
                                  cost=15,
                                  seller=seller2)
