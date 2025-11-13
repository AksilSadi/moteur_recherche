import { useState } from 'react'
import './App.css'
import { motion } from 'framer-motion'
import { Search } from 'lucide-react'

function App() {
  const [query, setQuery] = useState("");
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  

  return (
    <div className="min-h-screen bg-gray-700 from-slate-900 via-slate-950 to-black text-white">
      {/* HERO SECTION */}
      <section className="relative text-center py-24 px-6 overflow-hidden">
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
          Recherchez parmi des milliers d’œuvres, découvrez les classiques, et laissez-vous guider par la science des graphes.
        </motion.p>

        {/* Barre de recherche */}
        <form  className="relative max-w-xl mx-auto">
          <Search className="absolute left-3 top-3 text-gray-400" size={22} />
          <input
            type="text"
            placeholder="Rechercher un livre, un auteur, un mot-clé..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-3 rounded-full bg-slate-800 border border-slate-700 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
          />
        </form>

        {/* Effet décoratif */}
        <div className="absolute top-0 left-0 w-full h-full bg-[url('/pattern.svg')] opacity-5 bg-cover" />
      </section>

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

      {/* RESULTATS DE RECHERCHE */}
      {loading && (
        <div className="text-center text-gray-400 mt-10 animate-pulse">Recherche en cours...</div>
      )}

      {!loading && books.length > 0 && (
        <section className="mt-14 px-6">
          <h2 className="text-2xl font-semibold mb-6">
            🔍 Résultats pour “{query}”
          </h2>
         
        </section>
      )}

      {/* LIVRES POPULAIRES */}
      {!loading && books.length === 0 && (
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

      {/* FOOTER */}
      <footer className="mt-24 text-center text-gray-500 py-10 border-t border-slate-800">
        <p>✨ Moteur de recherche littéraire — Projet DAAR © 2025</p>
        <p className="text-sm mt-2">
          Développé par Aksil Sadi - Massin Sadi — M2 STL Sorbonne Université
        </p>
      </footer>

      {/* MODALE DÉTAILS */}
      
    </div>
  );
};

export default App
