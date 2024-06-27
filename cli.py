#!/usr/bin/env python3

import click
import logging
import configparser
import os
import json
import csv

# Initialize and load configuration settings
config = configparser.ConfigParser()
config.read('config.ini')

# Set up logging to a file with specified format
logging.basicConfig(filename='todo_app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Priority levels for todo items
PRIORITIES = {
    "o": "Optional",
    "l": "Low",
    "m": "Medium",
    "h": "High",
    "c": "Crucial"
}

# Global variable to hold the file path set by the user
current_file_path = None

def load_todos(format):
    """Loads todos from a file based on the specified format (json, csv, or txt)."""
    global current_file_path
    todos = []
    filename = current_file_path if current_file_path else config['DEFAULT']['FileName']
    try:
        if format == 'json':
            with open(filename, 'r') as f:
                todos = json.load(f)
        elif format == 'csv':
            with open(filename, newline='') as f:
                reader = csv.DictReader(f)
                todos = list(reader)
        else:  # default to txt
            with open(filename, 'r') as f:
                todos = f.read().splitlines()
    except FileNotFoundError:
        logging.info("No todo file found, starting a new one.")
    except Exception as e:
        logging.error(f"Failed to load todos: {e}")
    return todos

def save_todos(todos, format):
    """Saves todos to a file based on the specified format (json, csv, or txt)."""
    global current_file_path
    filename = current_file_path if current_file_path else config['DEFAULT']['FileName']
    try:
        if format == 'json':
            with open(filename, 'w') as f:
                json.dump(todos, f, indent=4)
        elif format == 'csv':
            with open(filename, 'w', newline='') as f:
                fieldnames = ['name', 'description', 'priority']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(todos)
        else:  # default to txt
            with open(filename, 'w') as f:
                for todo in todos:
                    f.write(f"{todo}\n")
    except Exception as e:
        logging.error(f"Failed to save todos: {e}")

@click.group()
def mycommands():
    """A command line todo application."""
    pass

@click.command()
def signin():
    """Prompts user to set the file path for todos, updating the global variable."""
    global current_file_path
    current_file_path = click.prompt("Enter the path to your todo file", type=str)
    logging.info(f"File path set to {current_file_path}")

@click.command()
@click.option("--name", prompt="Enter your name", help="The name of the user")
def hello(name):
    """Greets the user by name."""
    click.echo(f"Hello {name}!")
    logging.info(f"Greeted {name}")

@click.command()
@click.argument("priority", type=click.Choice(list(PRIORITIES.keys())), default="m")
@click.option("-n", "--name", prompt="Enter the todo name", help="The name of the todo item")
@click.option("-d", "--description", prompt="Describe the todo", help="The description of the todo item")
def add_todo(name, description, priority):
    """Adds a new todo item with specified details."""
    format = config['DEFAULT']['StorageType']
    todos = load_todos(format)
    new_todo = {
        'name': name,
        'description': description,
        'priority': PRIORITIES[priority]
    }
    if format == 'txt':
        todos.append(f"{name}: {description} [Priority: {PRIORITIES[priority]}]")
    else:
        todos.append(new_todo)
    save_todos(todos, format)
    logging.info("Added new todo.")

@click.command()
@click.argument("idx", type=int)
def delete_todo(idx):
    """Deletes a todo item by its index."""
    format = config['DEFAULT']['StorageType']
    todos = load_todos(format)
    if idx < len(todos):
        todos.pop(idx)
        save_todos(todos, format)
        logging.info(f"Deleted todo at index {idx}")
    else:
        click.echo("Invalid todo index.")
        logging.error("Attempt to delete non-existent todo index.")

@click.command()
@click.option("-p", "--priority", type=click.Choice(list(PRIORITIES.keys())))
def list_todos(priority):
    """Lists all todos or those filtered by priority."""
    format = config['DEFAULT']['StorageType']
    todos = load_todos(format)
    filtered_todos = [todo for todo in todos if todo['priority'] == PRIORITIES[priority]] if priority else todos
    for idx, todo in enumerate(filtered_todos):
        if format == 'txt':
            click.echo(f"({idx}) - {todo}")
        else:
            click.echo(f"({idx}) - {todo['name']}: {todo['description']} [Priority: {todo['priority']}]")
    logging.info("Listed todos successfully.")

# Adding the commands to the command group
mycommands.add_command(signin)
mycommands.add_command(hello)
mycommands.add_command(add_todo)
mycommands.add_command(delete_todo)
mycommands.add_command(list_todos)

if __name__ == "__main__":
    mycommands()
