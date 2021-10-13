import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10
categories_dic = {}
current_category = None

def paginate_questions(request, selection):
  page = request.args.get("page", 1, type=int)
  
  start = (page-1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/*": {'origins': '*'}})
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Acces-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,false')
    response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
    return response

  '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():    
    categories = Category.query.order_by(Category.id).all()
    
    for cat in categories:
      categories_dic[cat.id]=cat.type

    return jsonify({
      'success':True,
      'categories':categories_dic,
    })
  '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():

    all_questions = Question.query.order_by(Question.id).all()
    
    current_qs = paginate_questions(request, all_questions)

    if len(current_qs) == 0:
      abort(404)
    
    categories = Category.query.all()

    for cat in categories:
      categories_dic[cat.id] = cat.type
    
    for question in current_qs:
      current_category = question['category'] 

    return jsonify({
      'success': True,
      'questions':current_qs,
      'total_questions':len(all_questions),
      'categories': categories_dic,
      'current_category':current_category,
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id ).one_or_none()

      if question is None:
        abort(404)

      question.delete()

      return jsonify({
      'success':True
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():

    try:
      body = request.get_json()

      new_question = body.get("question", None)
      new_answer = body.get("answers", None)
      new_category = body.get("category", None)
      new_difficulty = body.get("difficulty", None)
    
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)    
      question.insert()

      return jsonify({
        'success':True,
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a POST? / GET endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_by_term():
    body = request.get_json()
    search_term = body.get('searchTerm', None)

    try:
      if search_term:
        selection = Question.query.filter(Question.question.ilike('%{}%'.format(search_term)))

        current_questions = paginate_questions(request, selection)

        # for question in current_questions:
        #   current_cat = categories_dic[question['category']]  

        return jsonify({
          'success':True,
          'questions':current_questions,
          'total_questions':len(selection.all()),
          # 'current_category':current_cat
        })
    
    except:
      abort(404)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 
  https://knowledge.udacity.com/questions/240434
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def questions_by_category(category_id):

    category_id = str(category_id)
    print(type(category_id))

    all_questions = Question.query.filter(Question.category == category_id).order_by(Question.id).all()
    paginated_questions = paginate_questions(request, all_questions)
    
    return jsonify({
      'success':True,
      'questions':paginated_questions,
      'total_questions':len(all_questions),
      'current_category': category_id,
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['GET','POST'])
  def play_quiz():
    body = request.get_json()

    previous_question = body.get('previous_questions', [])
    quiz_category = body.get('quiz_category', None)

    try:
      category_id = int(quiz_category['id'])      
      
      if quiz_category == 0:
        quiz = Question.query.all()

      else:
        quiz = Question.query.filter_by(category = category_id).all()

      if not quiz:
        abort(422)
      
      selected = []

      for question in quiz:
        if question.id not in previous_question:
          selected.append(question.format())

      if len(selected) != 0:
        random_questions = random.choice(selected)
        return jsonify({
          'success':True, 
          'question':random_questions
        })   

      else:
        return jsonify({
        'success':False,
        'questions': []
      })
    
    except:
      abort(422)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def page_not_found(error):
    return(jsonify({'success':False, 'error':'404', 'message':'Page not found'}),404)

  @app.errorhandler(422)
  def unprocessable(error):
    return (jsonify({'success':False, 'error':'422', 'message':'Unprocessable'}),422)

  @app.errorhandler(400)
  def bad_request(error):
    return (jsonify({'success':False, 'error':'400', 'message':'Bad request'}),400)

  return app

    