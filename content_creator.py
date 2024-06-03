import requests
import json
import argparse
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# Canvas API URL and token, be sure to replace the base_url with your Canvas instance URL
base_url = 'https://cti-courses.instructure.com/api/v1'
access_token = os.getenv('CANVAS_API_TOKEN')

if not access_token:
    print("Error: CANVAS_API_TOKEN is not set. Please ensure the .env file contains the correct API token.")
    sys.exit(1)

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

DEFAULT_ASSIGNMENT_GROUP_ID = '92'  # Replace with your actual default assignment group ID

def canvas_api_request(url, data, request_type='post'):
    try:
        if request_type == 'post':
            response = requests.post(url, headers=headers, json=data)
        elif request_type == 'put':
            response = requests.put(url, headers=headers, json=data)
        elif request_type == 'delete':
            response = requests.delete(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported request type: {request_type}")

        print(f"Request URL: {url}")
        print(f"Request Data: {data}")
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Data: {response.text}")

        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f'API request returned an unexpected status code: {response.status_code}')
            print('Response:', response.text)
            return None
    except Exception as e:
        print(f"An error occurred during the API request: {e}")
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
    print(f"Create Quiz Response: {response}")
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
    response = canvas_api_request(url, question_data)
    print(f"Add Question Response: {response}")

def create_assignment(course_id, assignment_group_id, title, description, points_possible, submission_types):
    assignment_data = {
        'assignment': {
            'name': title,
            'description': description,
            'assignment_group_id': assignment_group_id,
            'points_possible': points_possible,
            'submission_types': submission_types,
            'published': False
        }
    }
    url = f'{base_url}/courses/{course_id}/assignments'
    response = canvas_api_request(url, assignment_data)
    print(f"Create Assignment Response: {response}")
    return response['id'] if response else None

def create_discussion(course_id, title, message, discussion_type='side_comment', published=False):
    discussion_data = {
        'title': title,
        'message': message,
        'discussion_type': discussion_type,
        'published': published
    }
    print("Discussion Data:", discussion_data)   
    url = f'{base_url}/courses/{course_id}/discussion_topics'
    response = canvas_api_request(url, discussion_data)
    print(f"Create Discussion Response: {response}")
    return response['id'] if response else None

def main(course_id, data_file, object_type, assignment_group_id=None):
    assignment_group_id = assignment_group_id or DEFAULT_ASSIGNMENT_GROUP_ID
    if not os.path.exists(data_file):
        print(f"Error: Data file '{data_file}' not found.")
        sys.exit(1)

    with open(data_file, 'r') as f:
        data = json.load(f)
    
    print("Loaded Data:", data)   

    if object_type == 'quiz':
        total_quizzes = 0
        for quiz in data.get("quizzes", []):
            total_points = sum(question['points_possible'] for question in quiz['questions'])
            quiz_id = create_quiz(course_id, assignment_group_id, quiz['title'], quiz['description'], total_points)
            if quiz_id:
                total_quizzes += 1
                print(f'Creating quiz: {quiz["title"]} with {len(quiz["questions"])} questions and {total_points} total points.')
                for question in quiz['questions']:
                    add_question(course_id, quiz_id, question)
        print(f'Total quizzes added: {total_quizzes}')
        print(f'Quizzes were added to course ID: {course_id}')

    elif object_type == 'assignment':
        total_assignments = 0
        for assignment in data.get("assignments", []):
            submission_types = assignment.get('submission_types', ['online_text_entry'])
            assignment_id = create_assignment(course_id, assignment_group_id, assignment['title'], assignment['description'], assignment['points_possible'], submission_types)
            if assignment_id:
                total_assignments += 1
                print(f'Creating assignment: {assignment["title"]} with {assignment["points_possible"]} points.')
        print(f'Total assignments added: {total_assignments}')
        print(f'Assignments were added to course ID: {course_id}')

    elif object_type == 'discussion':
        total_discussions = 0
        for discussion in data.get("discussions", []):
            discussion_type = discussion.get('discussion_type', 'side_comment')
            published = discussion.get('published', False)
            print(f"Creating discussion: {discussion['title']}")   
            discussion_id = create_discussion(course_id, discussion['title'], discussion['message'], discussion_type, published)
            if discussion_id:
                total_discussions += 1
                print(f'Created discussion: {discussion["title"]}')
        print(f'Total discussions added: {total_discussions}')
        print(f'Discussions were added to course ID: {course_id}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Canvas Object Creator')
    parser.add_argument('course_id', type=str, help='ID of the course')
    parser.add_argument('object_type', type=str, choices=['quiz', 'assignment', 'discussion'], help='Type of object to create')
    parser.add_argument('data_file', type=str, help='Path to the JSON file containing data for the object')
    parser.add_argument('--assignment_group_id', type=str, help='ID of the assignment group (optional)')

    args = parser.parse_args()

    main(args.course_id, args.data_file, args.object_type, args.assignment_group_id)
