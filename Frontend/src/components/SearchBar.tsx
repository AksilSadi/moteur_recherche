import { useState, useEffect } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons'

function SearchBar({ search }: { search: (query: string) => void }) {
    const [searchTerm, setSearchTerm] = useState("");
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [showSuggestions, setShowSuggestions] = useState(true);

    // Autocomplétion
    useEffect(() => {
        if (searchTerm.length < 1) {
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
        if (searchTerm.trim() !== "") {
            search(searchTerm);
            setShowSuggestions(false);
        }
    };

    const handleSuggestionClick = (word: string) => {
        setSearchTerm(word);
        search(word);
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
                    placeholder="Rechercher un livre par mot-clé"
                    className="text-white w-[400px] bg-transparent outline-none"
                    value={searchTerm}
                    onChange={(e) => {
                        const value = e.target.value;
                        setSearchTerm(value);
                        setShowSuggestions(true);

                        if (value.length === 0) {
                            search("");         
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
