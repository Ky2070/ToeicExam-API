# from django.test import TestCase
# from rest_framework.test import APIClient
# from rest_framework import status
# from django.contrib.auth.models import User

# from datetime import datetime, timedelta
# from django.test import TestCase
# from EStudyApp.models import Test
#
#
# # Create test case
#
# class TestModelTestCase(TestCase):
#     def test_create_test_with_defaults(self):
#         """Kiểm tra tạo một đối tượng Test với các giá trị mặc định"""
#         test_instance = Test.objects.create(name="Sample Test")
#         self.assertEqual(test_instance.duration, timedelta(minutes=120))
#         self.assertEqual(test_instance.question_count, 200)
#         self.assertEqual(test_instance.part_count, 7)
#         self.assertIsNone(test_instance.type)
#         self.assertIsNone(test_instance.description)
#         self.assertIsNotNone(test_instance.test_date)  # Mặc định là thời gian hiện tại
#
#     def test_create_test_with_custom_values(self):
#         """Kiểm tra tạo một đối tượng Test với giá trị tùy chỉnh"""
#         test_instance = Test.objects.create(
#             name="Custom Test",
#             description="This is a custom test.",
#             type="READING",
#             test_date=datetime(2024, 1, 1, 10, 0, 0),
#             duration=timedelta(minutes=90),
#             question_count=150,
#             part_count=5,
#         )
#         self.assertEqual(test_instance.name, "Custom Test")
#         self.assertEqual(test_instance.description, "This is a custom test.")
#         self.assertEqual(test_instance.type, "READING")
#         self.assertEqual(test_instance.test_date, datetime(2024, 1, 1, 10, 0, 0))
#         self.assertEqual(test_instance.duration, timedelta(minutes=90))
#         self.assertEqual(test_instance.question_count, 150)
#         self.assertEqual(test_instance.part_count, 5)
#
#     def test_invalid_type_choice(self):
#         """Kiểm tra tạo một đối tượng Test với type không hợp lệ"""
#         with self.assertRaises(ValueError):
#             Test.objects.create(name="Invalid Type Test", type="INVALID")
#
#     def test_str_method(self):
#         """Kiểm tra phương thức __str__"""
#         test_instance = Test.objects.create(name="Test for String")
#         self.assertEqual(str(test_instance), "Test for String")
#
#     def test_field_constraints(self):
#         """Kiểm tra các ràng buộc của trường"""
#         # Kiểm tra max_length của name
#         test_instance = Test.objects.create(name="A" * 255)
#         self.assertEqual(test_instance.name, "A" * 255)
#
#         # Tạo một name vượt quá max_length
#         with self.assertRaises(ValueError):
#             Test.objects.create(name="A" * 256)
