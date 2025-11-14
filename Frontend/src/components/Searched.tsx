import { useState,useEffect } from 'react';
import type { Book } from '../types';
import BookCard from './BookCard';
function Searched({term}:{term:string}) {
    const [searchResults, setSearchResults] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleDetailClick = (bookId: string) => {
        // Gérer l'affichage des détails du livre
    };

    useEffect(() => {
        if (term.length === 0) {
          setSearchResults([]);
          return;
        }
    
        const fetchBooks = async () => {
          setLoading(true);
          try {
            const response = await fetch(`http://127.0.0.1:8000/livres/search?q=${encodeURIComponent(term)}&type=keyword`);
            const data = await response.json();
            setSearchResults(data.resultats);
          } catch (error) {
            console.error("Erreur lors de la récupération des livres :", error);
          } finally {
            setLoading(false);
          }
        };
    
        const delayDebounceFn = setTimeout(() => {
          fetchBooks();
        }, 500);
        return () => clearTimeout(delayDebounceFn);
      }, [term]);

    return (
        <div className="w-full px-5 py-5">
            <p className="text-white text-xl mb-4">Résultats de recherche pour "{term}":</p>
            {loading ? (
                <div className="flex justify-center items-center h-40">
                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
            ) : searchResults?.length === 0 ? (
                <p className="text-white">Aucun résultat trouvé.</p>
            ) : (
                <ul className="grid grid-cols-4 gap-4">
                    {searchResults?.map((book: Book) => (
                        <BookCard
                         key={book.gutendexId}
                         livre={book}
                         onClick={() => { handleDetailClick(book.gutendexId) }}
                        />
                    ))}
                </ul>
            )}
            
        </div>
    );
}

export default Searched;