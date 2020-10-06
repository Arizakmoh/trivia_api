import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia_api test case"""

    def setUp(self):
    
        """Define test variables and initialize app."""
        
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        #self.database_path = 'postgresql://postgres:123456@localhost:5432/trivia'
        setup_db(self.app, self.database_path)

        # sample question to use in test case
        
        self.new_question = {
            'question': 'When did Somalia take independence?',
            'answer': 'July 1, 1960',
            'difficulty': 2,
            'category': '4'
        }

        #  app to context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
         """Executed after reach test"""
        pass

    #----------------------------------------------------------------------------#
    # TODO Write at least one test for each test for successful operation and for expected errors.
    #----------------------------------------------------------------------------#
    
    # 1 )
    #----------------------------------------------------------------------------#
    # question pagination success / failure
    #----------------------------------------------------------------------------#
    
    
    def test_get_paginated_questions(self):
        """Tests question pagination success"""

        # get response and load data
        response = self.client().get('/questions')
        data = json.loads(response.data)

        # fetch status / response code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check questions return data
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
     
    def test_404_request_beyond_valid_page(self):
        """Tests question pagination if failure 404 """

        response = self.client().get('/questions?page=100')
        data = json.loads(response.data)

        # fetch status / response code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        
        
    # 2 )
    #----------------------------------------------------------------------------#
    # question deletion success / failure
    #----------------------------------------------------------------------------#
    
    def test_delete_question(self):
        """Tests question deletion success"""

        question = Question(question=self.new_question['question'], answer=self.new_question['answer'],
                            category=self.new_question['category'], difficulty=self.new_question['difficulty'])
        question.insert()

        # get the id of the new question
        q_id = question.id

        # display all questions
        questions_before = Question.query.all()

        # delete the question  
        response = self.client().delete('/questions/{}'.format(q_id))
        data = json.loads(response.data)

        # display query after you deleted
        questions_after = Question.query.all()

        # check if the question has been deleted successfully
        question = Question.query.filter(Question.id == 1).one_or_none()

        # fetch status / response code  and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check question id 
        self.assertEqual(data['deleted'], q_id)

        # check if questions are empty after delete
        self.assertEqual(question, None)
        
        
    # 3 )
    #----------------------------------------------------------------------------#
    # question creation success / failure
    #----------------------------------------------------------------------------#
    def test_create_new_question(self):
        """Tests question creation success"""

        # display all questions
        questions_before = Question.query.all()

        # create new question  
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        # display questions after insertion
        questions_after = Question.query.all()

        # check if the question has been inserted successfully
        question = Question.query.filter_by(id=data['created']).one_or_none()

        # fetch status / response code code and success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

      

        # check that question is empty
        self.assertIsNotNone(question)

    def test_422_if_question_creation_fails(self):
        """Tests question creation failure 422"""

        # display all questions
        questions_before = Question.query.all()

        # create new question without json data, then load response data
        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        # display all questions
        questions_after = Question.query.all()

        # fetch status / response code and success message
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

        # check if questions_after and questions_before are equal
        self.assertTrue(len(questions_after) == len(questions_before))
        
        
    # 4 )
    #----------------------------------------------------------------------------#
    # question search success / failure
    #----------------------------------------------------------------------------#
    
    
    def test_search_questions(self):
        """Tests search questions success"""

        # send post request with search term
        response = self.client().post('/questions',
                                      json={'searchTerm': 'egyptians'})

        # load response data
        data = json.loads(response.data)

        # fetch response / status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that id of question in response is correct
        self.assertEqual(data['questions'][0]['id'], 23)

    def test_404_if_search_questions_fails(self):
        """Tests search questions failure 404"""

        # send post request with search term that should fail
        response = self.client().post('/questions',
                                      json={'searchTerm': 'abcdefghijk'})

        # return json response data
        data = json.loads(response.data)

        # fetch response status code and message
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')
        
    # 5 )
    #----------------------------------------------------------------------------#
    # getting questions by category success / failure
    #----------------------------------------------------------------------------#
    
    def test_get_questions_by_category(self):
        """Tests getting questions by category success"""

        # send request with category id 1 for science
        response = self.client().get('/categories/1/questions')

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that questions are returned (len != 0)
        self.assertNotEqual(len(data['questions']), 0)

        # check that current category returned is science
        self.assertEqual(data['current_category'], 'Science')

    def test_400_if_questions_by_category_fails(self):
        """Tests getting questions by category failure 400"""

        # send request with category id 100
        response = self.client().get('/categories/100/questions')

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')
        
        
    # 6 )
    #----------------------------------------------------------------------------#
    # playing quiz game success / failure
    #----------------------------------------------------------------------------#
    
    def test_play_quiz_game(self):
        """Tests playing quiz game success"""

        # send post request with category and previous questions
        response = self.client().post('/quizzes',
                                      json={'previous_questions': [20, 21],
                                            'quiz_category': {'type': 'Science', 'id': '1'}})

        # load response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        # check that a question is returned
        self.assertTrue(data['question'])

        # check that the question returned is in correct category
        self.assertEqual(data['question']['category'], 1)

        # check that question returned is not on previous q list
        self.assertNotEqual(data['question']['id'], 20)
        self.assertNotEqual(data['question']['id'], 21)

    def test_play_quiz_fails(self):
        """Tests playing quiz game failure 400"""

        # send post request without json data
        response = self.client().post('/quizzes', json={})

        # return join response data
        data = json.loads(response.data)

        # check response status code and message
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
