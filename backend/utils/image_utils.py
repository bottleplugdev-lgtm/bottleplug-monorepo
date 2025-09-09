import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image
import uuid


def generate_unique_filename(original_filename, folder_path):
    """
    Generate a unique filename for uploaded images
    """
    # Get file extension
    ext = os.path.splitext(original_filename)[1]
    # Generate unique filename
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    # Return full path
    return os.path.join(folder_path, unique_filename)


def save_image_from_url(image_url, folder_path, filename=None):
    """
    Download and save an image from URL to the specified folder
    """
    import requests
    from django.core.files.base import ContentFile
    
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        if not filename:
            # Extract filename from URL or generate one
            filename = os.path.basename(image_url) or f"{uuid.uuid4().hex}.jpg"
        
        # Generate unique filename
        unique_filename = generate_unique_filename(filename, folder_path)
        
        # Save the image
        file_path = default_storage.save(unique_filename, ContentFile(response.content))
        return file_path
        
    except Exception as e:
        print(f"Error saving image from URL {image_url}: {e}")
        return None


def resize_image(image_path, max_width=800, max_height=600, quality=85):
    """
    Resize an image to fit within specified dimensions
    """
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Calculate new dimensions
            width, height = img.size
            if width > max_width or height > max_height:
                ratio = min(max_width / width, max_height / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save the resized image
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            return True
            
    except Exception as e:
        print(f"Error resizing image {image_path}: {e}")
        return False


def validate_image_file(file):
    """
    Validate uploaded image file
    """
    try:
        # Check file size (max 5MB)
        if file.size > 5 * 1024 * 1024:
            return False, "File size too large. Maximum size is 5MB."
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if file.content_type not in allowed_types:
            return False, "Invalid file type. Allowed types: JPEG, PNG, GIF, WebP."
        
        # Try to open with PIL to validate it's actually an image
        with Image.open(file) as img:
            img.verify()
        
        return True, "Valid image file"
        
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def get_image_url(image_field):
    """
    Get the URL for an image field
    """
    if image_field and hasattr(image_field, 'url'):
        return image_field.url
    return None 