# Canvas Quiz and Question Creator

This script allows you to create quizzes and add questions to them in a Canvas course using the Canvas API. The script reads quiz and question data from a JSON file and automates the creation process.

## Features

- Create multiple quizzes from a JSON file.
- Add multiple-choice questions to the created quizzes.
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

4. Prepare a JSON file (`quizzes.json`) with the structure provided in the Canvas REST API documentataion.

## Usage

Run the script from the command line with the required arguments:

```bash
python3 quiz_creator.py <course_id> quizzes.json --assignment_group_id <assignment_group_id>