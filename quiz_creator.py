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

DEFAULT_ASSIGNMENT_GROUP_ID = '92'  # Replace with your actual default assignment group ID

def canvas_api_request(url, data, request_type='post'):
    if request_type == 'post':
        response = requests.post(url, headers=headers, data=json.dumps(data))
    elif request_type == 'put':
        response = requests.put(url, headers=headers, data=json.dumps(data))
    elif request_type == 'delete':
        response = requests.delete(url, headers=headers, data=json.dumps(data))
    else:
        raise ValueError(f"Unsupported request type: {request_type}")

    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(f'API request returned an unexpected status code: {response.status_code}')
        print('Response:', response.text)
        return None

def create_quiz(course_id, assignment_group_id, title, description, total_points):
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
            'published': False,
            'points_possible': total_points
        }
    }
    url = f'{base_url}/courses/{course_id}/quizzes'
    response = canvas_api_request(url, quiz_data)
    return response['id'] if response else None

def add_question(course_id, quiz_id, question):
    question_data = {
        'question': {
            'question_name': question['question_name'],
            'question_text': question['question_text'],
            'question_type': question['question_type'],
            'points_possible': question['points_possible']
        }
    }
    if 'answers' in question:
        question_data['question']['answers'] = [
            {
                'answer_text': ans['answer_text'],
                'weight': ans['weight']
            } for ans in question['answers']
        ]
    url = f'{base_url}/courses/{course_id}/quizzes/{quiz_id}/questions'
    canvas_api_request(url, question_data)

def main(course_id, quizzes_file, assignment_group_id=None):
    assignment_group_id = assignment_group_id or DEFAULT_ASSIGNMENT_GROUP_ID
    with open(quizzes_file, 'r') as f:
        quizzes = json.load(f)["quizzes"]

    total_quizzes = 0
    for quiz in quizzes:
        total_points = sum(question['points_possible'] for question in quiz['questions'])
        quiz_id = create_quiz(course_id, assignment_group_id, quiz['title'], quiz['description'], total_points)
        if quiz_id:
            total_quizzes += 1
            print(f'Creating quiz: {quiz["title"]} with {len(quiz["questions"])} questions and {total_points} total points.')
            for question in quiz['questions']:
                add_question(course_id, quiz_id, question)
    print(f'Total quizzes added: {total_quizzes}')
    print(f'Quizzes were added to course ID: {course_id}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Canvas Object Creator')
    parser.add_argument('course_id', type=str, help='ID of the course')
    parser.add_argument('object_type', type=str, choices=['quiz', 'assignment', 'discussion'], help='Type of object to create')
    parser.add_argument('data_file', type=str, help='Path to the JSON file containing data for the object')
    parser.add_argument('--assignment_group_id', type=str, help='ID of the assignment group (optional, required for assignments and quizzes)')

    args = parser.parse_args()

    if args.object_type == 'quiz':
        main(args.course_id, args.data_file, args.assignment_group_id)
    elif args.object_type == 'assignment':
        with open(args.data_file, 'r') as f:
            assignments = json.load(f)["assignments"]
        for assignment in assignments:
            create_assignment(args.course_id, args.assignment_group_id, assignment['title'], assignment['description'], assignment['points_possible'])
    elif args.object_type == 'discussion':
        with open(args.data_file, 'r') as f:
            discussions = json.load(f)["discussions"]
        for discussion in discussions:
            create_discussion(args.course_id, discussion['title'], discussion['message'])
