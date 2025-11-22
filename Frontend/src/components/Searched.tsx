import { useState, useEffect } from "react";
import type { Book } from "../types";
import BookCard from "./BookCard";
import BookDetails from "./Bookdetails";

function Searched({ term, type }: { term: string; type: "keyword" | "regex" }) {
  const [searchResults, setSearchResults] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);

  const [suggestions, setSuggestions] = useState<Book[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);
  const [clickedOne, setClickedOne] = useState<Book | null>(null);

  // Pagination
  const [page, setPage] = useState(1);
  const limit = 8;
  const [total, setTotal] = useState(0);
  const totalPages = Math.max(1, Math.ceil(total / limit));
  const [top3Global, setTop3Global] = useState<Book[]>([]);

  const handleDetailClick = (book: Book) => {
    setClickedOne(book);
  };

  useEffect(() => {
    if (!term) {
      setSearchResults([]);
      setSuggestions([]);
      setTop3Global([]);
      return;
    }

    const fetchBooks = async () => {
      setLoading(true);
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/livres/search?q=${encodeURIComponent(
            term
          )}&type=${type}&page=${page}&limit=${limit}`
        );
        const data = await res.json();

        setSearchResults(data.resultats);
        setTotal(data.total);

        if (page === 1) setTop3Global(Array.isArray(data.top3) ? data.top3 : []);
      } finally {
        setLoading(false);
      }
    };

    const t = setTimeout(fetchBooks, 400);
    return () => clearTimeout(t);
  }, [term, page, type]);

  // Suggestions basées sur les top3
  useEffect(() => {
    if (!term || !Array.isArray(top3Global) || top3Global.length === 0) {
      setSuggestions([]);
      return;
    }

    const fetchSuggestions = async () => {
      setLoadingSuggestions(true);
      try {
        const recGroups = await Promise.all(
          top3Global.map((b) =>
            fetch(
              `http://127.0.0.1:8000/livres/${b.gutendexId}/recommendations`
            ).then((res) => res.json())
          )
        );

        const merged: Record<string, Book> = {};
        recGroups.forEach((g) => {
          g?.recommendations?.forEach((r: Book) => {
            merged[r.gutendexId] = r;
          });
        });

        const resultIds = new Set(searchResults.map((b) => b.gutendexId));

        const cleanList = Object.values(merged)
          .filter((b) => !resultIds.has(b.gutendexId))
          .sort((a, b) => (b.scoreGlobal ?? 0) - (a.scoreGlobal ?? 0))
          .slice(0, 12);

        setSuggestions(cleanList);
      } finally {
        setLoadingSuggestions(false);
      }
    };

    fetchSuggestions();
  }, [top3Global]);

  const Pagination = () => (
    <div className="flex justify-center mt-6 space-x-2">
      <button
        onClick={() => page > 1 && setPage(page - 1)}
        disabled={page === 1}
        className={`px-3 py-1 rounded ${
          page === 1 ? "bg-gray-600 cursor-not-allowed" : "bg-gray-800 hover:bg-gray-700"
        } text-white`}
      >
        Précédent
      </button>

      {Array.from({ length: totalPages }, (_, i) => i + 1)
        .slice(Math.max(0, page - 3), page + 2)
        .map((p) => (
          <button
            key={p}
            onClick={() => setPage(p)}
            className={`px-3 py-1 rounded text-white ${
              p === page ? "bg-blue-600" : "bg-gray-800 hover:bg-gray-700"
            }`}
          >
            {p}
          </button>
        ))}

      <button
        onClick={() => page < totalPages && setPage(page + 1)}
        disabled={page === totalPages}
        className={`px-3 py-1 rounded ${
          page === totalPages ? "bg-gray-600 cursor-not-allowed" : "bg-gray-800 hover:bg-gray-700"
        } text-white`}
      >
        Suivant
      </button>
    </div>
  );

  return (
    <>
      {clickedOne ? (
        <BookDetails clicked={clickedOne} />
      ) : (
        <div className="w-full px-4 py-5">
          <p className="text-white text-xl mb-4">
            Résultats de recherche pour "{term}":
          </p>

          {loading ? (
            <div className="flex justify-center items-center h-40">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : searchResults.length === 0 ? (
            <p className="text-white">Aucun résultat trouvé.</p>
          ) : (
            <>
              {/* GRID RESPONSIVE */}
              <ul className="
                grid 
                grid-cols-1 
                sm:grid-cols-2 
                md:grid-cols-3 
                lg:grid-cols-4 
                gap-4
              ">
                {searchResults.map((book) => (
                  <BookCard
                    key={book.gutendexId}
                    livre={book}
                    onClick={() => handleDetailClick(book)}
                  />
                ))}
              </ul>

              <Pagination />
            </>
          )}

          {/* SUGGESTIONS */}
          {suggestions.length > 0 && (
            <div className="mt-12">
              <h3 className="text-white text-xl font-bold mb-4">Suggestions</h3>

              {loadingSuggestions ? (
                <div className="flex justify-center items-center h-40">
                  <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
              ) : (
                <ul className="
                  grid 
                  grid-cols-1 
                  sm:grid-cols-2 
                  md:grid-cols-3 
                  lg:grid-cols-4 
                  gap-4
                ">
                  {suggestions.map((book) => (
                    <BookCard
                      key={book.gutendexId}
                      livre={book}
                      onClick={() => handleDetailClick(book)}
                    />
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      )}
    </>
  );
}

export default Searched;
