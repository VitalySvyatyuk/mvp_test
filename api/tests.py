import pytest
from rest_framework.test import APIClient

from .models import Product, User

client = APIClient()

@pytest.mark.django_db
def test_anonymous_user_dont_have_access():
    response = client.get('/api/products/')
    assert response.status_code == 401

@pytest.mark.django_db
def test_seller_creates_product(seller1):
    client.force_authenticate(seller1)
    response = client.post(
        '/api/products/', {'product_name': 'New Product', 'amount_available': 50, 'cost': 25})
    assert response.status_code == 201
    assert response.json()['product_name'] == 'New Product'
    assert Product.objects.first().seller == seller1

@pytest.mark.django_db
def test_seller_error_creating_product(seller1):
    client.force_authenticate(seller1)

    # cost = 0
    response = client.post(
        '/api/products/', {'product_name': 'New Product', 'amount_available': 50, 'cost': 0})
    assert response.status_code == 400
    assert response.json()['cost'] == ['Cost must be > 0']

    # cost = 9
    response = client.post(
        '/api/products/', {'product_name': 'New Product', 'amount_available': 50, 'cost': 9})
    assert response.status_code == 400
    assert response.json()['cost'] == ['Cost must be divisible by 5 without a remainder']

    # product name
    response = client.post(
        '/api/products/', {'amount_available': 50, 'cost': 10})
    assert response.status_code == 400
    assert response.json()['product_name'] == ['This field is required.']

@pytest.mark.django_db
def test_seller_updates_product(seller1, product1):
    client.force_authenticate(seller1)

    # put
    response = client.put(
        '/api/products/1/', {'product_name': 'New Product', 'amount_available': 70, 'cost': 35})
    assert response.status_code == 200
    assert Product.objects.last().cost == 35

    # patch
    response = client.patch(
        '/api/products/1/', {'amount_available': 80})
    assert response.status_code == 200
    assert Product.objects.last().amount_available == 80

@pytest.mark.django_db
def test_seller_updates_wrong_product(seller1, product2):
    client.force_authenticate(seller1)
    response = client.patch(
        f'/api/products/{product2.id}/', {'cost': 45})
    assert response.status_code == 403
    assert response.json()['detail'] == 'You do not have permission to perform this action.'

@pytest.mark.django_db
def test_seller_deletes_product(seller1, product1):
    client.force_authenticate(seller1)
    response = client.delete('/api/products/1/')
    assert response.status_code == 204
    assert Product.objects.all().exists() is False

@pytest.mark.django_db
def test_seller_error_updating_deposit(seller1):
    client.force_authenticate(seller1)
    response = client.post('/api/users/deposit/', {'deposit': 150})
    assert response.status_code == 403

@pytest.mark.django_db
def test_seller_error_buying_product(seller1, product2):
    client.force_authenticate(seller1)
    response = client.post(f'/api/products/{product2.id}/buy/', {'amount': 1})
    assert response.status_code == 403

@pytest.mark.django_db
def test_buyer_error_creating_product(buyer1):
    client.force_authenticate(buyer1)
    response = client.post(
        '/api/products/', {'product_name': 'New Product', 'amount_available': 50, 'cost': 25})
    assert response.status_code == 403

@pytest.mark.django_db
def test_buyer_error_updating_product(buyer1, product1):
    client.force_authenticate(buyer1)
    response = client.patch(
        '/api/products/1/', {'cost': 35})
    assert response.status_code == 403

@pytest.mark.django_db
def test_buyer_error_deleting_product(buyer1, product1):
    client.force_authenticate(buyer1)
    response = client.delete('/api/products/1/')
    assert response.status_code == 403

@pytest.mark.django_db
def test_buyer_updates_deposit(buyer1):
    client.force_authenticate(buyer1)
    response = client.post('/api/users/deposit/', {'deposit': 20})
    assert response.status_code == 200
    assert User.objects.first().deposit == 40

@pytest.mark.django_db
def test_buyer_error_updating_deposit(buyer1):
    client.force_authenticate(buyer1)
    response = client.post('/api/users/deposit/', {'deposit': 30})
    assert response.status_code == 400
    assert response.json()['deposit'] == ['Value not allowed']

@pytest.mark.django_db
def test_buyer_buys_product(buyer1, product1, buyer2, product2):
    client.force_authenticate(buyer1)
    response = client.post(f'/api/products/{product1.id}/buy/', {'amount': 3})
    assert response.status_code == 200
    assert response.json()['total_spent'] == 15
    assert response.json()['product'] == 'Product 1'
    assert response.json()['change'] == [5]

    client.force_authenticate(buyer2)
    response = client.post(f'/api/products/{product1.id}/buy/', {'amount': 1})
    assert response.status_code == 200
    assert response.json()['total_spent'] == 5
    assert response.json()['product'] == 'Product 1'
    assert response.json()['change'] == [50, 20, 20, 5]

@pytest.mark.django_db
def test_buyer_error_buying_product(buyer1, product1, buyer2, product2):
    client.force_authenticate(buyer1)

    # at least 1 amount
    response = client.post(f'/api/products/{product1.id}/buy/', {'amount': 0})
    assert response.status_code == 400
    assert response.json()['amount'] == ['Must be at least 1 amount']

    # cost > 0
    product2.cost = 0
    product2.save()
    response = client.post(f'/api/products/{product2.id}/buy/', {'amount': 1})
    assert response.status_code == 400
    assert response.json()['non_field_errors'] == ['Cost must be > 0']

    # deposit > 0
    buyer1.deposit = 0
    buyer1.save()
    response = client.post(f'/api/products/{product1.id}/buy/', {'amount': 1})
    assert response.status_code == 400
    assert response.json()['non_field_errors'] == ['Deposit must be > 0']

    # deposit is not enough
    buyer1.deposit = 5
    buyer1.save()
    response = client.post(f'/api/products/{product1.id}/buy/', {'amount': 2})
    assert response.status_code == 400
    assert response.json()['non_field_errors'] == ['Deposit is not enough']

    # not enough product
    client.force_authenticate(buyer2)
    response = client.post(f'/api/products/{product1.id}/buy/', {'amount': 5})
    assert response.status_code == 400
    assert response.json()['non_field_errors'] == ['Not enough product']
