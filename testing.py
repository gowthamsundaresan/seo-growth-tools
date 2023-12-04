from PIL import Image
from datetime import datetime, timedelta
import random


def get_date():
    # Define the start date and the current date
    start_date = datetime(2023, 10, 1)
    current_date = datetime.now()

    # Calculate the difference in days between the start date and current date
    delta_days = (current_date - start_date).days

    # Generate a random number of days to add to the start date
    random_days = random.randint(0, delta_days)

    # Calculate the random date
    random_date = start_date + timedelta(days=random_days)

    # Format the random date
    formatted_random_date = random_date.strftime("%B %d, %Y")
    return formatted_random_date


def main():
    date = get_date()
    print(date)


if __name__ == "__main__":
    main()