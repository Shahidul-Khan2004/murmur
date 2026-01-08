"""
test.py
Script to test the functions in image_selector.py
"""

from image_selector import select_image


def test_select_image():
    moods = ["positive", "negative", "neutral", "invalid"]

    for mood in moods:
        try:
            print(f"Testing mood: {mood}")
            image_path = select_image(mood)
            print(f"Selected image path: {image_path}\n")
        except FileNotFoundError as e:
            print(f"No images found: {e}\n")


if __name__ == "__main__":
    test_select_image()
