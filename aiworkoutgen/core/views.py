#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import JsonResponse
from openai import OpenAI

#API key
key = ''
client = OpenAI(api_key = key)


# Create your views here.
def home(request):
	return render(request, 'core/home.html')


def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		print(f"Username = {username}, Password = {password}")

		user = authenticate(request, username=username, password=password)

		if user is None:
			messages.error(request, 'Your Username or Password is Incorrect')
			return redirect('login')
		else:
			login(request, user)
			return redirect('home')
	
	return render(request, 'core/login.html')



def user_signup(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		email = request.POST.get('email')
		password = request.POST.get('password')
		print(f"Username: {username}, Password: {password}")
		confirmPassword = request.POST.get('confirmPassword')
		
		user = authenticate(request, username=username, password=password, confirmPassword=confirmPassword)
	

		if password != confirmPassword:
			messages.error(request, "The password does not match!")
			return render(request, 'core/signup.html')
		
		try: 
			user = user.objects.createUser(username=username, password = password)
			user.save()
			messages.success(request, "You have successfully registered! Please Log In")
			return redirect('login')
		except Exception as e:
			messages.error(request, f"Error while creating User: {str(e)}")
			
	return render(request, 'core/signup.html')


def user_workout(request):
	if request.method == 'POST':  # validate

		# Get user inputs
		time = request.POST.get('time') #capture time in string format i.e 10 minutes
		timeInt = int(time.split()[0]) # take only the first part, convert to int i.e 10
		target = request.POST.getlist('target_area')
		target_list = ", ".join(target)
		equipment = request.POST.getlist('equipment')
		equipment_list = ", ".join(equipment) #comma sep, remove list format []
		custom_equipment = request.POST.get('custom_equipment', '')  # Default to '' if not provided
		custom_target = request.POST.get('custom_target', '')

		# ChatGPT-generated prompt, .joint converts format from list to a string
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
		- Incorporate custom equipment and target areas if provided by the user. If no input from {equipment_list} or {custom_equipment} use body weight by default.

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
												"time": { "type": "integer" },
												"sets": { "type": "integer" },
												"reps": { "type": "integer" },  
												"target_area": { "type": "string" },
												"equipment_needed": { "type": "string" }
											}
										}
									},
									"Cardio": {
										"type": "array",
										"items": {
											"type": "object",
											"properties": {
												"name": { "type": "string" },
												"time": { "type": "integer" },
												"sets": { "type": "integer" },
												"reps": { "type": "integer" },  
												"target_area": { "type": "string" },
												"equipment_needed": { "type": "string" }
											}
										}
									},
									"Cool Down": {
										"type": "array",
										"items": {
											"type": "object",
											"properties": {
												"name": { "type": "string" },
												"time": { "type": "integer" },
												"sets": { "type": "integer" },
												"reps": { "type": "integer" },  
												"target_area": { "type": "string" },
												"equipment_needed": { "type": "string" }
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


		workout_plan_json = json.loads(response.choices[0].message.content) # one-liner json parsing, convert json string into py dictionary
#will display error if time doesn't match user input, temporily blocking this from executing so program can run.  time still needs addressing.
	''' total_time = 0  
		for section in workout_plan_json["sections"].values(): #takes array of all sections, name, sets, reps, time, target_area
			for exercise in section:  #itterate through array values in each section
				total_time += exercise["time"]  #takes each value of time in each section, takes sum

		if total_time != timeInt:
			return JsonResponse({"error": "ChatGPT unable to provide accurate time, please try again!"}) #django needs httpResponse object to display
		else: ''' 
	
	#dictionary key pair values for passing json data, var, from django view to template, workout.html!
	return render(request, 'core/workout.html', {'workout_data': workout_plan_json, #json, needs extra handling, therefore diff key/pair values.
												'target_list' : target_list, #var - target list w/o []
												'equipment_list' : equipment_list #var - equipment list w/o []
												})

																						


