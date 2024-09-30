import google.generativeai as genai

genai.configure(api_key="AIzaSyAupYlCpsWvqEAO3FyIjH6AW4e4teMBHG8")

def generate_response():
    model = genai.GenerativeModel('gemini-1.5-flash')

    prompt = "Give a very small phrase on wisdom"
    response = model.generate_content(prompt)

    return response.text

print(generate_response())