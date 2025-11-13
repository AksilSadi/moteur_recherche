import { useEffect, useState } from 'react'
import './App.css'
import { motion } from 'framer-motion'
import BookCard from './components/BookCard'
import type { Book } from './types';
import SearchBar from './components/SearchBar'
import Searched from './components/Searched';

function App() {
  const [query, setQuery] = useState("");
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);

  const handleDetailClick = (bookId: string) => {
    // Gérer l'affichage des détails du livre
  };

  const handleSearch = (searchQuery: string) => {
    setQuery(searchQuery);
  };


  

  //recuperer livre aleatoire
  useEffect(() => {
    const fetchRandomBooks = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://127.0.0.1:8000/livres/?page=${page}&limit=10`);
        const data = await response.json();
        setBooks(data.livres);
        console.log(data.livres);
      } catch (error) {
        console.error("Erreur lors de la récupération des livres :", error);
      } finally {
        setLoading(false);
      }
    };

    fetchRandomBooks();
  }, [page]);

  
  

  return (
    <div className="min-h-screen bg-gray-700 from-slate-900 via-slate-950 to-black text-white">
      {/* HERO SECTION */}
      <section className="relative text-center py-24 px-6">
        <motion.h1
          initial={{ opacity: 0, y: -30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-5xl sm:text-6xl font-extrabold mb-6"
        >
          Explorez la bibliothèque du futur 📚
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="text-gray-300 text-lg max-w-2xl mx-auto mb-12"
        >
          Recherchez parmi des milliers d'œuvres, découvrez les classiques, et laissez-vous guider par la science des graphes.
        </motion.p>

        {/* Barre de recherche */}
        <SearchBar search={handleSearch} />

        {/* Affichage des livre */}
        {query===""?<div>
          {books && books.length > 0 && (
          <div className="mt-16 flex flex-wrap justify-center gap-6 px-6 py-4">
            {books.map((book:Book) => (
              <BookCard
                key={book.gutendexId}
                livre={book}
                onClick={() => { handleDetailClick(book.gutendexId) }}
              />
            ))}
          </div>
        )}
        </div>:<Searched term={query} />}
      
      </section>


     {query===''?<section className='w-full'>
      {/* CATEGORIES */}
      <section className="mt-8 px-6 text-center">
        <h2 className="text-2xl font-semibold mb-4">🌈 Explorer par thème</h2>
        <div className="flex flex-wrap justify-center gap-3">
          {["Aventure", "Amour", "Philosophie", "Science", "Classiques"].map((theme) => (
            <button
              key={theme}
              className="bg-slate-800 hover:bg-blue-600 px-4 py-2 rounded-full text-white transition-all"
              
            >
              {theme}
            </button>
          ))}
        </div>
      </section>

      {/* LIVRES POPULAIRES */}
      {!loading && books && books.length === 0 && (
        <section className="mt-16 px-6">
          <h2 className="text-2xl font-semibold mb-6">📚 Livres populaires</h2>
          
        </section>
      )}

      {/* CITATION */}
      <section className="mt-24 mx-6 bg-slate-800 py-10 px-6 rounded-xl text-center shadow-xl">
        <p className="italic text-gray-300 text-lg max-w-2xl mx-auto">
          “A reader lives a thousand lives before he dies. The man who never reads lives only one.”
        </p>
        <span className="block mt-4 text-gray-500">— George R. R. Martin</span>
      </section>
     </section>:null}
      

      {/* FOOTER */}
      <footer className="mt-24 text-center text-gray-500 py-10 border-t border-slate-800">
        <p>✨ Moteur de recherche littéraire — Projet DAAR © 2025</p>
        <p className="text-sm mt-2">
          Développé par Aksil Sadi - Massin Sadi — M2 STL Sorbonne Université
        </p>
        
      </footer>
      
    </div>
  );
};

export default App
