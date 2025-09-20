from dotenv import load_dotenv
import os
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

load_dotenv()  # ensure .env variables are loaded for tests

# Create your tests here.
class ParseNotesViewTests(APITestCase):
    def test_parse_notes_success(self):
        url = reverse('vision_api:parse-notes')  # Use the URL name from your urls.py
        
        # Example URL to parse (you can choose any valid URL)
        data = {
            "url": "https://noobnotes.net/cant-help-falling-in-love-elvis-presley/?solfege=false"
        }
        
        response = self.client.post(url, data, format='json')
        print("Response status:", response.status_code)
        print("Response data:", response.data) 
        
        # Assert the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Assert the response contains 'parsed_notes' key
        self.assertIn('parsed_notes', response.data)
        
        # Optionally, check parsed_notes is a list and non-empty
        self.assertIsInstance(response.data['parsed_notes'], list)
        self.assertTrue(len(response.data['parsed_notes']) > 0               
                    )
        
        class ParseNotesAndGeminiIntegrationTests(APITestCase):
            def test_parse_and_shape_generation(self):
                url = reverse('vision_api:parse-notes')  # Your actual route name

        # Provide URL pointing to notes to be parsed
        data = {
            "url": "https://noobnotes.net/cant-help-falling-in-love-elvis-presley/?solfege=false"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # The response should include parsed notes and shape mappings (adjust keys accordingly)
        self.assertIn('parsed_notes', response.data)
        self.assertIn('shapes', response.data)

        # Optionally validate types and non-empty data
        self.assertIsInstance(response.data['parsed_notes'], list)
        self.assertTrue(len(response.data['parsed_notes']) > 0)
        self.assertIsInstance(response.data['shapes'], dict)