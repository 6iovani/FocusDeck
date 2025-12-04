class FlashcardRepository:
    """
    All functions for storing, loading, and deleting flashcards and study guides in Firestore per user.
    Each user has their own Firestore document, with subcollections for their card sets and guides.
    """
    def __init__(self, firebase_client):
        # Attach Firestore handle from shared Firebase connection
        self.db = firebase_client.db

    def save_flashcards(self, uid, set_title, cards):
        """
        Create and save a new flashcard set for user `uid`. Each set is a document with unique ID under the user's flashcard_sets subcollection.
        The set document contains a title and the full flashcards list.
        """
        user_ref = self.db.collection("users").document(uid)
        sets_ref = user_ref.collection("flashcard_sets")
        doc = sets_ref.document()
        doc.set({"title": set_title, "cards": cards})

    def get_flashcards(self, uid):
        """
        each set of flashcards includes a document ID, title, and the list of cards.
        """
        user_ref = self.db.collection("users").document(uid)
        sets_ref = user_ref.collection("flashcard_sets")
        docs = sets_ref.stream()
        result = []
        for d in docs:
            data = d.to_dict()
            result.append({"id": d.id, "title": data.get("title", "Untitled Set"), "cards": data.get("cards", [])})
        return result

    def delete_flashcard_set(self, uid, set_id):
        """
        delete a specific flashcard set for the user by its id.
        """
        doc_ref = self.db.collection("users").document(uid).collection("flashcard_sets").document(set_id)
        doc_ref.delete()

    def save_study_guide(self, uid, title, content):
        """
        save a study guide each one is a seperate document in their study_guides subcollection
        """
        user_ref = self.db.collection("users").document(uid)
        guides_ref = user_ref.collection("study_guides")
        doc = guides_ref.document()
        doc.set({"title": title, "content": content})

    def get_study_guides(self, uid):
        """
        load study guides for user, each guide has an id, title, and content
        """
        user_ref = self.db.collection("users").document(uid)
        guides_ref = user_ref.collection("study_guides")
        docs = guides_ref.stream()
        guides = []
        for d in docs:
            data = d.to_dict()
            guides.append({"id": d.id, "title": data.get("title", "Untitled Guide"), "content": data.get("content", "")})
        return guides

    def delete_study_guide(self, uid, guide_id):
        """
        delete a study guide by its id for the user
        """
        doc_ref = self.db.collection("users").document(uid).collection("study_guides").document(guide_id)
        doc_ref.delete()