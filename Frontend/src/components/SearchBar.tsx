import { useState, useEffect } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faMagnifyingGlass } from "@fortawesome/free-solid-svg-icons";

function detectSearchType(query: string): "keyword" | "regex" {
  if (!query || query.trim() === "") return "keyword";

  const regexChars = /[.*+?^${}()|[\]\\]/;
  if (regexChars.test(query)) return "regex";

  return "keyword";
}

function SearchBar({
  search,
}: {
  search: (query: string, type: "keyword" | "regex") => void;
}) {
  const [searchTerm, setSearchTerm] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(true);

  // Autocompletion
  useEffect(() => {
    const type = detectSearchType(searchTerm);

    // Désactiver l'autocomplete en mode regex
    if (searchTerm.length < 1 || type === "regex") {
      setSuggestions([]);
      return;
    }

    const fetchAutocomplete = async () => {
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/livres/autocomplete?prefix=${searchTerm}`
        );
        const data = await res.json();
        setSuggestions(data);
      } catch (e) {
        console.error("Erreur autocomplétion :", e);
      }
    };

    const timer = setTimeout(fetchAutocomplete, 200);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchTerm.trim() === "") return;

    const type = detectSearchType(searchTerm);
    search(searchTerm, type);
    setShowSuggestions(false);
  };

  const handleSuggestionClick = (word: string) => {
    setSearchTerm(word);
    search(word, "keyword");
    setShowSuggestions(false);
  };

  return (
    <div className="relative w-full flex justify-center mt-4">
      <form
        onSubmit={handleSubmit}
        className="search h-10 flex items-center bg-gray-600 px-6 py-5 w-[480px] rounded-md"
      >
        <input
          type="text"
          placeholder="Rechercher un livre… (mot-clé ou regex)"
          className="text-white w-[400px] bg-transparent outline-none"
          value={searchTerm}
          onChange={(e) => {
            const value = e.target.value;

            setSearchTerm(value);
            setShowSuggestions(true);

            if (value.length === 0) {
              search("", "keyword");
              setSuggestions([]);
            }
          }}
        />
        <button type="submit" className="text-black ml-2">
          <FontAwesomeIcon icon={faMagnifyingGlass} />
        </button>
      </form>

      {/* Suggestions */}
      {showSuggestions && suggestions.length > 0 && (
        <ul className="absolute top-14 w-[480px] bg-gray-800 rounded-md shadow-xl max-h-60 overflow-y-auto z-50">
          {suggestions.map((word) => (
            <li
              key={word}
              className="px-4 py-2 hover:bg-gray-700 cursor-pointer text-white"
              onClick={() => handleSuggestionClick(word)}
            >
              {word}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default SearchBar;
