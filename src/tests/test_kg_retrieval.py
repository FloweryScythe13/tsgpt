from os import name
import unittest
from src.knowledge_service.knowledge_retrieval import *
import pandas as pd

class InformationRetrievalTests(unittest.TestCase):
    
    def test_get_candidates_with_standard_name_retrieves_ok(self):
        input = 'A Voice for Men'
        index = 'dangerous_organizations'
        

        results = get_candidates(input, index)
        self.assertIsNotNone(results)
        
        expected = {'name': 'A Voice for Men', 'summary': 'Organization', 'label': ['ORGANIZATION']}
        
        self.assertEqual(expected, results[0])

    def test_get_candidates_with_alternate_latin_name_retrieves_ok(self):
        input = 'Uma Voz'
        index = 'dangerous_organizations'
        

        results = get_candidates(input, index)
        self.assertIsNotNone(results)
        
        expected = {'name': 'A Voice for Men', 'summary': 'Organization', 'label': ['ORGANIZATION']}
        
        self.assertEqual(expected, results[0])

    def test_get_information_standard_individual_returns_ok(self):
        entity = 'Curt Doolittle'
        index = 'dangerous_individuals'
        
        result = get_information(entity=entity, index=index)
        print(result)
        self.assertIsNotNone(result)
        
        self.assertIn("""Name: Curt Doolittle
Gender: Male
Summary: CEO at A. O. Smith
Policy Category: HATE""", result)
        
    def test_get_information_standard_organization_returns_ok(self):
        entity = 'Voice for Men'
        index = 'dangerous_organizations'
        
        result = get_information(entity=entity, index=index)
        print(result)
        self.assertIsNotNone(result)
        
        self.assertIn("Name: A Voice for Men", result)

if __name__=='__main__':
      unittest.main()




