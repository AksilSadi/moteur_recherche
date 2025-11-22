import type { Book } from "../types";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faDownload, faLink } from "@fortawesome/free-solid-svg-icons";

function BookDetails({ clicked }: { clicked: Book }) {
  return (
    <div className="w-full mt-8 text-white px-4 sm:px-6 lg:px-10">

      {/* SECTION IMAGE + INFOS */}
      <div className="relative rounded-xl overflow-hidden shadow-xl max-w-6xl mx-auto">

        {/* Background blur */}
        <img
          src={clicked.coverUrl}
          alt={clicked.titre}
          className="absolute inset-0 w-full h-full object-cover blur-md opacity-50"
        />

        {/* Content */}
        <div
          className="
            relative z-10 
            flex flex-col lg:flex-row 
            items-center lg:items-start 
            gap-10 
            p-6 sm:p-10
          "
        >
          {/* TEXT SECTION */}
          <div className="w-full lg:w-1/2 space-y-4">

            <h2 className="text-3xl sm:text-4xl font-extrabold drop-shadow-xl text-center lg:text-left">
              {clicked.titre}
            </h2>

            <p className="text-lg text-gray-300">
              <span className="font-semibold">Auteur : </span>
              {clicked.auteur}
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
              <FontAwesomeIcon
                icon={faDownload}
                className="text-green-400 text-xl mr-2"
              />
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

          {/* COVER IMAGE */}
          <div className="w-full lg:w-1/2 flex justify-center">
            <img
              src={clicked.coverUrl}
              alt={clicked.titre}
              className="
                w-48 h-72 
                sm:w-56 sm:h-80 
                lg:w-64 lg:h-96 
                rounded-lg shadow-xl 
                object-cover border border-white/30
              "
            />
          </div>
        </div>
      </div>

      {/* SECTION THEMES / SHELVES */}
      <div className="mt-10 max-w-6xl mx-auto">

        {/* THEMES */}
        {clicked.subjects && clicked.subjects.length > 0 && (
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-2">Thèmes</h3>
            <div className="flex flex-wrap gap-2">
              {clicked.subjects.map((sub, i) => (
                <span
                  key={i}
                  className="bg-gray-800 px-3 py-1 rounded-full text-sm input"
                >
                  {sub}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* CATEGORIES */}
        {clicked.bookshelves && clicked.bookshelves.length > 0 && (
          <div className="mb-6">
            <h3 className="text-xl font-semibold mb-2">Catégories</h3>
            <div className="flex flex-wrap gap-2">
              {clicked.bookshelves.map((shelf, i) => (
                <span
                  key={i}
                  className="bg-gray-800 px-3 py-1 rounded-full text-sm input"
                >
                  {shelf}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

    </div>
  );
}

export default BookDetails;
