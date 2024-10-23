#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from openai import OpenAI
from .forms import WorkoutPlanForm
from .models import WorkoutPlan

# API key
key = 'insert key'
client = OpenAI(api_key=key)

def create_workout_plan(request):
    if request.method == 'POST':
        form = WorkoutPlanForm(request.POST)
        if form.is_valid():
            workout_plan = form.save(commit=False)
            workout_plan.user = request.user  # Set the user
            workout_plan.save()
            return redirect('workout_plan_success')  # Redirect to a success page or another view
    else:
        form = WorkoutPlanForm()

    return render(request, 'core/create_workout_plan.html', {'form': form})

# Create your views here.
def home(request):
    return render(request, 'core/home.html')


def user_login(request):
    return render(request, 'core/login.html')


def user_signup(request):
    return render(request, 'core/signup.html')

def user_workout(request):
    if request.method == 'POST':
        form = WorkoutPlanForm(request.POST)
        time = request.POST.get('time')
        timeInt = int(time.split()[0])
        target = request.POST.getlist('target_area')
        target_list = ", ".join(target)
        equipment = request.POST.getlist('equipment')
        equipment_list = ", ".join(equipment)
        custom_equipment = request.POST.get('custom_equipment', '')
        custom_target = request.POST.get('custom_target', '')

        # ChatGPT-generated prompt
        chatGPT_generated_prompt = f"""
        Generate a custom workout plan with sets and reps keys based on the following user inputs:
        - **Time**: {timeInt} minutes
        - **Target Areas**: {target_list}
        - **Equipment**: {equipment_list}
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
        - **Equipment Needed** (the equipment used for the exercise)

        3. **Customization**:
        - Incorporate custom equipment and target areas if provided by the user. If no input from {equipment_list} or {custom_equipment}, use body weight by default.

        4. **Output Format**:
        - Return the workout plan in **JSON** format, with each section as a key.
        """

        response = client.chat.completions.create(
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
                            "time": {"type": "integer"},
                            "target": {"type": "array", "items": {"type": "string"}},
                            "equipment": {"type": "array", "items": {"type": "string"}},
                            "sections": {
                                "type": "object",
                                "properties": {
                                    "Warm-up": {"type": "array", "items": {"type": "object", "properties": {
                                        "name": {"type": "string"},
                                        "time": {"type": "integer"},
                                        "sets": {"type": "integer"},
                                        "reps": {"type": "integer"},
                                        "target_area": {"type": "string"},
                                        "equipment_needed": {"type": "string"}
                                    }}},
                                    "Cardio": {"type": "array", "items": {"type": "object", "properties": {
                                        "name": {"type": "string"},
                                        "time": {"type": "integer"},
                                        "sets": {"type": "integer"},
                                        "reps": {"type": "integer"},
                                        "target_area": {"type": "string"},
                                        "equipment_needed": {"type": "string"}
                                    }}},
                                    "Cool Down": {"type": "array", "items": {"type": "object", "properties": {
                                        "name": {"type": "string"},
                                        "time": {"type": "integer"},
                                        "sets": {"type": "integer"},
                                        "reps": {"type": "integer"},
                                        "target_area": {"type": "string"},
                                        "equipment_needed": {"type": "string"}
                                    }}}
                                }
                            }
                        }
                    }
                }
            }
        )

        workout_plan_json = json.loads(response.choices[0].message.content) # one-liner json parsing, convert json string into py dictionary
        #will display error if time doesn't match user input, temporily blocking this from executing so program can run.  time still needs addressing.
        ''' total_time = 0  
    for section in workout_plan_json["sections"].values(): #takes array of all sections, name, sets, reps, time, target_area
        for exercise in section:  #itterate through array values in each section
            total_time += exercise["time"]  #takes each value of time in each section, takes sum

    if total_time != timeInt:
        return JsonResponse({"error": "ChatGPT unable to provide accurate time, please try again!"}) #django needs httpResponse object to display
    else: '''

    # Render the workout.html template with the generated data
    return render(request, 'core/workout.html', {
        'workout_data': workout_plan_json,
        'target_list': target_list,
        'equipment_list': equipment_list,
    })
