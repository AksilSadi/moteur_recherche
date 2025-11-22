import { useEffect, useState } from "react";
import "./App.css";
import { motion } from "framer-motion";
import BookCard from "./components/BookCard";
import type { Book } from "./types";
import SearchBar from "./components/SearchBar";
import Searched from "./components/Searched";
import BookDetails from "./components/Bookdetails";

function App() {
  const [query, setQuery] = useState("");
  const [type, setType] = useState<"keyword" | "regex">("keyword");
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);

  // Pagination
  const [page, setPage] = useState(1);
  const limit = 10;
  const [total, setTotal] = useState(0);
  const totalPages = Math.max(1, Math.ceil(total / limit));

  const [clickedOne, setClickedOne] = useState<Book | null>(null);

  const handleDetailClick = (book: Book) => {
    setClickedOne(book);
  };

  const handleSearch = (searchQuery: string, type: "keyword" | "regex") => {
    setQuery(searchQuery);
    setType(type);
    setClickedOne(null);
  };

  // Récupérer les livres de la page d’accueil
  useEffect(() => {
    if (query !== "") return;

    const fetchBooks = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/livres/?page=${page}&limit=${limit}`
        );
        const data = await response.json();

        setBooks(data.livres);
        setTotal(data.total);
      } catch (error) {
        console.error("Erreur lors de la récupération :", error);
      } finally {
        setLoading(false);
      }
    };

    fetchBooks();
  }, [page, query]);

  // ----------------------------------------------
  // COMPONENT : PAGINATION RESPONSIVE
  // ----------------------------------------------
  const Pagination = () => (
    <div className="flex flex-wrap justify-center mt-6 gap-2 px-4">
      <button
        onClick={() => {
          if (page > 1) {
            setPage(page - 1);
            window.scrollTo({ top: 0, behavior: "smooth" });
          }
        }}
        disabled={page === 1}
        className={`px-3 py-1 rounded text-sm sm:text-base ${
          page === 1
            ? "bg-gray-600 cursor-not-allowed"
            : "bg-gray-800 hover:bg-gray-700"
        } text-white`}
      >
        Précédent
      </button>

      {Array.from({ length: totalPages }, (_, i) => i + 1)
        .slice(Math.max(0, page - 3), page + 2)
        .map((p) => (
          <button
            key={p}
            onClick={() => {
              setPage(p);
              window.scrollTo({ top: 0, behavior: "smooth" });
            }}
            className={`px-3 py-1 rounded text-sm sm:text-base text-white ${
              p === page ? "bg-blue-600" : "bg-gray-800 hover:bg-gray-700"
            }`}
          >
            {p}
          </button>
        ))}

      <button
        onClick={() => {
          if (page < totalPages) {
            setPage(page + 1);
            window.scrollTo({ top: 0, behavior: "smooth" });
          }
        }}
        disabled={page === totalPages}
        className={`px-3 py-1 rounded text-sm sm:text-base ${
          page === totalPages
            ? "bg-gray-600 cursor-not-allowed"
            : "bg-gray-800 hover:bg-gray-700"
        } text-white`}
      >
        Suivant
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-700 text-white">
      <section className="relative text-center py-20 sm:py-24 px-4 sm:px-6">
        {/* TITLE */}
        <motion.h1
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-4xl sm:text-6xl font-extrabold mb-6 leading-tight"
        >
          Explorez la bibliothèque du futur 📚
        </motion.h1>

        {/* SUBTITLE */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-gray-300 text-base sm:text-lg max-w-2xl mx-auto mb-10"
        >
          Recherchez parmi des milliers d'œuvres…
        </motion.p>

        {/* SEARCH BAR */}
        <SearchBar search={handleSearch} />

        {/* SEARCH RESULTS / DETAILS / HOME GRID */}
        {query !== "" ? (
          <Searched term={query} type={type} />
        ) : clickedOne ? (
          <BookDetails clicked={clickedOne} />
        ) : (
          <>
            <p className="mt-16 font-bold text-2xl sm:text-3xl">Tous les livres</p>

            <div className="mt-4 flex flex-wrap justify-center gap-6 px-2 sm:px-6 py-4">
              {loading ? (
                <p>Chargement…</p>
              ) : (
                books.map((book) => (
                  <BookCard
                    key={book.gutendexId}
                    livre={book}
                    onClick={() => handleDetailClick(book)}
                  />
                ))
              )}
            </div>

            <Pagination />
          </>
        )}
      </section>

      {/* FOOTER */}
      <footer className="mt-20 text-center text-gray-400 py-10 border-t border-slate-800 text-sm sm:text-base">
        <p>Moteur de recherche littéraire - Projet DAAR © 2025</p>
        <p className="text-xs sm:text-sm mt-2">Développé par Massin & Aksil & Meriem - M2 STL</p>
      </footer>
    </div>
  );
}

export default App;