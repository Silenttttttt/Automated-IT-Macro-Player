# Auto IT - Automated IT Macro Player


Auto IT is a powerful tool designed to interpret and execute a series of macro actions based on a provided input string. Whether you're looking to automate common tasks, interface with a chatbot, or execute custom sequences, Auto IT has you covered.

## Features:

- `Macro Execution: Execute complex macros derived from input strings.`
- `Chatbot Integration: Generate action lists using a chatbot.`
- `Custom Actions: Define your own macro actions using a unique syntax.`

## Usage:

```sh
python auto_it.py [filename]

```


## Input String Format:

Your macro command string can look something like this:

```sh
2|32|34:2|37:win+r|34:2|36:chrome|37:enter|34:2|36:192.168.1.254:8080|37:enter|34:2|36:admin|37:tab|36:password|37:enter
```

Each number refers to an action from the `general_actions` list. Some actions, like `34` (wait) and `37` (keyboard shortcut), expect additional input after a colon.

## General Actions:

Here's a brief overview of the predefined actions:

```sh
[32: login into windows admin user]
[33: search and open app(33:INPUT)]
[34: Wait for a period in seconds(34:INPUT)]
[35: Run CMD command(35:INPUT)]
[36: Type text(36:INPUT)]
[37: Keyboard Shortcut(+ separator)(37:INPUT)]
[38: Type file contents(38:INPUT)]
[39: for loop keyboard shortcut(39:INPUT;NUM)]
```

Each action corresponds to a real-world IT task, like logging in, waiting, typing text, or executing keyboard shortcuts.
