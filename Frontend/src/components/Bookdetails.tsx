import type { Book } from '../types';
import { useEffect, useState } from 'react';
import BookCard from './BookCard';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDownload, faLink } from '@fortawesome/free-solid-svg-icons';

function BookDetails({ clicked }: { clicked: Book }) {
  const [recommendations, setRecommendations] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [clickedOne, setClickedOne] = useState<Book | null>(null);

  // Charger recommandations
  useEffect(() => {
    const fetchSimilarBooks = async () => {
      setLoading(true);
      try {
        const response = await fetch(
          `http://127.0.0.1:8000/livres/${clicked.gutendexId}/recommendations`
        );
        const data = await response.json();
        setRecommendations(data.recommendations);
      } catch (error) {
        console.error("Erreur de récupération des recommandations :", error);
      } finally {
        setLoading(false);
      }
    };

    fetchSimilarBooks();
  }, [clicked.gutendexId]);

  const handleDetailClick = (book: Book) => {
    setClickedOne(book);
  };

  if (clickedOne) {
    return <BookDetails clicked={clickedOne} />;
  }

  return (
    <div className="w-full mt-10 text-white">

      <div className="relative h-[450px] rounded-xl overflow-hidden shadow-xl">

        <img
          src={clicked.coverUrl}
          alt={clicked.titre}
          className="absolute inset-0 w-full h-full object-cover blur-md opacity-60"
        />

        <div className="relative z-10 flex h-full p-12">

          <div className="w-1/2 space-y-4">
            <h2 className="text-4xl font-extrabold drop-shadow-xl">
              {clicked.titre}
            </h2>

            <p className="text-lg text-gray-300">
              <span className="font-semibold">Auteur : </span>{clicked.auteur}
            </p>

            {(clicked.birthYear || clicked.deathYear) && (
              <p className="text-md text-gray-300">
                <span className="font-semibold">Période : </span>
                {clicked.birthYear ?? "?"} - {clicked.deathYear ?? "?"}
              </p>
            )}

            <p className="text-md text-gray-300">
              <span className="font-semibold">Langues : </span>
              {clicked.languages?.join(", ") || "En"}
            </p>


            <div className="flex items-center text-md mt-3">
              <FontAwesomeIcon icon={faDownload} className="text-green-400 text-xl mr-2" />
              <p>{clicked.downloadCount} téléchargements</p>
            </div>

            {clicked.gutenbergUrl && (
              <a
                href={clicked.gutenbergUrl}
                target="_blank"
                className="inline-flex items-center mt-3 text-blue-400 hover:text-blue-300 transition"
              >
                <FontAwesomeIcon icon={faLink} className="mr-2" />
                Voir la page Gutenberg
              </a>
            )}
          </div>

          <div className="w-1/2 flex justify-center">
            <img
              src={clicked.coverUrl}
              alt={clicked.titre}
              className="w-60 h-80 rounded-lg shadow-xl object-cover border border-white/30"
            />
          </div>
        </div>
      </div>

      <div className="mt-10 px-10">

        {clicked.subjects && clicked.subjects.length > 0 && (
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-2">Thèmes</h3>
            <div className="flex flex-wrap gap-2">
              {clicked.subjects.map((sub, i) => (
                <span key={i} className="bg-gray-800 px-3 py-1 rounded-full text-sm input">
                  {sub}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Bookshelves */}
        {clicked.bookshelves && clicked.bookshelves.length > 0 && (
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-2">Catégories</h3>
            <div className="flex flex-wrap gap-2">
              {clicked.bookshelves.map((shelf, i) => (
                <span key={i} className="bg-gray-800 px-3 py-1 rounded-full text-sm input">
                  {shelf}
                </span>
              ))}
            </div>
          </div>
        )}

      </div>

      <div className="mt-10 px-10">
        <h3 className="text-white font-bold text-2xl mb-4">Recommandations</h3>

        {loading ? (
          <div className="flex justify-center items-center h-40">
            <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="flex flex-wrap justify-center gap-6">
            {recommendations?.length > 0 ? (
              recommendations?.map((book) =>
                book.gutendexId !== clicked.gutendexId ? (
                  <BookCard
                    key={book.gutendexId}
                    livre={book}
                    onClick={() => handleDetailClick(book)}
                  />
                ) : null
              )
            ) : (
              <p className="text-gray-300">Aucune recommandation trouvée.</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default BookDetails;
