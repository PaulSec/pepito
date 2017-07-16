# Pepito

Searches through git repositories for specific strings, digging deep into commit history and branches. This is effective at finding secrets accidentally committed.
This project is highly inspired from [TruffleHog](https://github.com/dxa4481/truffleHog) which does exactly the same thing on high entropy strings.

## Usage

![Example](https://i.imgur.com/GHIYGHu.gif "Looks for 'password' in a repository")

```bash
pepito https://github.com/dxa4481/truffleHog.git --search 'password'
```

or

```bash
python pepito.py file:///user/dxa4481/codeprojects/truffleHog/
```

## Install
```bash
git clone https://github.com/PaulSec/pepito
cd pepito && python pepito.py -h 
```

## How it works

This module will go through the entire commit history of each branch, and check each diff from each commit. There, it will go through all the changes and check for the existence of the string you're looking for. If present, it will print the content to the screen.

## License

This has been released under MIT License. Shout out to [@PaulWebSec](https://twitter.com/PaulWebSec) for any questions.