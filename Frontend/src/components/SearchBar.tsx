import { useEffect,useState } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons'
function SearchBar({search}:{search:(query:string)=>void}) {
    const [searchTerm, setSearchTerm] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (searchTerm.trim() !== '') {
            search(searchTerm);
        }
        setSearchTerm('');
    };

  return (
    <div className=' h-8 flex items-center justify-center px-5 py-5 search w-full'>
                    <form onSubmit={handleSubmit} className='search h-8 flex items-center bg-gray-600 px-6 py-5 w-[480px]'>
                      <input 
                        type='search' 
                        placeholder="Rechercher un livre par mot-clé"
                        className='text-white w-[400px] bg-transparent outline-none' 
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                      <button type="submit" className=' text-black ml-2'>
                        <FontAwesomeIcon icon={faMagnifyingGlass} />
                      </button>
                    </form>
                    </div>
  );
}

export default SearchBar;