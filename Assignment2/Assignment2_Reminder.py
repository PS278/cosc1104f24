import time
from datetime import datetime, timedelta

# List to store tasks
tasks = []
shown_reminders = set()  # Track reminders that have already been shown

# Function to add a new task
def add_task():
    task_name = input("Enter task name: ")
    due_date_str = input("Enter due date (YYYY-MM-DD HH:MM): ")
    reminder_minutes = int(input("How many minutes before due time would you like a reminder? "))
    
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d %H:%M")
    reminder_time = due_date - timedelta(minutes=reminder_minutes)
    
    task = {
        "name": task_name,
        "due_date": due_date,
        "reminder_time": reminder_time
    }
    
    tasks.append(task)
    print(f"Task '{task_name}' added successfully!\n")

# Function to view all tasks
def view_tasks():
    if not tasks:
        print("No tasks available.")
    else:
        for i, task in enumerate(tasks, 1):
            print(f"{i}. {task['name']} - Due: {task['due_date']} - Reminder: {task['reminder_time']}")
    print()

# Function to check for upcoming reminders and display notifications
def check_reminders():
    current_time = datetime.now()
    for task in tasks:
        # Check if the current time is within the reminder window and if the reminder hasn't been shown yet
        if task["reminder_time"] <= current_time < task["due_date"] and task["name"] not in shown_reminders:
            print(f"Reminder: Task '{task['name']}' is due soon (Due: {task['due_date']})!\n")
            shown_reminders.add(task["name"])  # Mark this reminder as shown to avoid repeats

# Main function to run the console application
def main():
    print("Task Reminder Application\n")

    while True:
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            add_task()
        elif choice == '2':
            view_tasks()
        elif choice == '3':
            print("Exiting the application.")
            break
        else:
            print("Invalid choice, please try again.")
        
        # Automatically check for reminders every minute
        print("Checking for reminders...")
        check_reminders()
        time.sleep(60)  # Wait 1 minute before checking reminders again

# Run the application
if __name__ == "__main__":
    main()
