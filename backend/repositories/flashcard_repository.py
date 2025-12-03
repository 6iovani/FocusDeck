class FlashcardRepository:
    def __init__(self, firebase_client):
        self.db = firebase_client.db

    # FLASHCARD SETS
    def save_flashcards(self, uid, set_title, cards):
        user_ref = self.db.collection("users").document(uid)
        sets_ref = user_ref.collection("flashcard_sets")
        doc = sets_ref.document()
        doc.set({"title": set_title, "cards": cards})

    def get_flashcards(self, uid):
        user_ref = self.db.collection("users").document(uid)
        sets_ref = user_ref.collection("flashcard_sets")
        docs = sets_ref.stream()
        result = []
        for d in docs:
            data = d.to_dict()
            result.append({"id": d.id, "title": data.get("title", "Untitled Set"), "cards": data.get("cards", [])})
        return result

    def delete_flashcard_set(self, uid, set_id):
        doc_ref = self.db.collection("users").document(uid).collection("flashcard_sets").document(set_id)
        doc_ref.delete()

    # STUDY GUIDES
    def save_study_guide(self, uid, title, content):
        user_ref = self.db.collection("users").document(uid)
        guides_ref = user_ref.collection("study_guides")
        doc = guides_ref.document()
        doc.set({"title": title, "content": content})

    def get_study_guides(self, uid):
        user_ref = self.db.collection("users").document(uid)
        guides_ref = user_ref.collection("study_guides")
        docs = guides_ref.stream()
        guides = []
        for d in docs:
            data = d.to_dict()
            guides.append({"id": d.id, "title": data.get("title", "Untitled Guide"), "content": data.get("content", "")})
        return guides

    def delete_study_guide(self, uid, guide_id):
        doc_ref = self.db.collection("users").document(uid).collection("study_guides").document(guide_id)
        doc_ref.delete()