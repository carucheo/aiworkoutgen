#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI

#API key
key = 'at discord chat 2'
client = OpenAI(api_key = key)


# Create your views here.
def home(request):
    return render(request, 'core/home.html')


def user_login(request):
    return render(request, 'core/login.html')


def user_signup(request):
    return render(request, 'core/signup.html')


def user_workout(request):
    if request.method == 'POST':  # validate

        # Get user inputs
        time = request.POST.get('time') #capture time in string format i.e 10 minutes
        timeInt = int(time.split()[0]) # take only the first part, convert to int i.e 10
        target = request.POST.getlist('target_area')
        equipment = request.POST.getlist('equipment')
        custom_equipment = request.POST.get('custom_equipment', '')  # Default to '' if not provided
        custom_target = request.POST.get('custom_target', '')

        # ChatGPT-generated prompt, .joint converts format from list to a string
        chatGPT_generated_prompt = f"""
        Generate a custom workout plan with sets and reps keys based on the following user inputs:

        - **Time**: {timeInt} minutes
        - **Target Areas**: {', '.join(target)}
        - **Equipment**: {', '.join(equipment)}
        - **Custom Equipment**: {custom_equipment or 'None'}
        - **Custom Target Areas**: {custom_target or 'None'}

        Requirements:

        1. **Sections**:
        - Always include the following sections:
        - **Warm-up**
        - **Cool Down**
        - Automatically add relevant sections such as **Cardio**, **Strength Training**, etc., based on the provided target areas and equipment.

        2. **Exercises**:
        - For each section, list exercises with the following details:
        - **Name** of the exercise
        - **Sets** (number of sets)
        - **Time** (time in minutes) 
        - **Target Area** (the body area being targeted)

        3. **Customization**:
        - Incorporate custom equipment and target areas if provided by the user. If no input from {equipment} or {custom_equipment} use body weight by default.

        4. **Output Format**:
        - Return the workout plan in **JSON** format, with each section as a key.
        """

        response = client.chat.completions.create( #generate JSON data, from chat.completetion openai documentation, custom JSON schema generated
            model="gpt-4o-2024-08-06",
            messages=[
                {
                    "role": "user",
                    "content": chatGPT_generated_prompt 
                },
            ],
            response_format={         
               "type": "json_schema",
                "json_schema": {
                    "name": "workout_schema",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "time": {
                                "type": "integer",
                                "description": "The time in minutes for the workout"
                            },
                            "target": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of target areas"
                            },
                            "equipment": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                },
                                "description": "List of equipment"
                            },
                            "sections": {
                                "type": "object",
                                "properties": {
                                    "Warm-up": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": { "type": "string" },
                                                "sets": { "type": "integer" },
                                                "reps": { "type": "integer" },  
                                                "time": { "type": "integer" },
                                                "target_area": { "type": "string" }
                                            }
                                        }
                                    },
                                    "Cardio": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": { "type": "string" },
                                                "sets": { "type": "integer" },
                                                "reps": { "type": "integer" },  
                                                "time": { "type": "integer" },
                                                "target_area": { "type": "string" }
                                            }
                                        }
                                    },
                                    "Cool Down": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": { "type": "string" },
                                                "sets": { "type": "integer" },
                                                "reps": { "type": "integer" },  
                                                "time": { "type": "integer" },
                                                "target_area": { "type": "string" }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        )


        workout_plan_json = json.loads(response.choices[0].message.content)

        total_time = 0 
        for section in workout_plan_json["sections"].values(): #takes array of all sections, name, sets, reps, time, target_area
            for exercise in section:  #itterate through array values in each section
                total_time += exercise["time"]  #takes each value of time in each section, takes sum

        if total_time != timeInt:
            return JsonResponse({"error": "ChatGPT unable to provide accurate time, please try again!"}) #django needs httpResponse object to display
        else:
            return JsonResponse(workout_plan_json)


