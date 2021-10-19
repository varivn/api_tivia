import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {"question":"Who scored the first goal in a World Cup", "answer":"Lucien Laurent", "category":6, "difficulty":4}

        self.bad_question = {"question":"", "answer":"", "category":2, "difficulty":1}
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    # Testing retrieve categories
    def test_get_categories(self):
      res = self.client().get('/categories')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['categories'])
    
    # Testing retrieve paginated questions
    def test_get_questions(self):
      res = self.client().get('/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['questions'])
      self.assertTrue(data['total_questions'])
      self.assertTrue(data['current_category'])

    # Testing fail 404 retrieve paginated questions
    def test_404_get_questions(self):
      res = self.client().get('/questions?page=1000')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertTrue(data['message'])
      self.assertEqual(data['error'], '404')

    # Testing delete questions
    # def test_delete_question(self):
    #   res = self.client().delete('/questions/23')
    #   data = json.loads(res.data)

    #   self.assertEqual(res.status_code, 200)
    #   self.assertEqual(data['success'], True)
    #   self.assertTrue(data['question_id'])

    # Testing fail questions deletion
    def test_422_delete_question(self):
      res = self.client().delete('/questions/1000')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 422)
      self.assertEqual(data['success'], False)
      self.assertTrue(data['message'])
      self.assertEqual(data['error'], '422')

    # Testing retrieve questions by category
    def test_get_questions_by_category(self):
      res = self.client().get('categories/3/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['questions'])
      self.assertTrue(data['current_category'])

    def test_422_get_questions_by_category(self):
      # TODO
      id_category = None
      res = self.client().get(f'categories/{id_category}/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 404)
      self.assertEqual(data['success'], False)
      self.assertTrue(data['error'])
      self.assertEqual(data['error'], '404')
      self.assertTrue(data['message'])
      self.assertEqual(data['message'], 'Page not found')
    
    # Testing questions creation
    def test_create_question(self):
      res = self.client().post('/questions', json=self.new_question)
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
    
    # Testing no empty field in question creation
    def test_createquestion_empty_fields(self):
      res = self.client().post('/questions', json=self.bad_question)
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 422)
      self.assertEqual(data['success'], False)
      self.assertTrue(data['message'])
      self.assertEqual(data['message'], 'Unprocessable')
      self.assertEqual(data['error'], '422')

    # Testing fail question creation by 422 http status code
    def test_422_create_question(self):
      res = self.client().post('/questions')
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 422)
      self.assertEqual(data['success'], False)
      self.assertTrue(data['message'])
      self.assertEqual(data['message'], 'Unprocessable')
      self.assertEqual(data['error'], '422')
    
    # Testing retrieve questions by category
    def test_question_search(self):
      res = self.client().post('/questions/search', headers={'Content-Type': 'application/json'}, json={"searchTerm": "soccer"})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['questions'])
    
    def test_question_search_no_matches(self):
      res = self.client().post('/questions/search', json={"searchTerm": "pizza"})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(len(data['questions']) == 0)

    # Test play quizzes endpoint
    def test_play(self):
      quizz_data = {
            'previous_questions': [],
            'quiz_category': {
                'type':'Entertainment',
                'id': 5
            }
      }
      res = self.client().post('/quizzes', json=quizz_data, headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)
      
      self.assertEqual(res.status_code, 200)
      self.assertEqual(data['success'], True)
      self.assertTrue(data['question'])

    #Test play quizzes fail
    def test_400_test_play(self):
      res = self.client().post('/quizzes', headers={'Content-Type': 'application/json'})
      data = json.loads(res.data)

      self.assertEqual(res.status_code, 400)
      self.assertEqual(data['success'], False)
      self.assertTrue(data['message'])
      self.assertEqual(data['message'], 'Bad request')
      self.assertEqual(data['error'], '400')

# Make the tests conveniently executable
if __name__ == "__main__":
  unittest.main()