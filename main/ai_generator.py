import google.generativeai as genai

genai.configure(api_key="AIzaSyAupYlCpsWvqEAO3FyIjH6AW4e4teMBHG8")

def generate_bike_comparison(bike1, bike2):
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Create a detailed prompt for comparison
    prompt = f"""You are an agent of a Bike Rental System called WheelStreet!
    Your duty is to compare the 2 bikes given to you for the customers to help them with their rental choice. 
    Compare the following two bikes:

    Bike 1:
    Brand: {bike1['brand']}
    Model: {bike1['model']}
    Mileage: {bike1['mileage']} kmpl
    Rental price per hour: Rs. {bike1['price_per_hour']}

    Bike 2:
    Brand: {bike2['brand']}
    Model: {bike2['model']}
    Mileage: {bike2['mileage']} kmpl
    Rental price per hour: Rs. {bike2['price_per_hour']}

    Please provide a brief but precise and impartial comparison of these two bikes based on the aspects listed above like a concluding summary. 
    It should not exceed 300 words. 
    Do not give any headings or any other formatting to the text.
    """

    # Generate the AI response
    response = model.generate_content(prompt)

    return response.text

