# DAV Programming Language

**DAV** is a human-friendly programming language that allows you to write code in natural French or English.

## Features

- 🇫🇷 **French syntax**: Write code in natural French
- 🇬🇧 **English syntax**: Write code in natural English  
- 🧮 **Mathematical operations**: Support for basic to advanced math
- 🔄 **Control structures**: If/else, loops, functions
- 📝 **Natural language**: Code reads like human sentences
- 🚀 **Easy to learn**: Perfect for beginners

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/dav-language.git
cd dav-language

# Make executable
chmod +x bin/dav

# Add to PATH (optional)
export PATH=$PATH:$(pwd)/bin
```

### Usage

```bash
# Run French programs
dav hello.dav

# Run English programs  
dav-en hello.dav

# Interactive mode
dav --interactive
```

### Example Programs

**French version** (`hello.dav`):
```dav
J'ai un nombre appelé x.
Définir x à 5.
Montrer x à l'écran.

Créer une fonction nommée doubler qui prend un nombre.
    Je vais retourner nombre fois 2.

Montrer le résultat de doubler(x) à l'écran.
```

**English version** (`hello.dav`):
```dav  
I have a number called x.
Set x to 5.
Show x on the screen.

Create a function named double that takes a number.
    I will return number times 2.

Show the result of double(x) on the screen.
```

## Language Syntax

| French | English | Description |
|--------|---------|-------------|
| `J'ai un nombre appelé x` | `I have a number called x` | Variable declaration |
| `Définir x à 5` | `Set x to 5` | Assignment |
| `Montrer x à l'écran` | `Show x on the screen` | Print output |
| `Si x est supérieur à 3` | `If x is greater than 3` | Conditions |
| `Tant que x est inférieur à 10` | `While x is less than 10` | Loops |

## Project Structure

```
dav-language/
├── bin/
│   ├── dav              # French interpreter executable
│   └── dav-en           # English interpreter executable  
├── src/
│   ├── core/
│   │   ├── parser.py    # Common parsing logic
│   │   ├── evaluator.py # Expression evaluation
│   │   └── executor.py  # Code execution
│   ├── french/
│   │   └── interpreter.py
│   ├── english/
│   │   └── interpreter.py
│   └── common/
│       ├── types.py
│       └── utils.py
├── examples/
│   ├── french/
│   └── english/
├── docs/
├── tests/
└── assets/
    └── logo.ico
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
