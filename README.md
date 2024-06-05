# Exam Score Checker
## Overview
The Exam Score Checker is a tool designed to streamline the process of grading and analyzing responses from the Joint Entrance Examination (JEE) Response Sheets. This tool compares the answer key with response sheets to calculate scores automatically, simplifying the evaluation process for educators and students alike.<br>
Visit [Exam Score Checker](https://exam-score-checker.onrender.com/)

## Features
- **Automated Response Evaluation**: The program automates the evaluation process, saving time and effort in manually grading exam papers.
- **Detailed Feedback**: Provides detailed feedback to the user, highlighting both correct and incorrect answers.
- **User-Friendly Interface**: Offers a simple and intuitive interface for ease of use.

## Usage
1. **Enter URL**: Enter URL to the response sheet of the JEE exam.
   
<img width="1278" alt="Enter URL" src="https://github.com/emohk/exam_score_checker/assets/168178777/121091c5-8b20-4b42-b9d9-3ef47cf337ea">
  
2. **View Detailed Analysis**: Click on `View Marked Response Sheet` to view detailed analysis.
  
<img width="1277" alt="Result" src="https://github.com/emohk/exam_score_checker/assets/168178777/00548ca8-d65c-418e-b1a3-e2c8ed34c579">

3. **Review Marked Response**: Review the marked response provided by the program, which includes marked correct and incorrect answers.
   
<img width="1219" alt="Detailed Analysis" src="https://github.com/emohk/exam_score_checker/assets/168178777/1b317fc0-c74a-4772-8b47-ff6ed34b9877">
   
## Moderator Usage
   Moderators can add and remove answers key
     
<img width="1279" alt="Add Answer Key" src="https://github.com/emohk/exam_score_checker/assets/168178777/309720c1-72e1-4888-9187-7a8c66971bbc">

## Code
This app is built with Flask, Python and Bootstrap

### Python libraries used
- re
- beautifulsoup4
- Flask
- gunicorn
- Jinja2
- requests
- urllib3
- Werkzeug

### `app.py`
This file initializes the Flask application, defines routes, and handles requests.

### `check_url.py`
This file contains functions which is used for grading the user's response sheet.

### `key_manager.py`
This file handles most of the database work and queries.

### `/templates/`
This folder contains all the `.html` files.
