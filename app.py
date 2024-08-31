# jenkins_monitor/app.py

from flask import Flask, render_template, request
import jenkins
from datetime import datetime

app = Flask(__name__)

# Configure Jenkins servers
jenkins_servers = [
    {'name': 'Server 1', 'url': 'http://jenkins_server_1:8080', 'username': 'user', 'password': 'pass'},
    {'name': 'Server 2', 'url': 'http://jenkins_server_2:8080', 'username': 'user', 'password': 'pass'}
]

def get_jenkins_data(start_time=None, end_time=None):
    data = []
    for server in jenkins_servers:
        j = jenkins.Jenkins(server['url'], username=server['username'], password=server['password'])
        jobs = j.get_jobs()
        for job in jobs:
            job_info = j.get_job_info(job['name'])
            builds = job_info['builds']
            for build in builds:
                build_info = j.get_build_info(job['name'], build['number'])
                build_timestamp = datetime.fromtimestamp(build_info['timestamp'] / 1000.0)
                if start_time and end_time:
                    if not (start_time <= build_timestamp <= end_time):
                        continue
                data.append({
                    'server': server['name'],
                    'job_name': job['name'],
                    'build_number': build['number'],
                    'status': build_info['result'],
                    'duration': build_info['duration'],
                    'timestamp': build_timestamp
                })
    return data

@app.route('/')
def index():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    
    if start_time and end_time:
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
        end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
    else:
        start_time = None
        end_time = None

    data = get_jenkins_data(start_time, end_time)
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)