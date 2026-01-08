from image_selector import select_image

# List of moods to test
moods = ["positive", "negative", "neutral", "invalid"]

for mood in moods:
    print(f"Testing mood: {mood}")
    try:
        img_path = select_image(mood)
        print(f"Selected image: {img_path}\n")
    except Exception as e:
        print(f"Error: {e}\n")
