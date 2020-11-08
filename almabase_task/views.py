from django.http import HttpResponse
from django.shortcuts import render
import requests
import json

def index(request):
	
	# url for serching repos by organisation name
	url = 'https://api.github.com/orgs/{}/repos'

	# get company name, value of M and N from the user

	company = request.POST.get('company_name', 'default')
	_N = request.POST.get('value_of_n', 1)
	_M = request.POST.get('value_of_m', 1)

	N = int(_N)
	M = int(_M)

	if N <= 0 or M <= 0:
		return HttpResponse("Invalid Values Entered")

	# API response converted into json array
	response = requests.get(url.format(company)).json()
	
	if 'message' in response:
		if response['message'] == 'Not Found':
			return HttpResponse("Error")

	# sorting responses by forks count
	response.sort(key = lambda repo:repo["forks_count"], reverse = True)
	
	repo_data = [] # to store final all N repositories of a company
	
	for r in response:
		N -= 1   # decrease count each time by 1
		repo = {
		'name' : r["name"],
		'url' : r["html_url"],
		'forks' : r["forks_count"],
		'owner' : r["owner"]["login"],
		'commits' : []
		}

		# url for searching committers of a repo
		c_url = "https://api.github.com/repos/" + repo['owner'] + "/" + repo['name'] +"/contributors"
		
		response2 = requests.get(c_url).json()
		temp_M = M
		for x in response2:
			temp_M -= 1
			commit = {
			'name' : x["login"],
			'commit_count' : x["contributions"],
			'profile_url' : x['html_url'],
			}
			repo['commits'].append(commit)
			if temp_M <= 0:
				break

		repo_data.append(repo)
		if N <= 0:
			break

	context  = {
	'repo_data' : repo_data,
	}

	return render(request, 'index.html', context)
