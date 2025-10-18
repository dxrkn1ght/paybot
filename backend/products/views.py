from rest_framework import generics
from .models import Product
from .serializers import ProductSerializer

class ProductList(generics.ListAPIView):
    queryset = Product.objects.all().order_by('type','price')
    serializer_class = ProductSerializer
