import type { Book } from '../types';
import './book.css'
type BookCardProps = {
  livre: Book;
   onClick: () => void;
};
function BookCard({livre,onClick}: BookCardProps) {
    
     return(
  <div onClick={onClick} key={livre.gutendexId} className="flex flex-col rounded-lg mr-8 px-2 py-2 basis-1/2 sm:basis-1/3 md:basis-1/4 lg:basis-1/5">
    <img
      src={`${livre.coverUrl}`}
      className="w-full h-80 object-contain rounded-lg transition-transform duration-300 hover:scale-105 cursor-pointer"
    />
    <div className="flex justify-center items-center mt-1 w-full">
        <p className="text-white text-center mt-1 text-sm">{livre.titre}</p>
    </div>
  </div>
);
}

export default BookCard;