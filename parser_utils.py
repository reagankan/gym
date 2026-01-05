from bs4 import BeautifulSoup

def parse_html(html_string):
    # Create a BeautifulSoup object
    soup = BeautifulSoup(html_string, 'html.parser')
    
    # Find all <div> elements and extract their text
    div_texts = [div.get_text(strip=True) for div in soup.find_all('div')]
    
    # Filter out empty strings
    return [text for text in div_texts if text]


def parse_workout(lines):

    workout = []
    exercise = []
    for i, line in enumerate(lines):

        # title
        if i == 0:
            workout.append(line)
            continue

        if exercise and line[:3].isalpha():
            workout.append(exercise)
            exercise = []

        exercise.append(line)
    return workout
