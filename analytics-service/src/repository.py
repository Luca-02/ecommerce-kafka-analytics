import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import ArrayUnion, Increment

from shared.logger import get_logger


class FirebaseRepository:
    def __init__(
        self,
        google_application_credentials: str = None,
    ):
        self._logger = get_logger(component='repository')
        self.google_application_credentials = google_application_credentials
        self._app = None
        self._db = None

    def __enter__(self):
        self._initialize_firebase_firestore()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    def _initialize_firebase_firestore(self) -> bool:
        try:
            self._logger.info("Initializing Firebase Firestore connection...")
            cred = credentials.Certificate(self.google_application_credentials)
            self._app = firebase_admin.initialize_app(cred)
            self._logger.info("Firebase initialized successfully.")
            self._db = firestore.client()
            self._logger.info("Firebase Firestore connection initialized successfully.")
        except Exception as e:
            self._logger.error(f"Error initializing Firebase: {e}")

    def _close(self):
        self._logger.info("Closing Firebase connection...")
        self._db.close()
        firebase_admin.delete_app(self._app)
        self._logger.info("Firebase connection closed successfully.")

    def set_document(self, collection_name: str, document_id: str, data: dict):
        """
        Adds a document to the specified collection with the given document ID and data.

        :param collection_name: Collection name.
        :param document_id: Document ID.
        :param data: Document data.
        """
        try:
            doc_ref = self._db.collection(collection_name).document(document_id)
            doc_ref.set(data, merge=True)
            self._logger.info(f"Document {document_id} set to collection {collection_name}")
        except Exception as e:
            self._logger.error(f"Error setting document to Firebase: {e}")

    def increment_field(self, collection_name: str, document_id: str, field: str, value: int = 1):
        """
        Increments a numeric field in a Firestore document.
        If the document or field does not exist, it creates them.

        :param collection_name: Collection name.
        :param document_id: Document ID.
        :param field: Field name.
        :param value: Increment value.
        """
        try:
            doc_ref = self._db.collection(collection_name).document(document_id)
            doc_ref.set({field: Increment(value)}, merge=True)
            self._logger.info(
                f"Incremented field '{field}' in document '{document_id}' of collection '{collection_name}' by {value}"
            )
        except Exception as e:
            self._logger.error(f"Error incrementing field in Firebase: {e}")

    def increment_fields(self, collection_name: str, document_id: str, fields: list[tuple[str, int]]):
        """
        Increments a numeric field in a Firestore document.
        If the document or field does not exist, it creates them.

        :param collection_name: Collection name.
        :param document_id: Document ID.
        :param fields: List of tuples (field name, increment value).
        """
        try:
            doc_ref = self._db.collection(collection_name).document(document_id)
            increment_dict = {field: Increment(value) for field, value in fields}
            doc_ref.set(increment_dict, merge=True)
            self._logger.info(
                f"Incremented fields {list(increment_dict.keys())} in document '{document_id}' "
                f"of collection '{collection_name}' by {list(increment_dict.values())}"
            )
        except Exception as e:
            self._logger.error(f"Error incrementing fields in Firebase: {e}")

    def array_union(self, collection_name: str, document_id: str, field: str, value: list):
        try:
            doc_ref = self._db.collection(collection_name).document(document_id)
            doc_ref.set({field: ArrayUnion(value)}, merge=True)
            self._logger.info(
                f"Array union '{field}' in document '{document_id}' of collection '{collection_name}' by {value}"
            )
        except Exception as e:
            self._logger.error(f"Error array union in Firebase: {e}")
