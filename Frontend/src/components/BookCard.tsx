import type { Book } from '../types';
import './book.css';

type BookCardProps = {
  livre: Book;
  onClick: () => void;
};

function BookCard({ livre, onClick }: BookCardProps) {
  return (
    <div
      onClick={onClick}
      key={livre.gutendexId}
      className="
        flex flex-col 
        rounded-lg 
        px-2 py-2 
        cursor-pointer
        basis-1/2           
        sm:basis-1/3        
        md:basis-1/4       
        lg:basis-1/5        
        xl:basis-1/6        
      "
    >
      <img
        src={livre.coverUrl}
        className="
          w-full 
          h-56 sm:h-64 md:h-72 lg:h-80 
          object-contain 
          rounded-lg
          transition-transform duration-300 
          hover:scale-105 
        "
      />

      <div className="flex justify-center items-center mt-2 w-full">
        <p className="text-white text-center text-xs sm:text-sm line-clamp-2 px-1">
          {livre.titre}
        </p>
      </div>
    </div>
  );
}

export default BookCard;
