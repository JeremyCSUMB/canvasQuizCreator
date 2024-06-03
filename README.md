# Canvas Quiz and Question Creator

This script allows you to create quizzes, assignments, and discussions in a Canvas course using the Canvas API. The script reads data from a JSON file and automates the creation process.

## Features

- Create multiple quizzes from a JSON file.
- Add multiple-choice questions to the created quizzes.
- Create assignments with various submission types.
- Create discussion topics.
- Optionally specify an assignment group ID or use a default one.
- Securely manage API tokens using environment variables.

## Prerequisites

- Python 3.x
- Canvas API token
- Canvas course ID and optional assignment group ID

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-repo/canvas-quiz-creator.git
    cd canvas-quiz-creator
    ```

2. Install the required Python packages:

    ```bash
    pip install requests python-dotenv
    ```

3. Create a `.env` file in the project directory and add your Canvas API token:

    ```plaintext
    CANVAS_API_TOKEN=your_api_token_here
    ```

4. Prepare a JSON file (`data.json`) with the structure provided in the Canvas REST API documentation.

## Usage

Run the script from the command line with the required arguments:

```bash
python3 canvas_creator.py <course_id> <object_type> <data_file> [--assignment_group_id <assignment_group_id>]
```

- `<course_id>`: ID of the Canvas course.
- `<object_type>`: Type of object to create (`quiz`, `assignment`, `discussion`).
- `<data_file>`: Path to the JSON file containing data for the object.
- `--assignment_group_id <assignment_group_id>`: Optional assignment group ID.

Examples:

```bash
python3 canvas_creator.py 12345 quiz quizzes.json --assignment_group_id 92
python3 canvas_creator.py 12345 assignment assignments.json
python3 canvas_creator.py 12345 discussion discussions.json
```
