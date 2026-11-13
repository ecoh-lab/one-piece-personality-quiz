"""What One Piece Character Are You? - a Drafter personality quiz.

All changing app data lives in the State dataclass. Character choices are
matched against each Character instance's traits to calculate the result.
"""

from dataclasses import dataclass
from drafter import *


@dataclass
class Character:

    name: str
    description: str
    traits: list[str]
    score: int
    image_url: str
    background: str


@dataclass
class State:

    user_name: str
    current_page: str
    quiz_answers: list[str]
    characters: list[Character]
    result: str
    feedback: str


set_website_title("One Piece Personality Quiz")
set_site_information(
    author="Ethan Cohen",
    description="A personality quiz that tells you which One Piece character you relate to!",
    sources="Thanks to the Drafter docs.",
    planning="",
    links=["https://github.com/ecoh-lab/one-piece-personality-quiz"]
)
hide_debug_information()
set_website_framed(False)


@route
def home(state: State) -> Page:
    """
    Welcome page and name input.
    
    Args:
        state (State)
    Returns:
        Page (home page)
    """
    state.current_page = "home"
    content = [
        Header("What One Piece Character Are You?"),
        "Set sail on a five-question personality quiz and find out which "
        "Straw Hat shares your style.",
        "Enter your name:",
        TextBox("name", state.user_name),
        Button("Start the quiz", "start_quiz"),
        Button("Browse the crew", "character_directory"),
    ]
    if state.feedback:
        content.insert(1, state.feedback)
    return Page(state, content)


@route
def index(state: State) -> Page:
    """
    Drafter opens the route named index at the site root.
    
    Args:
        state (State)
    Returns:
        Page
    """
    return home(state)


@route
def start_quiz(state: State, name: str) -> Page:
    """
    Validate the name, then continue to the instructions.
    
    Args:
        state (State)
        name (str): Name the user enters.
    Returns:
        Page (home page)
    """
    if name.strip() == "":
        state.feedback = "Please enter your name before starting the quiz."
        return home(state)

    state.user_name = name.strip()
    state.feedback = ""
    return instructions(state)


@route
def instructions(state: State) -> Page:
    """
    Explain the quiz before the visitor begins.
    
    Args:
        state (State)
    Returns:
        Page (instructions page)
    """
    state.current_page = "instructions"
    content = [
        Header("Before you set sail"),
        "You will answer five multiple-choice questions about how you "
        "think, work with a crew, and handle a challenge.",
        "Choose the answer that feels most like you. Each answer adds a "
        "point to one character. Your highest-scoring match will appear "
        "at the end.",
        Button("Begin the five questions", "quiz"),
        Button("Back to home", "home"),
        Button("Browse the crew", "character_directory"),
    ]
    if state.user_name:
        content.insert(1, "Welcome aboard, " + state.user_name + "!")
    return Page(state, content)


@route
def quiz(state: State) -> Page:
    """
    Show five multiple-choice questions using SelectBox inputs.
    
    Args:
        state (State)
    Returns:
        Page (quiz page)
    """
    state.current_page = "quiz"
    placeholder = "-- Choose an answer --"

    # The option text matches one of the traits stored on a Character.
    questions = [
        (
            "1. When a challenge appears, what is your first instinct?",
            [
                placeholder,
                "I trust my instincts and leap into action.",
                "I stay focused and push through the challenge.",
                "I check that everyone is safe before acting.",
                "I scan the situation and make a smart plan.",
                "I notice who needs support and step in.",
            ],
        ),
        (
            "2. Which approach sounds most like you?",
            [
                placeholder,
                "A big dream matters more to me than playing it safe.",
                "Practice and discipline are the best way forward.",
                "A little kindness can turn someone's day around.",
                "I protect my resources and think several steps ahead.",
                "I ask questions and learn before I decide.",
            ],
        ),
        (
            "3. How do you show loyalty to people you care about?",
            [
                placeholder,
                "I stand up for my friends without hesitation.",
                "I prove loyalty by keeping my promises.",
                "I show I care by helping in practical ways.",
                "I use quick thinking to get the group out of trouble.",
                "I care deeply and want to help people heal.",
            ],
        ),
        (
            "4. What role do you tend to play on a team?",
            [
                placeholder,
                "I make the team feel brave by believing in them.",
                "I work quietly until people can rely on me.",
                "I keep the group going with warmth and humor.",
                "I organize the details so everyone can move.",
                "I may get nervous, but I still show up for friends.",
            ],
        ),
        (
            "5. Pick the value that matters most to you.",
            [
                placeholder,
                "I choose freedom and adventure over a predictable path.",
                "I pick a tough goal and stick with it.",
                "I put myself on the line for people I care about.",
                "I value security, independence, and a good map.",
                "I stay curious and compassionate under pressure.",
            ],
        ),
    ]

    content = [
        Header("Your five questions"),
        "Choose one answer for every question, then submit your choices.",
    ]
    if state.feedback:
        content.append(state.feedback)
        state.feedback = ""

    for index, (question, options) in enumerate(questions):
        content.append(question)
        if index < len(state.quiz_answers):
            selected_answer = state.quiz_answers[index]
        else:
            selected_answer = placeholder
        content.append(
            SelectBox("q" + str(index + 1), options, selected_answer)
        )

    content.extend(
        [
            Button("Submit my answers", "submit_quiz"),
            Button("Back to instructions", "instructions"),
        ]
    )
    return Page(state, content)


@route
def submit_quiz(
    state: State,
    q1: str,
    q2: str,
    q3: str,
    q4: str,
    q5: str,
) -> Page:
    """
    Save the five answers, score characters, and show the result.
    
    Args:
        state (State)
        q1 (str): the first question answer
        q2 (str): the second question answer
        q3 (str): the third question answer
        q4 (str): the fourth question answer
        q5 (str): the fifth question answer
    Returns:
        Page (quiz page)
    """
    state.quiz_answers = [q1, q2, q3, q4, q5]

    if "-- Choose an answer --" in state.quiz_answers:
        state.feedback = "Please answer all five questions before submitting."
        return quiz(state)

    for character in state.characters:
        character.score = 0

    # Compare every answer with each character's trait list.
    for character in state.characters:
        for answer in state.quiz_answers:
            if answer in character.traits:
                character.score += 1

    best_match = state.characters[0]
    for character in state.characters:
        if character.score > best_match.score:
            best_match = character

    state.result = best_match.name
    return results(state)


@route
def results(state: State) -> Page:
    """
    Display the best match and its personality traits.
    
    Args:
        state (State)
    Returns:
        Page (results page)
    """
    state.current_page = "results"
    if state.result == "":
        return Page(
            state,
            [
                Header("No result yet"),
                "Complete the quiz to see your character match.",
                Button("Go to the quiz", "quiz"),
            ],
        )

    matched_character = None
    for character in state.characters:
        if character.name == state.result:
            matched_character = character

    if matched_character is None:
        return Page(
            state,
            [
                Header("Match not found"),
                "Please take the quiz again.",
                Button("Restart", "restart"),
            ],
        )

    content = [
        Header("Your Straw Hat match"),
        "Great sailing, " + state.user_name + "! Your closest match is "
        + matched_character.name + ".",
        Image(
            matched_character.image_url,
            260,
            alt="Portrait of " + matched_character.name,
        ),
        matched_character.description,
        "Your matching traits:",
    ]
    for trait in matched_character.traits:
        content.append("- " + trait)

    content.extend(
        [
            "Quiz score: " + str(matched_character.score) + " out of 5",
            Button("Take the quiz again", "restart"),
            Button("Browse all five characters", "character_directory"),
        ]
    )
    return Page(state, content)


@route
def character_directory(state: State) -> Page:
    """
    Show all five possible results and link to their detail pages.
    
    Args:
        state (State)
    Returns:
        Page (character directory page)
    """
    state.current_page = "character_directory"
    content = [
        Header("Meet the Straw Hat crew"),
        "Choose a character to read more about their personality.",
    ]

    for character in state.characters:
        content.append(Header(character.name))
        content.append(
            Image(
                character.image_url,
                150,
                alt="Portrait of " + character.name,
            )
        )
        content.append(character.description)
        content.append(
            Button(
                "Read about " + character.name,
                "character_details",
                [Argument("character_name", character.name)],
            )
        )

    content.extend(
        [
            Button("Back to home", "home"),
            Button("Start the quiz", "instructions"),
        ]
    )
    return Page(state, content)


@route
def character_details(state: State, character_name: str) -> Page:
    """
    Show the selected character's background and matching traits.
    
    Args:
        state (State)
        character_name (str): name of the selected character
    Returns:
        Page (character details page)
    """
    state.current_page = "character_details"
    selected_character = None

    for character in state.characters:
        if character.name == character_name:
            selected_character = character

    if selected_character is None:
        return Page(
            state,
            [
                Header("Character not found"),
                "Choose someone from the directory to see their details.",
                Button("Open the character directory", "character_directory"),
            ],
        )

    content = [
        Header(selected_character.name),
        Image(
            selected_character.image_url,
            260,
            alt="Portrait of " + selected_character.name,
        ),
        selected_character.description,
        selected_character.background,
        "Personality traits:",
    ]
    for trait in selected_character.traits:
        content.append("- " + trait)

    content.extend(
        [
            Button("Back to the directory", "character_directory"),
            Button("Take the quiz", "instructions"),
        ]
    )
    return Page(state, content)


@route
def restart(state: State) -> Page:
    """
    Reset quiz data and return to the home page.
    
    Args:
        state (State)
    Returns:
        Page (home page)
    """
    if state.result != "":
        state.quiz_answers = []
        state.result = ""
        state.user_name = ""
        for character in state.characters:
            character.score = 0
        state.feedback = "The quiz is reset. Enter a name to set sail again."
    else:
        state.feedback = "The quiz is already reset. Enter your name to begin."

    state.current_page = "home"
    return home(state)


# Drafter unit tests: routes are ordinary functions, so call them with a test
# State and check the returned Page or the state changes directly.
def make_test_state() -> State:
    """Create isolated characters and state for route tests."""
    return State(
        user_name="",
        current_page="home",
        quiz_answers=[],
        characters=[
            Character(
                "Monkey D. Luffy",
                "A brave captain.",
                [
                    "I trust my instincts and leap into action.",
                    "A big dream matters more to me than playing it safe.",
                    "I stand up for my friends without hesitation.",
                    "I make the team feel brave by believing in them.",
                    "I choose freedom and adventure over a predictable path.",
                ],
                0,
                "assets/luffy.png",
                "Luffy's test background.",
            ),
            Character(
                "Roronoa Zoro",
                "A focused swordsman.",
                ["zoro-trait"],
                0,
                "assets/zoro.png",
                "Zoro's test background.",
            ),
            Character(
                "Vinsmoke Sanji",
                "A caring cook.",
                ["sanji-trait"],
                0,
                "assets/sanji.png",
                "Sanji's test background.",
            ),
            Character(
                "Nami",
                "A clever navigator.",
                ["nami-trait"],
                0,
                "assets/nami.png",
                "Nami's test background.",
            ),
            Character(
                "Tony Tony Chopper",
                "A kind doctor.",
                ["chopper-trait"],
                0,
                "assets/chopper.png",
                "Chopper's test background.",
            ),
        ],
        result="",
        feedback="",
    )


def test_home_route() -> None:
    """Tests home route function"""
    page = home(make_test_state())
    assert_has(page, Header("What One Piece Character Are You?"))
    assert_has(page, Button("Start the quiz", "start_quiz"))


def test_index_route() -> None:
    """Tests index route function"""
    page = index(make_test_state())
    assert_has(page, Header("What One Piece Character Are You?"))
    assert_equal(page.state.current_page, "home")


def test_start_quiz_route() -> None:
    """Tests start quiz route function"""
    valid_page = start_quiz(make_test_state(), "  Ada  ")
    assert_equal(valid_page.state.user_name, "Ada")
    assert_has(valid_page, Header("Before you set sail"))

    invalid_page = start_quiz(make_test_state(), "   ")
    assert_has(invalid_page, "Please enter your name")


def test_instructions_route() -> None:
    """Tests instructions route function"""
    page = instructions(make_test_state())
    assert_has(page, Button("Begin the five questions", "quiz"))
    assert_equal(page.state.current_page, "instructions")


def test_quiz_route() -> None:
    """Tests quiz route function"""
    page = quiz(make_test_state())
    assert_has(page, "1. When a challenge appears")
    assert_has(page, "5. Pick the value that matters most to you.")
    assert_has(page, Button("Submit my answers", "submit_quiz"))


def test_submit_quiz_route() -> None:
    """Tests submit quiz route function"""
    state = make_test_state()
    page = submit_quiz(
        state,
        "I trust my instincts and leap into action.",
        "A big dream matters more to me than playing it safe.",
        "I stand up for my friends without hesitation.",
        "I make the team feel brave by believing in them.",
        "I choose freedom and adventure over a predictable path.",
    )
    assert_equal(page.state.result, "Monkey D. Luffy")
    assert_equal([character.score for character in page.state.characters], [5, 0, 0, 0, 0])
    assert_has(page, Header("Your Straw Hat match"))

    incomplete_page = submit_quiz(
        make_test_state(),
        "-- Choose an answer --",
        "A big dream matters more to me than playing it safe.",
        "I stand up for my friends without hesitation.",
        "I make the team feel brave by believing in them.",
        "I choose freedom and adventure over a predictable path.",
    )
    assert_has(incomplete_page, "Please answer all five questions")


def test_results_route() -> None:
    """Tests results route function"""
    state = make_test_state()
    state.user_name = "Ada"
    state.result = "Nami"
    page = results(state)
    assert_has(page, "Your closest match is Nami.")
    assert_has(page, Image("assets/nami.png", 260, alt="Portrait of Nami"))


def test_character_directory_route() -> None:
    """Tests character directory route function"""
    page = character_directory(make_test_state())
    assert_has(page, Header("Monkey D. Luffy"))
    assert_has(page, Header("Tony Tony Chopper"))
    assert_has(
        page,
        Button(
            "Read about Nami",
            "character_details",
            [Argument("character_name", "Nami")],
        ),
    )


def test_character_details_route() -> None:
    """Tests character details route function"""
    page = character_details(make_test_state(), "Tony Tony Chopper")
    assert_has(page, Header("Tony Tony Chopper"))
    assert_has(page, "Chopper's test background.")

    missing_page = character_details(make_test_state(), "Not a crew member")
    assert_has(missing_page, Header("Character not found"))


def test_restart_route() -> None:
    """Tests restart route function"""
    state = make_test_state()
    state.user_name = "Ada"
    state.quiz_answers = ["I trust my instincts and leap into action."]
    state.result = "Monkey D. Luffy"
    for character in state.characters:
        character.score = 3

    page = restart(state)
    assert_equal(page.state.user_name, "")
    assert_equal(page.state.quiz_answers, [])
    assert_equal(page.state.result, "")
    assert_equal([character.score for character in page.state.characters], [0, 0, 0, 0, 0])
    assert_has(page, "The quiz is reset")


test_home_route()
test_index_route()
test_start_quiz_route()
test_instructions_route()
test_quiz_route()
test_submit_quiz_route()
test_results_route()
test_character_directory_route()
test_character_details_route()
test_restart_route()


start_server(
    State(
        user_name="",
        current_page="home",
        quiz_answers=[],
        characters=[
            Character(
                name="Monkey D. Luffy",
                description=(
                    "A joyful, bold captain who follows his instincts and "
                    "believes strongly in his friends."
                ),
                traits=[
                    "I trust my instincts and leap into action.",
                    "A big dream matters more to me than playing it safe.",
                    "I stand up for my friends without hesitation.",
                    "I make the team feel brave by believing in them.",
                    "I choose freedom and adventure over a predictable path.",
                ],
                score=0,
                image_url="assets/luffy.png",
                background=(
                    "Luffy is the captain of the Straw Hat Pirates. His "
                    "ambition is to find the One Piece and become King of "
                    "the Pirates, and he is fiercely loyal to his crew."
                ),
            ),
            Character(
                name="Roronoa Zoro",
                description=(
                    "A determined swordsman known for his discipline, "
                    "strength, and unwavering loyalty."
                ),
                traits=[
                    "I stay focused and push through the challenge.",
                    "Practice and discipline are the best way forward.",
                    "I prove loyalty by keeping my promises.",
                    "I work quietly until people can rely on me.",
                    "I pick a tough goal and stick with it.",
                ],
                score=0,
                image_url="assets/zoro.png",
                background=(
                    "Zoro is the crew's swordsman. He trains toward his "
                    "goal of becoming the world's greatest swordsman and "
                    "takes his promises seriously."
                ),
            ),
            Character(
                name="Vinsmoke Sanji",
                description=(
                    "A resourceful cook with a generous heart who looks "
                    "after the people around him."
                ),
                traits=[
                    "I check that everyone is safe before acting.",
                    "A little kindness can turn someone's day around.",
                    "I show I care by helping in practical ways.",
                    "I keep the group going with warmth and humor.",
                    "I put myself on the line for people I care about.",
                ],
                score=0,
                image_url="assets/sanji.png",
                background=(
                    "Sanji is the Straw Hat Pirates' cook. He is a skilled "
                    "fighter who values food, hospitality, and protecting "
                    "his friends."
                ),
            ),
            Character(
                name="Nami",
                description=(
                    "A clever, independent navigator who plans ahead and "
                    "keeps the crew on course."
                ),
                traits=[
                    "I scan the situation and make a smart plan.",
                    "I protect my resources and think several steps ahead.",
                    "I use quick thinking to get the group out of trouble.",
                    "I organize the details so everyone can move.",
                    "I value security, independence, and a good map.",
                ],
                score=0,
                image_url="assets/nami.png",
                background=(
                    "Nami is the Straw Hat Pirates' navigator. She is "
                    "skilled at reading weather and charts, and she dreams "
                    "of making a map of the entire world."
                ),
            ),
            Character(
                name="Tony Tony Chopper",
                description=(
                    "A curious, kind-hearted doctor who wants to help "
                    "people and learn about the world."
                ),
                traits=[
                    "I notice who needs support and step in.",
                    "I ask questions and learn before I decide.",
                    "I care deeply and want to help people heal.",
                    "I may get nervous, but I still show up for friends.",
                    "I stay curious and compassionate under pressure.",
                ],
                score=0,
                image_url="assets/chopper.png",
                background=(
                    "Chopper is the crew's doctor, a reindeer who gained "
                    "human-like abilities after eating a Devil Fruit. He "
                    "studies medicine so he can treat people in need."
                ),
            ),
        ],
        result="",
        feedback="",
    )
)



