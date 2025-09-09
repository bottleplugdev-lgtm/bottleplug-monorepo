# Image Asset Migration Summary

## Overview
This document summarizes the changes made to convert the project from using URL fields for images to requiring actual image assets with proper file storage.

## Changes Made

### 1. Model Changes

#### Products App
- **Product model**: Changed `image` field from `URLField` to `ImageField(upload_to='products/')`
- **Category model**: Changed `image` field from `URLField` to `ImageField(upload_to='categories/')`
- **ProductImage model**: Changed `image_url` field to `image` field as `ImageField(upload_to='product_images/')`

#### Users App
- **User model**: Changed `profile_image` field from `URLField` to `ImageField(upload_to='profile_images/')`

#### Events App
- **Event model**: Already using `ImageField(upload_to='events/')` - no changes needed

### 2. Serializer Updates
- **ProductImageSerializer**: Updated to use `image` field instead of `image_url`
- **User serializers**: Already included `profile_image` field - no changes needed

### 3. View Updates
- **ProductViewSet**: Added `upload_image` action for handling image uploads
- **CategoryViewSet**: Added `upload_image` action for handling image uploads
- **UserViewSet**: Added `upload_profile_image` action for handling profile image uploads
- All viewsets now include `MultiPartParser` and `FormParser` for file uploads

### 4. Firebase Authentication Updates
- **UserViewSet**: Removed automatic profile image assignment from Firebase tokens
- Firebase picture URLs are no longer automatically assigned to profile_image field
- Users will need to upload profile images separately

### 5. New Utility Functions
Created `utils/image_utils.py` with the following functions:
- `generate_unique_filename()`: Generate unique filenames for uploaded images
- `save_image_from_url()`: Download and save images from URLs
- `resize_image()`: Resize images to specified dimensions
- `validate_image_file()`: Validate uploaded image files
- `get_image_url()`: Get URL for image fields

### 6. Media Configuration
- **Settings**: Media configuration already properly set up
- **URLs**: Media serving already configured for development
- **Directories**: Created media subdirectories:
  - `media/products/`
  - `media/categories/`
  - `media/product_images/`
  - `media/profile_images/`
  - `media/events/`

### 7. Dependencies
- **Pillow**: Already included for image processing
- **Requests**: Added for downloading images from URLs

## API Endpoints

### New Image Upload Endpoints

#### Products
- `POST /api/v1/products/{id}/upload_image/`
  - Uploads an image for a specific product
  - Requires multipart form data with 'image' field

#### Categories
- `POST /api/v1/products/categories/{id}/upload_image/`
  - Uploads an image for a specific category
  - Requires multipart form data with 'image' field

#### Users
- `POST /api/v1/auth/users/{id}/upload_profile_image/`
  - Uploads a profile image for a specific user
  - Requires multipart form data with 'image' field

## Image Validation

### File Size Limit
- Maximum file size: 5MB

### Allowed File Types
- JPEG/JPG
- PNG
- GIF
- WebP

### Image Processing
- Images are automatically resized to max 800x600 pixels
- Quality is optimized to 85%
- Images are converted to JPEG format for consistency

## Migration Notes

### Database Migration
- All image fields are now nullable to avoid migration issues
- Existing data with URL values will need to be handled separately
- New uploads will store actual image files

### Backward Compatibility
- API responses still include image URLs
- Frontend applications will need to be updated to handle file uploads
- Existing URL-based images will need to be migrated to file uploads

## Usage Examples

### Upload Product Image
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "image=@product_image.jpg" \
  http://localhost:8000/api/v1/products/1/upload_image/
```

### Upload Category Image
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "image=@category_image.jpg" \
  http://localhost:8000/api/v1/products/categories/1/upload_image/
```

### Upload Profile Image
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "image=@profile_image.jpg" \
  http://localhost:8000/api/v1/auth/users/1/upload_profile_image/
```

## Next Steps

1. **Frontend Updates**: Update frontend applications to use file uploads instead of URL inputs
2. **Data Migration**: Migrate existing URL-based images to file uploads
3. **Testing**: Test all image upload endpoints thoroughly
4. **Documentation**: Update API documentation to reflect new image requirements
5. **Performance**: Monitor image storage and processing performance 