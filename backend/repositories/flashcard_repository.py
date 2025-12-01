class FlashcardRepository:
    def __init__(self, firebase_client):
        self.db = firebase_client.get_firestore()

    def save_flashcards(self, user_id, cards):
        col = self.db.collection("users").document(user_id).collection("flashcards")
        for card in cards:
            col.add(card)

    def get_flashcards(self, user_id):
        col = self.db.collection("users").document(user_id).collection("flashcards")
        docs = col.stream()
        return [{"id": d.id, **d.to_dict()} for d in docs]

    def delete_flashcard(self, user_id, card_id):
        doc_ref = self.db.collection("users").document(user_id) \
            .collection("flashcards").document(card_id)
        doc_ref.delete()