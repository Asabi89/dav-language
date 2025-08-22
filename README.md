# 🚀 DAV - Premier Langage de Programmation Bilingue

[![Release](https://img.shields.io/github/v/release/Asabi89/dav-language)](https://github.com/Asabi89/dav-language/releases)
[![Downloads](https://img.shields.io/github/downloads/Asabi89/dav-language/total)](https://github.com/Asabi89/dav-language/releases)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**DAV** révolutionne la programmation en permettant d'écrire du code en **français** ET **anglais** naturels !

## ⚡ Installation Ultra-Rapide

### Script Automatique (Recommandé)
```bash
# Linux/macOS
curl -sSL https://github.com/Asabi89/dav-language/releases/download/v1.0.0/install.sh | bash

# Windows (PowerShell)
iwr -useb https://github.com/Asabi89/dav-language/releases/download/v1.0.0/install.ps1 | iex
```

### Package Managers (Bientôt)
```bash
# PyPI
pip install dav-language

# Homebrew (macOS)  
brew install dav

# APT (Ubuntu/Debian)
sudo apt install dav-language
```

## 🎯 Usage Simple

```bash
# Mode français
dav mon_programme.dav

# Mode anglais
dav-en my_program.dav

# Mode interactif
dav --interactive
```

## 💡 Exemples de Code

### 🇫🇷 Version Française
```dav
J'ai un nombre appelé âge.
Assigne âge à 25.

Si l'âge est supérieur à 18 alors
    Afficher "Vous êtes majeur !"
Sinon
    Afficher "Vous êtes mineur."

Créer une fonction nommée calculer_double qui prend un nombre.
    Je vais retourner nombre fois 2.

Affiche le résultat de calculer_double(âge) à l'écran.
```

### 🇬🇧 Version Anglaise
```dav
I have a number called age.
Set age to 25.

If age is greater than 18 then
    Display "You are an adult!"
else
    Display "You are a minor."

Create a function named calculate_double that takes a number.
    I will return number times 2.

Show the result of calculate_double(age) on the screen.
```

## 🌟 Fonctionnalités

| 🇫🇷 Français | 🇬🇧 English | Description |
|---------------|-------------|-------------|
| `J'ai un nombre appelé x` | `I have a number called x` | Déclaration de variable |
| `Assigne x à 5` | `Set x to 5` | Assignation |
| `Affiche x` | `Show x` | Affichage |
| `Si x est supérieur à 3` | `If x is greater than 3` | Conditions |
| `Tant que x est inférieur à 10` | `While x is less than 10` | Boucles |
| `Créer une fonction nommée` | `Create a function named` | Fonctions |

## 📁 Structure du Projet

```
dav-language/
├── 🐍 dav_main.py           # Interpréteur français
├── 🐍 dav_en_main.py        # Interpréteur anglais  
├── 🏗️ build.py             # Script de build
├── 📋 setup.py             # Configuration PyPI
├── 📁 langage/             # Grammaires et syntaxe
├── 📁 test/                # Tests unitaires
├── 📁 assets/              # Ressources (logo, etc.)
├── 📁 releases/            # Binaires compilés
├── 📁 packaging/           # Packages (.deb, .pkg, etc.)
├── 📁 installers/          # Installateurs
├── 📁 website/             # Site web
└── 📁 vscode-extension-dav/ # Extension VSCode
```

## 🛠️ Développement

### Build depuis les Sources
```bash
# Cloner le repository
git clone https://github.com/Asabi89/dav-language.git
cd dav-language

# Build les binaires
python build.py

# Tester
python dav_main.py examples/test.dav
python dav_en_main.py examples/test_en.dav
```

### Tests
```bash
# Lancer tous les tests
python -m pytest test/

# Tests spécifiques
python test/test_parser.py
python test/test_evaluator.py
```

## 🌍 Communauté

- 📚 **[Documentation](https://github.com/Asabi89/dav-language/wiki)**
- 🐛 **[Issues](https://github.com/Asabi89/dav-language/issues)**
- 💬 **[Discussions](https://github.com/Asabi89/dav-language/discussions)**
- 🎮 **[Playground Web](https://asabi89.github.io/dav-language)**

## 🎯 Roadmap

- [ ] 📦 Package managers (PyPI, Homebrew, etc.)
- [ ] 🌐 Éditeur en ligne interactif
- [ ] 🔧 Extension VSCode
- [ ] 📚 Documentation interactive
- [ ] 🏫 Support éducationnel

## 🤝 Contribuer

1. Fork le repository
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) pour les détails.

---

**Créé avec ❤️ par [Asabi89](https://github.com/Asabi89) pour démocratiser la programmation**
