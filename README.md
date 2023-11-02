# LogicLearner
LogicLearner is a Python repository aimed at teaching and practicing logic concepts, including propositional logic, Boolean algebra, and Disjunctive Normal Form (DNF). The repository contains functionalities for parsing logical expressions, evaluating their truth values, generating questions, and validating user-provided answers.

File Structure
The repository contains several files:

file_manager.py: Manages the storage, serialization, and deserialization of logical question sets using JSON format. It provides classes for handling questions and file I/O operations.

logic_engine.py: Houses functions for logical parsing, evaluating logical expressions, testing for equivalency, and generating logic-related questions.

main.py: Implements a Flask server to expose API endpoints for managing logic-related tasks, such as writing and retrieving question sets, generating random questions, and marking user-provided answers.

API Endpoints
The main.py file contains the following API endpoints:

/post_json: Accepts a POST request to write a JSON-formatted question set.
/get_json: Accepts a GET request to retrieve a question set by its identifier.
/random: Accepts a GET request to retrieve a randomly generated question set.
/mark_answer: Accepts a GET request to mark a user's answer against the correct answer within a question set.
License
This repository is released under the MIT License. For details, please refer to the LICENSE file included in this repository.

Usage and Contributions
To use this repository:

Clone the repository to your local machine.
Explore the file_manager.py and logic_engine.py files to understand the provided functionalities.
Run the Flask server using main.py and access the defined API endpoints to perform various logic-related operations.
Contributions, bug reports, or suggestions are welcome. Please feel free to fork this repository, make changes, and submit pull requests to enhance the functionality and learning experience around logical concepts.

For more detailed information on each module's functionalities and usage, please refer to the comments and function documentation within the respective Python files.

