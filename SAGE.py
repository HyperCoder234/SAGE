import pyttsx3
import requests
import re
import os

# Initialize the text-to-speech engine globally
engine = pyttsx3.init()

def save_speech_to_file(text, filename='static/response.mp3'):
    """Convert text to speech and save it to a file."""
    engine.save_to_file(text, filename)
    engine.runAndWait()

def speak(text):
    """Convert text to speech and play it."""
    print(f"Speaking: {text}")
    engine.say(text)
    engine.runAndWait()

def get_weather(city, api_key):
    """Fetch weather information for a city."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()

        if weather_data.get("cod") != 200:
            return f"Oops! I couldn't find weather info for {city}. Double-check the city name and try again."

        # Validate weather data keys
        required_keys = ["main", "wind", "weather"]
        if not all(key in weather_data for key in required_keys):
            return "Invalid weather data received. Please try again."

        temp_min = weather_data["main"]["temp_min"]
        temp_max = weather_data["main"]["temp_max"]
        wind_speed = weather_data["wind"]["speed"]
        condition = weather_data["weather"][0]["main"]

        if condition.lower() in ["clear"]:
            weather_description = "sunny"
        elif condition.lower() in ["clouds"]:
            cloudiness = weather_data["clouds"]["all"]
            if cloudiness < 20:
                weather_description = "partly cloudy"
            else:
                weather_description = "cloudy"
        elif condition.lower() in ["rain"]:
            weather_description = "rainy"
        elif condition.lower() in ["thunderstorm"]:
            weather_description = "thunderstorm"
        else:
            weather_description = condition.lower()

        weather_report = (
            f"Here's a quick update on the weather for {city}:\n"
            f"- Minimum Temperature: {temp_min}°C\n"
            f"- Maximum Temperature: {temp_max}°C\n"
            f"- Wind Speed: {wind_speed} meters per second\n"
            f"- Condition: {weather_description}.\n"
            f"Data provided by OpenWeatherMap. www.openweathermap.org"
        )
        return weather_report

    except requests.exceptions.RequestException as e:
        return f"Oops! There was an issue fetching the weather: {e}"
    except Exception as e:
        return f"Something went wrong while retrieving the weather data: {e}"

def extract_city_from_input(user_input):
    """Extract city name from user input using regex."""
    pattern = r"weather in (.+)|temperature in (.+)|wind in (.+)"
    match = re.search(pattern, user_input, re.IGNORECASE)
    
    if match:
        city = match.group(1) or match.group(2) or match.group(3)
        return city.strip()
    return None

def search_travel_info(query, api_key, cse_id):
    """Perform a Google Custom Search for travel and tourism information and summarize results."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": cse_id,
        "key": api_key,
        "num": 5  # Retrieve multiple results
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "items" in data:
            results = []
            for item in data["items"]:
                title = item.get("title", "No title available")
                snippet = item.get("snippet", "No snippet available")
                formatted_result = (
                    f"- {title}:\n"
                    f"  - Summary: {snippet}\n"
                )
                results.append(formatted_result)
            
            if results:
                return "Here’s what I found for you:\n" + "\n".join(results)
            else:
                return "Hmm, I couldn’t find much on that. Maybe try asking about something else?"
        else:
            return "Sorry, I couldn’t find any information on that topic. How about trying a different query?"
    
    except requests.exceptions.RequestException as e:
        return f"Oops! There was an issue with the request: {e}"
    except Exception as e:
        return f"Something went wrong: {e}"

def search_images(query, api_key, cse_id):
    """Perform a Google Custom Search for images and return image URLs."""
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": query,
        "cx": cse_id,
        "key": api_key,
        "searchType": "image",
        "num": 3,  # Retrieve a few images
        "usageRights": "freeToUse"  # Filter by free-to-use images
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if "items" in data:
            images = []
            for item in data["items"]:
                image_url = item.get("link", "No image available")
                # Add attribution to the image creator, if required
                attribution = item.get("image", {}).get("creator", "")
                if attribution:
                    image_url += f" (Credit: {attribution})"
                images.append(image_url)
            
            if images:
                image_response = "Here are some images I found for you:\n" + "\n".join(images)
                return image_response
            else:
                return "I couldn't find any images on that topic. Maybe try a different search?"
        else:
            return "Sorry, I couldn’t find any images. How about trying a different query?"
    
    except requests.exceptions.RequestException as e:
        return f"Oops! There was an issue with the request: {e}"
    except Exception as e:
        return f"Something went wrong: {e}"

class TravelBot:
    def __init__(self, name, weather_api_key, search_api_key, search_cse_id):
        self.name = name
        self.weather_api_key = weather_api_key
        self.search_api_key = search_api_key
        self.search_cse_id = search_cse_id

    def process_query(self, user_input):
        """Process a single user input query and return a response."""
        response = ""
        if user_input.lower() in ["quit", "exit", "bye"]:
            response = "Goodbye! Have a great day and safe travels. If you need more help, just let me know!"

        # Handle greetings
        elif any(greeting in user_input.lower() for greeting in ["hello", "hi", "hey"]):
            response = f"Hey there! I'm {self.name}. How can I help you with your travel plans today?"

        # Handle queries related to weather
        elif any(word in user_input.lower() for word in ["weather", "temperature", "wind", "cloudy", "sunny", "rain"]):
            city = extract_city_from_input(user_input)
            if city:
                response = get_weather(city, self.weather_api_key)
            else:
                response = "I need a city name to provide the weather report. Could you please tell me the city you're interested in?"

        # Handle general travel information queries
        elif "image" in user_input.lower():
            response = search_images(user_input, self.search_api_key, self.search_cse_id)

        else:
            response = search_travel_info(user_input, self.search_api_key, self.search_cse_id)

        # Save the response as an MP3 file in the static directory
        save_speech_to_file(response, 'static/response.mp3')

        return response

# Load API keys from environment variables
weather_api_key = os.environ.get("WEATHER_API_KEY")
search_api_key = os.environ.get("SEARCH_API_KEY")
search_cse_id = os.environ.get("SEARCH_CSE_ID")

# Create a TravelBot instance
bot = TravelBot("TravelBot", weather_api_key, search_api_key, search_cse_id)

# Test the bot
user_input = "What's the weather like in New York?"
response = bot.process_query(user_input)
print(response)