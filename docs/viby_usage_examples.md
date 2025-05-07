# Viby Usage Examples

This document provides various usage scenarios and examples for the Viby tool to help users fully utilize its functionality.

## 1. Configuration Examples

### 1.1 Initial Setup

After installing Viby for the first time, you can run the configuration wizard:

```bash
yb --config
```

Configuration wizard example:

```bash
Checking terminal Chinese support...
Chinese support test

=============================================================================================
                                                       Viby Configuration Wizard                                                        
=============================================================================================

Please select interface language:
  1. English
  2. 中文
[1]: 1

Selected English interface

───────────────────────────────────────────────────────────────────────────────────────
Default API base URL [http://localhost:1234]:
Default API key (if needed) (enter 'pass' to skip) []:
───────────────────────────────────────────────────────────────────────────────────────

=======================================================================================
                                                                       --- Default Model Configuration ---                                                                  
=======================================================================================

Default model name [qwen3-30b-a3b-mlx@4bit]:
API URL for qwen3-30b-a3b-mlx@4bit (optional, leave blank to use default) (enter 'pass' to skip) [http://localhost:1234]:
API key for qwen3-30b-a3b-mlx@4bit (optional, leave blank to use default) (enter 'pass' to skip) []:
───────────────────────────────────────────────────────────────────────────────────────

=======================================================================================
                                                                   --- Think Model Configuration (Optional) ---                                                             
=======================================================================================

Think model name (optional, leave blank to skip) (enter 'pass' to skip) [qwen3-32b-mlx]:
API URL for qwen3-32b-mlx (optional, leave blank to use default) (enter 'pass' to skip) [http://localhost:1234]:
API key for qwen3-32b-mlx (optional, leave blank to use default) (enter 'pass' to skip) []:
───────────────────────────────────────────────────────────────────────────────────────

=======================================================================================
                                                                   --- Fast Model Configuration (Optional) ---                                                              
=======================================================================================

Fast model name (optional, leave blank to skip) (enter 'pass' to skip) [qwen3-0.6b-mlx]:
API URL for qwen3-0.6b-mlx (optional, leave blank to use default) (enter 'pass' to skip) []:
API key for qwen3-0.6b-mlx (optional, leave blank to use default) (enter 'pass' to skip) []:
───────────────────────────────────────────────────────────────────────────────────────
Temperature (0.0-1.0) [0.7]:
Max tokens [40960]:
API timeout (seconds) [300]:
Enable MCP tools
  1. Yes
  2. No
[1]: 1

MCP configuration folder: /Users/JohanLi233/.config/viby

───────────────────────────────────────────────────────────────────────────────────────
Configuration saved to: /Users/JohanLi233/.config/viby/config.yaml

Press Enter to continue...
usage: yb [-h] [-v] [--chat] [--shell] [--config] [--think] [--fast] [prompt]

viby - A versatile CLI tool for interacting with large language models

positional arguments:
  prompt         Prompt content to send to the model

options:
  -h, --help     Show this help message and exit
  -v, --version  Show program version number and exit
  --chat, -c     Start interactive chat session with the model
  --shell, -s    Generate and optionally execute shell commands
  --config       Start interactive configuration wizard
  --think, -t    Use think model for deeper analysis (if configured)
  --fast, -f     Use fast model for quicker responses (if configured)

Examples:
  yb "What is the Fibonacci sequence?"
  git diff | yb "Help me write a commit message"
  yb --shell "Find all json files in current directory"

```

## 2. Basic Usage Examples

### 2.1 Single Q&A

The most basic usage is to directly ask Viby questions:

```bash
yb "What are Python decorators? Please provide an example"
```

Example output:

```python
Python decorators are functions that take another function as argument and return a new function, typically used to enhance functionality without modifying the original function's code.

Basic example:

def log_function(func):
    def wrapper(*args, **kwargs):
        print(f"Calling function: {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Function {func.__name__} executed")
        return result
    return wrapper

@log_function
def greet(name):
    print(f"Hello, {name}!")

greet("John")

# Output:
# Calling function: greet
# Hello, John!
# Function greet executed
```

### 2.2 Interactive Chat

Start an interactive chat session:

```bash
yb --chat
```

Chat session example:

```markdown
User> I want to make a todo app, what features do I need?
Assistant> A basic todo app typically requires these core features:

1. Task management:
   - Add new tasks
   - Edit existing tasks
   - Delete tasks
   - Mark tasks as complete/incomplete

2. Task organization:
   - Category/tag system
   - Priority settings
   - Due dates
   - List or project grouping

3. Reminder features:
   - Date reminders
   - Recurring tasks

4. User experience:
   - Clean interface
   - Search functionality
   - Sorting and filtering

5. Data management:
   - Data sync/backup
   - Import/export

Which features would you like to focus on?

User> How to implement persistent task storage?
Assistant> Task persistence can be implemented in several ways depending on your app type and scale:

1. Local file storage:
   - JSON files: Common for simple apps
   - SQLite: Lightweight but fully featured relational database
   - XML or YAML: Good for configs and small data

2. Relational databases:
   - MySQL/PostgreSQL: For large apps with complex queries
   - Supports transactions and data integrity

3. NoSQL databases:
   - MongoDB: For frequently changing data structures
   - Firebase/Firestore: For cross-platform apps with realtime sync

4. Cloud storage services:
   - AWS DynamoDB
   - Azure Cosmos DB
   - Google Cloud Datastore

5. Mobile-specific storage:
   - iOS: Core Data, UserDefaults
   - Android: Room, SharedPreferences

|> exit

```

### 2.3 Shell Command Generation

Generate and execute Shell commands:

```bash
yb --shell "Create a project with three subdirectories and initialize it as a git repository"
```

Example output:

```bash
Generated command:
mkdir -p project/{src,docs,tests} && cd project && git init

Execute this command? [r]un, [e]dit, [y]ank, [c]hat, [q]uit (default: run): 
```

## 3. Advanced Usage Examples

### 3.1 Using the Think Model

When more complex thinking capabilities are needed, use the think model:

```bash
yb --think "Help me optimize this code, focusing on performance:
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"
```

For simple tasks, use the fast model to improve response time:

```bash
yb --fast "Translate 'Hello, World!' to Chinese"
```

### 3.3 Using MCP Tools

Use MCP tools to extend functionality:

```bash
yb "Use the weather tool to check tomorrow's weather in Beijing"
```

## 4. Command Reference

Viby provides a series of commands for different ways of interacting with large language models.

### 4.1 `yb [question]`
- **Function**: Directly ask AI a question and get a one-time answer. This is Viby's default behavior; if the first argument is not a known option, it will be treated as a question.
- **Example**:
  ```bash
  yb "What is the capital of China?"
  yb "Explain what cloud computing is"
  ```

### 4.2 `yb --chat`
- **Function**: Start an interactive chat session, allowing for multi-turn conversations.
- **Example**:
  ```bash
  yb --chat
  ```
  After entering chat mode, you can directly input questions and use `exit` to quit.

### 4.3 `yb --shell [task description]`
- **Function**: Generate appropriate Shell commands based on the task description and provide execution options (run, edit, copy, quit).
- **Alias**: `-s`
- **Example**:
  ```bash
  yb --shell "List all .txt files in the current directory and count their lines"
  ```

### 4.4 `yb --config`
- **Function**: Start the configuration wizard to set API address, model, language, temperature, and other parameters.
- **Example**:
  ```bash
  yb --config
  ```

### 4.5 `yb --version`
- **Function**: Display the current version number of the Viby tool.
- **Example**:
  ```bash
  yb --version
  ```

### 4.6 `yb --help`
- **Function**: Display help information, listing all available commands and options.
- **Alias**: `-h`
- **Example**:
  ```bash
  yb --help
  ```

## 5. Common Use Cases

1. **Code assistance**: Explain code, generate code snippets, debugging help
2. **Text processing**: Translation, summarization, text refinement
3. **Knowledge queries**: Basic concept explanations and knowledge Q&A
4. **Shell operations**: Generate complex or hard-to-remember commands
5. **Creative writing**: Writing ideas, content creation assistance
6. **Data analysis**: Simple data explanations and processing suggestions
7. **Learning assistance**: Concept explanations and learning material generation

---
