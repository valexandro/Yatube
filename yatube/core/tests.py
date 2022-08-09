from http import HTTPStatus

from django.test import Client, TestCase


class ErrorPagesTemplatesTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_error_uses_correct_template(self):
        """Страница 404 ошибки использует нужный шаблон."""

        response_not_found = self.guest_client.get('/made_up_url/')
        self.assertEqual(response_not_found.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response_not_found, 'core/404.html')
