import requests
import json
import argparse
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Canvas API URL and token, be sure to replace the base_url with your Canvas instance URL
base_url = 'https://cti-courses.instructure.com/api/v1'
access_token = os.getenv('CANVAS_API_TOKEN')

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

DEFAULT_ASSIGNMENT_GROUP_ID = 'default_assignment_group_id'  # Replace with your actual default assignment group ID

def create_quiz(course_id, assignment_group_id, title, description):
    quiz_data = {
        'quiz': {
            'title': title,
            'description': description,
            'quiz_type': 'assignment',
            'assignment_group_id': assignment_group_id,
            'time_limit': None,
            'shuffle_answers': True,
            'hide_results': 'always',
            'show_correct_answers': False,
            'allowed_attempts': 1,
            'scoring_policy': 'keep_highest',
            'one_question_at_a_time': False,
            'published': True,
            'points_possible': 10.0
        }
    }
    response = requests.post(f'{base_url}/courses/{course_id}/quizzes', headers=headers, data=json.dumps(quiz_data))
    if response.status_code in [200, 201]:
        return response.json()['id']
    else:
        print('Quiz creation returned an unexpected status code')
        print('Status Code:', response.status_code)
        print('Response:', response.text)
        return None

def add_question(course_id, quiz_id, question_name, question_text, question_type, points_possible, answers):
    question_data = {
        'question': {
            'question_name': question_name,
            'question_text': question_text,
            'question_type': question_type,
            'points_possible': points_possible,
            'answers': [
                {
                    'answer_text': ans['text'],
                    'weight': ans['weight'],
                    'answer_correct': ans['is_correct']
                } for ans in answers
            ]
        }
    }
    response = requests.post(f'{base_url}/courses/{course_id}/quizzes/{quiz_id}/questions', headers=headers, data=json.dumps(question_data))
    if response.status_code in [200, 201]:
        print(f'Question added successfully: {question_name}')
    else:
        print(f'Failed to add question: {question_name}')
        print('Status Code:', response.status_code)
        print('Response:', response.text)

def main(course_id, quizzes_file, assignment_group_id=None):
    assignment_group_id = assignment_group_id or DEFAULT_ASSIGNMENT_GROUP_ID
    with open(quizzes_file, 'r') as f:
        quizzes = json.load(f)

    for quiz in quizzes:
        quiz_id = create_quiz(course_id, assignment_group_id, quiz['title'], quiz['description'])
        if quiz_id:
            for question in quiz['questions']:
                add_question(
                    course_id,
                    quiz_id,
                    question['question_name'],
                    question['question_text'],
                    question['question_type'],
                    question['points_possible'],
                    question['answers']
                )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Canvas Quiz and Question Creator')
    parser.add_argument('course_id', type=str, help='ID of the course')
    parser.add_argument('quizzes_file', type=str, help='Path to the JSON file containing quizzes and questions')
    parser.add_argument('--assignment_group_id', type=str, help='ID of the assignment group (optional)')

    args = parser.parse_args()
    main(args.course_id, args.quizzes_file, args.assignment_group_id)