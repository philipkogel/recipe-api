"""Test Ingredients API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return ingredient detail url."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_user(email='example@user.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class TestPublicIngredientApi(TestCase):
    """Test unauthenticated api requests."""
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retreving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class TestPrivateIngredientAPi(TestCase):
    """Test authenticated api requests."""
    def setUp(self) -> None:
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrive_ingredients(self):
        """Test retriving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Pepper')
        Ingredient.objects.create(user=self.user, name='Vanilla')
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_retrive_user_ingredients(self):
        """Test retriving list of ingredients created by requesting user."""
        new_user = create_user(
            email='user2@example.com',
            password='123testpass'
        )
        Ingredient.objects.create(user=new_user, name='Garlic')
        Ingredient.objects.create(user=self.user, name='Onions')

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.filter(
            user=self.user
        ).order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Cilantro'
        )

        payload = {'name': 'Coriander'}
        url = detail_url(ingredient_id=ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(
            user=self.user,
            name='Basil'
        )

        url = detail_url(ingredient_id=ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(
            user=self.user
        )
        self.assertFalse(ingredients.exists())
