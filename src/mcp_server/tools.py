from pathlib import Path
import hmac
import os

# Managed directory. In Docker it is mounted at /data
# Locally it falls back to <project_root>/data.
_DEFAULT_DATA_DIR = Path(__file__).resolve().parents[2] / "data"
BASE_DIR = Path(os.getenv("DATA_DIR", _DEFAULT_DATA_DIR)).resolve()

FLAG_FILENAME = "flag.txt"



def is_safe_path(path: str) -> bool:
    """
    Valideaza daca un path este in data/
    
    - Normalizeaza path-ul cu resolve() pentru a elimina ../ 
    - Verifica ca path-ul normalizat e copil al data/
    - Previne accesul la fisiere din afara data/ 
    
    Args:
        path: Calea de verificat 
        
    Returns:
        True daca path-ul e sigur si in interiorul data/
        
    """
    
    # in caz ca modelul LLm adauga prefix redundant, stergere prefix pt consistenta
    if path.startswith("data/"):
        path = path[5:]
    
    try:
        # construire path complet (combina BASE_DIR cu path dat)
        full_path = (BASE_DIR / path).resolve()
        
        # verifica relatia parent-child (daca full_path e in interiorul BASE_DIR)
        is_within_bounds = full_path.is_relative_to(BASE_DIR)
        return is_within_bounds
        
    except (ValueError, OSError):
        return False



def get_file_content(file_path: str) -> str:
    """
    - validare securitatea cu is_safe_path()
    - verificare existenta si daca e fiser 
    
    Args:
        file_path: calea relativa fata de data/
    
    Returns:
        Continutul fisierului ca string
        
    """
    if file_path.startswith("data/"):
        file_path = file_path[5:]

    # verif securitate (daca path e in data/)
    if not is_safe_path(file_path):
        raise ValueError(
            f"Acces denied: '{file_path}' is outside of the managed folder"
        )
    
    # path absolut complet
    full_path = (BASE_DIR / file_path).resolve()

    # blocare accesul direct la flag.txt
    if full_path.name == FLAG_FILENAME:
        raise PermissionError("Access to flag.txt is restricted and cannot be read directly.")
    
    # Validari 
    if not full_path.exists():
        raise FileNotFoundError(f"File '{file_path}' does not exist")
    
    if not full_path.is_file():
        raise ValueError(f"'{file_path}' is not valid file")
    
    # citire fisier cu format modern UTF-8
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except UnicodeDecodeError:
        # daca nu a mers cu UTF-8: Latin-1 pentru fisiere vechi
        with open(full_path, 'r', encoding='latin-1') as f:
            content = f.read()
        return content


def list_directory(dir_path: str = "") -> list[str]:
    """    
    Format:
    - Directoare: "[DIR] nume_director"
    - Fisiere: "nume_fisier.ext"
    
    - Valideaza securitatea
    - Verifica ca path-ul e valid
    - Itereaza si sorteaza continutul
    - Folosire prefix [DIR] pentru subdirectoare
    
    Args:
        dir_path: Calea relativa la data/
    
    Returns:
        Lista sortata cu continutul folderului
        
    """
    if dir_path.startswith("data/"):
        dir_path = dir_path[5:]
    
    #daca LLM trimite fix "data" ca path
    if dir_path == "data":
        dir_path = ""
    
    # Validare securitate
    if not is_safe_path(dir_path):
        raise ValueError(
            f"Acces denied: '{dir_path}' is outside of the managed folder"
        )
    
    # path complet
    full_path = BASE_DIR / dir_path
    
    if not full_path.exists():
        raise FileNotFoundError(f"Directory '{dir_path}' does not exist")
    
    if not full_path.is_dir():
        raise NotADirectoryError(f"'{dir_path}' is not a directory")
    
    items = []
    
    #iterdir() ret un iterator cu continutul folderului
    for item in sorted(full_path.iterdir()):
        if item.is_dir():
            # subdirectoare sunt marcate cu [DIR] 
            items.append(f"[DIR] {item.name}")
        else:
            items.append(item.name)
    
    return items



def search_file(filename: str) -> list[str]:
    """
    Cauta un fisier dupa nume in tot arborele de directoare.
    
    Args:
        filename: Numele fisierului cautat 
    
    Returns:
        Lista de path-uri complete unde fisierul a fost gasit
        
    Examples:
        search_file("hidden.bit") -> ["misc/copy/hidden.bit"]
        search_file("txt") -> ["docs/guide.txt", "docs/settings.txt", "info.txt"]
    """

    if not is_safe_path(""):
        return []
    
    matches = []

    #conversie la lowercase pt cautare case-insensitive
    filename_lower = filename.lower()
    
    
    # os.walk() traversare recursiva arbore de foldere

    # pt fiecare director gasit:
    # root: path-ul complet catre folder
    # dirs: lista de subdirectoare
    # files: lista de fisiere 

    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            # Match case-insensitive
            if filename_lower in file.lower():
                
                #path complet spre fisier
                full_path = Path(root) / file

                #conversie la path relativ fata de BASE_DIR
                relative_path = full_path.relative_to(BASE_DIR)

                # Normalizare separatori (sa functioneze cross-platform) 
                normalized_path = str(relative_path).replace("\\", "/")
                matches.append(normalized_path)
    
    # sortat alfabetic
    return sorted(matches)








def _load_flag() -> str:
    """Return the secret flag: FLAG env var first, data/flag.txt as a local fallback."""
    env_flag = os.getenv("FLAG", "").strip()
    if env_flag:
        return env_flag

    flag_path = BASE_DIR / FLAG_FILENAME
    if flag_path.is_file():
        return flag_path.read_text(encoding="utf-8").strip()

    raise RuntimeError(
        "No flag configured. Set the FLAG environment variable (see .env.example)."
    )


def check_flag_guess(guess: str) -> bool:
    """
    Check whether a guess matches the secret flag.

    The comparison is case-insensitive, ignores surrounding whitespace and
    never returns the flag itself.
    """
    real_flag = _load_flag()
    normalized_guess = guess.strip().upper().encode("utf-8")
    normalized_flag = real_flag.upper().encode("utf-8")
    return hmac.compare_digest(normalized_guess, normalized_flag)
