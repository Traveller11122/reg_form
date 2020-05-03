from requests import post, get


print(get("https://64705546.ngrok.io/api/jobs/1").json())
'''print(post('http://localhost:5000/api/news', json={'team_leader': 1,
                                                   'collaborators': '2,3,4',
                                                   'work_size': 12,
                                                   'job': "temp"}).json())'''

