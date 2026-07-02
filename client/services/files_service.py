from io import BytesIO

from fastapi import UploadFile
from pypdf import PdfReader


class FilesError(Exception):
    pass


class FilesService:
    MAX_FILES = 5
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024
    MAX_EXTRACTED_CHARS_PER_FILE = 12_000

    async def build_files_context(self, files: list[UploadFile] | None) -> str | None:
        uploaded_files = files or []

        if not uploaded_files:
            return None

        if len(uploaded_files) > self.MAX_FILES:
            raise FilesError(
                f"Nombre maximum de fichiers dépassé : {self.MAX_FILES}."
            )

        files_context_parts: list[str] = []

        for file_index, uploaded_file in enumerate(uploaded_files, start=1):
            file_bytes = await uploaded_file.read()

            if len(file_bytes) > self.MAX_FILE_SIZE_BYTES:
                raise FilesError(
                    f"Le fichier {uploaded_file.filename} est trop volumineux."
                )

            if uploaded_file.content_type != "application/pdf":
                raise FilesError(
                    f"Type de fichier non supporté : {uploaded_file.content_type}"
                )

            extracted_text = self._extract_pdf_text(file_bytes)

            if not extracted_text:
                extracted_text = "[Aucun texte extractible trouvé dans ce PDF.]"

            extracted_text = extracted_text[: self.MAX_EXTRACTED_CHARS_PER_FILE]

            files_context_parts.append(
                (
                    f"--- FICHIER {file_index} ---\n"
                    f"Nom : {uploaded_file.filename}\n"
                    f"Type : {uploaded_file.content_type}\n"
                    f"Contenu extrait :\n"
                    f"{extracted_text}\n"
                    f"--- FIN FICHIER {file_index} ---"
                )
            )

        return "\n\n".join(files_context_parts)

    def _extract_pdf_text(self, file_bytes: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(file_bytes))

            pages_text: list[str] = []

            for page in reader.pages:
                page_text = page.extract_text() or ""

                if page_text.strip():
                    pages_text.append(page_text.strip())

            return "\n\n".join(pages_text)

        except Exception as error:
            raise FilesError(
                f"Erreur lors de l'extraction du PDF : {type(error).__name__}: {error}"
            ) from error