from knox.views import LoginView as KnoxLoginView
from rest_framework import mixins, viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from api.models import Product, User
from api.permissions import BuyerPermission, SellerPermission, UserPermission
from api.serializers import (BuyProductSerializer, ProductGetSerializer, ProductSerializer, UserCreateSerializer,
                             UserSerializer)


class LoginView(KnoxLoginView):
    authentication_classes = [BasicAuthentication]


class UserViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['destroy', 'list']:
            self.permission_classes = [IsAdminUser]
        elif self.action == 'retrieve':
            self.permission_classes = [IsAuthenticated, UserPermission]
        elif self.action in ['deposit', 'reset']:
            self.permission_classes = [IsAuthenticated, BuyerPermission]
        else:  # create
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    @action(detail=False, methods=['POST'])
    def deposit(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def reset(self, request):
        request.user.deposit = 0
        request.user.save()
        return Response(self.get_serializer(request.user).data)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ProductGetSerializer
        elif self.action == 'buy':
            return BuyProductSerializer
        return ProductSerializer

    def get_permissions(self):
        if self.action == 'buy':
            self.permission_classes = [IsAuthenticated, BuyerPermission]
        else:
            self.permission_classes = [IsAuthenticated, SellerPermission]
        return super().get_permissions()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        kwargs['context']['user'] = self.request.user
        return serializer_class(*args, **kwargs)

    @action(detail=True, methods=['POST'])
    def buy(self, request, pk=None):
        product = self.get_object()
        serializer = self.get_serializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())
