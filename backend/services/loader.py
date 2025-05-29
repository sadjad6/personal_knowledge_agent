import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import frontmatter
from unstructured.partition.auto import partition
from datetime import datetime
import hashlib
import json

from ...config import settings

logger = logging.getLogger(__name__)

class Document:
    """A class to represent a document with metadata and content."""
    
    def __init__(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        source_path: Optional[Path] = None,
    ):
        self.content = content
        self.metadata = metadata or {}
        self.source_path = source_path
        
        # Add source file info to metadata if available
        if source_path:
            self.metadata.update({
                "source": str(source_path.relative_to(settings.NOTES_DIR)),
                "file_name": source_path.name,
                "file_type": source_path.suffix.lower(),
                "last_modified": datetime.fromtimestamp(source_path.stat().st_mtime).isoformat(),
            })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary for storage."""
        return {
            "content": self.content,
            "metadata": self.metadata,
            "source_path": str(self.source_path) if self.source_path else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create a Document from a dictionary."""
        source_path = Path(data["source_path"]) if data.get("source_path") else None
        return cls(
            content=data["content"],
            metadata=data.get("metadata", {}),
            source_path=source_path,
        )
    
    @property
    def doc_id(self) -> str:
        """Generate a unique ID for the document based on its content and metadata."""
        doc_str = f"{self.content}{json.dumps(self.metadata, sort_keys=True)}"
        return hashlib.sha256(doc_str.encode()).hexdigest()


def load_document(file_path: Path) -> Optional[Document]:
    """
    Load a single document from a file.
    
    Args:
        file_path: Path to the document file
        
    Returns:
        Document object or None if the file could not be loaded
    """
    try:
        # Skip hidden files and directories
        if file_path.name.startswith('.'):
            return None
            
        # Parse the file based on its extension
        if file_path.suffix.lower() == '.md':
            return _load_markdown(file_path)
        else:
            # Use unstructured for other file types
            return _load_with_unstructured(file_path)
            
    except Exception as e:
        logger.error(f"Error loading document {file_path}: {str(e)}", exc_info=True)
        return None

def _load_markdown(file_path: Path) -> Optional[Document]:
    """Load a markdown file, extracting frontmatter if present."""
    try:
        # Parse the markdown file with frontmatter
        post = frontmatter.load(file_path)
        
        # Extract content and metadata
        content = post.content.strip()
        metadata = dict(post.metadata)
        
        return Document(content=content, metadata=metadata, source_path=file_path)
    except Exception as e:
        logger.error(f"Error parsing markdown file {file_path}: {str(e)}")
        return None

def _load_with_unstructured(file_path: Path) -> Optional[Document]:
    """Load a document using unstructured library."""
    try:
        elements = partition(filename=str(file_path))
        content = "\n\n".join([str(el) for el in elements])
        
        # Extract basic metadata
        metadata = {
            "title": file_path.stem,
            "content_type": elements[0].metadata.filetype if elements else "unknown",
        }
        
        return Document(content=content, metadata=metadata, source_path=file_path)
    except Exception as e:
        logger.error(f"Error processing {file_path} with unstructured: {str(e)}")
        return None

def load_documents(directory: Path) -> List[Document]:
    """
    Load all documents from a directory recursively.
    
    Args:
        directory: Directory to search for documents
        
    Returns:
        List of Document objects
    """
    documents = []
    
    # Ensure the directory exists
    if not directory.exists():
        logger.warning(f"Directory {directory} does not exist")
        return documents
    
    # Define supported file extensions
    supported_extensions = {'.md', '.txt', '.mdx', '.markdown', '.csv', '.docx', '.pptx', '.pdf'}
    
    # Walk through the directory
    for file_path in directory.rglob('*'):
        if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
            doc = load_document(file_path)
            if doc:
                documents.append(doc)
    
    logger.info(f"Loaded {len(documents)} documents from {directory}")
    return documents
