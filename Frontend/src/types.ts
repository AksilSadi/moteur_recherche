type Book = {
    gutendexId: string;
    titre: string;
    auteur: string;
    chemin: string;
    coverUrl: string;
    nombreMots: number;
    downloadCount: number;
    dateAjout: string;
    birthYear?: number | null;
    deathYear?: number | null;
    subjects?: string[];
    languages?: string[];
    rights?: string | null;
    bookshelves?: string[];
    mediaType?: string | null;
    gutenbergUrl?: string;
    similarite?: number ,
    scoreGlobal?: number,
    top3?: Book[]
};

export type { Book };
