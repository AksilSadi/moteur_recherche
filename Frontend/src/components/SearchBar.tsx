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

  // Autocomplétion
  useEffect(() => {
    const type = detectSearchType(searchTerm);

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
    <div className="relative w-full flex justify-center mt-4 px-4">
      {/* FORMULAIRE RESPONSIVE */}
      <form
        onSubmit={handleSubmit}
        className="
          search
          flex items-center
          bg-gray-600
          h-10
          px-4 py-5
          rounded-md
          w-full 
          max-w-md sm:max-w-lg md:max-w-xl lg:max-w-2xl
        "
      >
        <input
          type="text"
          placeholder="Rechercher un livre… (mot-clé ou regex)"
          className="
            text-white 
            bg-transparent 
            outline-none 
            w-full
            text-sm sm:text-base
          "
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

      {/* LISTE DES SUGGESTIONS RESPONSIVE */}
      {showSuggestions && suggestions.length > 0 && (
        <ul
          className="
            absolute 
            top-14 
            bg-gray-800 
            rounded-md 
            shadow-xl 
            max-h-60 
            overflow-y-auto 
            z-50 
            w-full
            max-w-md sm:max-w-lg md:max-w-xl lg:max-w-2xl
          "
        >
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
