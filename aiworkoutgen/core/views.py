#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI

#API key
key = 'insert-key'
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
        time = request.POST.get('time')
        target = request.POST.getlist('target_area')
        equipment = request.POST.getlist('equipment')
        custom_equipment = request.POST.get('custom_equipment', '')  # Default to '' if not provided
        custom_target = request.POST.get('custom_target', '')

        # ChatGPT-generated prompt
        chatGPT_generated_prompt = f"""
        Generate a custom workout plan based on the following user inputs:

        - **Time**: {time} minutes
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

        response = client.chat.completions.create( #I had chatgpt genarate custom schema for json output , chat completetion template used from openai documentation
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
                                                "time": { "type": "integer" },
                                                "target_area": { "type": "string" }
                                            }
                                        }
                                    }
                                },
                                "required": ["Warm-up", "Cool Down"]
                            }
                        },
                        "required": ["time", "target", "equipment", "sections"]
                    }
                }
            }
        )

        workout_plan_json = json.loads(response.choices[0].message.content)
        return JsonResponse(workout_plan_json)



