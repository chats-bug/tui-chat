import json

def find_task_status(file_path):
        try:
            task_status = []
            # Iterate through each task in the Task_list
            #task_list = json.loads(data['Task_list'])
            with open(file_path, 'r') as file:
                task_memory = json.load(file)
                for task in (task_memory):
                # Check if the mining_status is 'pending'
                    task_status.append({task["task_description"]:task['execution_status']})
                    
            return str(task_status)
            
        except:
            return ''