
import type { Book } from '../types';
import { useEffect,useState } from 'react';
import BookCard from './BookCard';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faDownload } from '@fortawesome/free-solid-svg-icons'
function BookDetails({clicked}:{clicked:Book}) {
  const [recommendations, setRecommendations] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [clickedOne, setClickedOne] = useState<Book | null>(null);

  //recuperer recommendation de livre similaire
  useEffect(() => {
    const fetchSimilarBooks = async () => {
      setLoading(true);
      try {
        const response = await fetch(`http://127.0.0.1:8000/livres/${clicked.gutendexId}/recommendations`);
        const data = await response.json();
        setRecommendations(data.recommendations);
        console.log("Livres similaires :", data);
      } catch (error) {
        console.error("Erreur lors de la récupération des livres similaires :", error);
      }finally {
        setLoading(false);
      }
    };

    fetchSimilarBooks();
  }, [clicked.gutendexId]);

  const handleDetailClick = (book:Book) => {
    setClickedOne(book);
  }

  return (
    <div>
    <div className="w-full flex flex-col relative h-[400px] rounded-lg overflow-hidden mt-8">
            <img
                src={`${clicked.coverUrl}`}
                className="w-full h-full object-cover"
            />
  
  {/* Overlay flou pour le texte */}
  <div className="absolute bottom-0 left-0 w-full h-full bg-black/40 backdrop-blur-[2px] text-white p-4">

   <div className='flex w-full h-full'>
    <div className='w-1/2 pl-10'>
     <h2 className="text-2xl font-bold">{clicked.titre}</h2>
     <div className='flex mt-2'>
        <p className='text-[9px] text-gray-400'>livre</p>
     </div>
     <div className='flex mt-2'>
            <p className='text-[9px] text-gray-400'>Date de sortie:</p>
            <p className='text-[9px] text-gray-400 ml-1'>{clicked.dateAjout}</p>
            </div>
     <div className='flex mt-2 items-center'>
        <FontAwesomeIcon icon={faDownload} className="text-lg w-5 text-green-500" />
        <div className="flex pl-1">
            <li className="list-none text-white text-[16px]">
                {clicked.downloadCount}
            </li>
       </div>
     </div>
    </div>
    <img
      src={`${clicked.coverUrl}`}
      className="w-56 h-80 object-cover rounded-lg ml-40"
    />

   </div>

  </div>
   
</div>


    <div>
      {clickedOne?
            <BookDetails clicked={clickedOne} />:
    <div className="w-full flex flex-col mt-8">
    <p className='text-white font-bold text-2xl'>Recommendation</p>
    <div className='flex mt-4 flex-wrap'>
        {loading? (
                <div className="flex justify-center items-center h-40"> 
                    <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
            ):
            (
            <div className="mt-16 flex flex-wrap justify-center gap-6 px-6 py-4">
             {recommendations.map((book, index) => {  
               if (book.gutendexId !== clicked.gutendexId) {
                return (
                      <BookCard
                        livre={book}
                        onClick={() => handleDetailClick(book)}
                       />
                      );
               }
               })}
              </div>
              )
                }
    </div>
    </div>
            }
    </div>
    </div>
  );
}

export default BookDetails;